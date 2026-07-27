"""BLE client for Luxaflex Gen 3 communication."""

import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .const import (
    CHARACTERISTIC_UUID,
    COMMAND_CLOSE,
    COMMAND_OPEN,
    COMMAND_POSITION,
    COMMAND_STOP,
    COMMAND_TILT,
    SERVICE_UUID,
)

_LOGGER = logging.getLogger(__name__)


class LuxaflexBLEClient:
    """BLE client for Luxaflex Gen 3 shades."""

    def __init__(self, mac_address: str, encryption_key: Optional[str] = None):
        """Initialize the BLE client."""
        self.mac_address = mac_address
        self.encryption_key = encryption_key
        self.client: Optional[BleakClient] = None
        self._connected = False

    async def connect(self, timeout: int = 6) -> bool:
        """Connect to the shade."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.client = BleakClient(self.mac_address, timeout=timeout)
                await self.client.connect()
                self._connected = True
                _LOGGER.info("Connected to Luxaflex shade %s", self.mac_address)
                return True
            except (BleakError, asyncio.TimeoutError) as err:
                _LOGGER.error(
                    "Failed to connect to %s (attempt %d/%d): %s",
                    self.mac_address,
                    attempt + 1,
                    max_retries,
                    str(err)
                )
                self._connected = False
                
                # If not last attempt, wait before retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        
        return False

    async def disconnect(self) -> None:
        """Disconnect from the shade."""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
            _LOGGER.info("Disconnected from %s", self.mac_address)

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected and self.client is not None and self.client.is_connected

    def _build_command(self, position: int, seq: int = 1) -> bytes:
        """Build command frame based on ajain189 implementation."""
        p = (position * 100).to_bytes(2, 'little')
        pl = p + bytes([0, 128, 0, 128, 0, 128, 0])
        h = (0x01F7).to_bytes(2, 'little') + bytes([seq, len(pl)])
        return h + pl

    def _encrypt_command(self, command: bytes) -> bytes:
        """Encrypt command using AES-CTR (ajain189 implementation)."""
        if not self.encryption_key:
            # No encryption key, return unencrypted command
            return command

        # Convert hex key to bytes
        key_bytes = bytes.fromhex(self.encryption_key)
        
        # Encrypt using AES-CTR with 16-byte counter
        # Using modes.CTR with nonce parameter
        cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce=bytes(16)))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(command) + encryptor.finalize()
        
        return encrypted

    async def send_command(self, position: int) -> bool:
        """Send a command to the shade."""
        if not self.is_connected():
            _LOGGER.error("Not connected to shade")
            return False

        try:
            command = self._build_command(position)
            encrypted_command = self._encrypt_command(command)
            
            # Write to characteristic
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, encrypted_command, response=False)
            _LOGGER.debug("Sent command with position %d to %s", position, self.mac_address)
            return True
        except (BleakError, AttributeError) as err:
            _LOGGER.error("Failed to send command to %s: %s", self.mac_address, str(err))
            return False

    async def open(self) -> bool:
        """Open the shade."""
        return await self.send_command(100)

    async def close(self) -> bool:
        """Close the shade."""
        return await self.send_command(0)

    async def stop(self) -> bool:
        """Stop the shade."""
        # For stop, we send current position (not implemented in ajain189)
        return await self.send_command(50)

    async def set_position(self, position: int) -> bool:
        """Set shade position (0-100)."""
        if not 0 <= position <= 100:
            _LOGGER.error("Position must be between 0 and 100")
            return False
        return await self.send_command(position)

    async def set_tilt(self, tilt: int) -> bool:
        """Set shade tilt (0-100)."""
        if not 0 <= tilt <= 100:
            _LOGGER.error("Tilt must be between 0 and 100")
            return False
        return await self.send_command(tilt)
