"""BLE client for Luxaflex Gen 3 communication."""

import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection
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
        try:
            self.client = await establish_connection(
                BleakClient, self.mac_address, self.mac_address, timeout=timeout
            )
            self._connected = True
            _LOGGER.info("Connected to Luxaflex shade %s", self.mac_address)
            return True
        except (BleakError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to connect to %s: %s", self.mac_address, str(err))
            self._connected = False
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

    def _encrypt_command(self, command: int, position: int = 0) -> bytes:
        """Encrypt command using AES-ECB."""
        if not self.encryption_key:
            # No encryption key, return unencrypted command
            return bytes([command, position])

        # Convert hex key to bytes
        key_bytes = bytes.fromhex(self.encryption_key)
        
        # Create command frame (16 bytes)
        frame = bytearray(16)
        frame[0] = command
        frame[1] = position
        
        # Encrypt using AES-ECB
        cipher = Cipher(algorithms.AES(key_bytes), modes.ECB())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(bytes(frame)) + encryptor.finalize()
        
        return encrypted

    async def send_command(self, command: int, position: int = 0) -> bool:
        """Send a command to the shade."""
        if not self.is_connected():
            _LOGGER.error("Not connected to shade")
            return False

        try:
            encrypted_command = self._encrypt_command(command, position)
            
            # Write to characteristic
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, encrypted_command)
            _LOGGER.debug("Sent command %d with position %d to %s", command, position, self.mac_address)
            return True
        except (BleakError, AttributeError) as err:
            _LOGGER.error("Failed to send command to %s: %s", self.mac_address, str(err))
            return False

    async def open(self) -> bool:
        """Open the shade."""
        return await self.send_command(COMMAND_OPEN)

    async def close(self) -> bool:
        """Close the shade."""
        return await self.send_command(COMMAND_CLOSE)

    async def stop(self) -> bool:
        """Stop the shade."""
        return await self.send_command(COMMAND_STOP)

    async def set_position(self, position: int) -> bool:
        """Set shade position (0-100)."""
        if not 0 <= position <= 100:
            _LOGGER.error("Position must be between 0 and 100")
            return False
        return await self.send_command(COMMAND_POSITION, position)

    async def set_tilt(self, tilt: int) -> bool:
        """Set shade tilt (0-100)."""
        if not 0 <= tilt <= 100:
            _LOGGER.error("Tilt must be between 0 and 100")
            return False
        return await self.send_command(COMMAND_TILT, tilt)
