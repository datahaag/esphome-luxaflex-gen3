"""Constants for Luxaflex Gen 3 integration."""

DOMAIN = "luxaflex_gen3"

# Configuration keys
CONF_MAC_ADDRESS = "mac_address"
CONF_ENCRYPTION_KEY = "encryption_key"
CONF_BLE_TIMEOUT = "ble_timeout"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_BLE_TIMEOUT = 6
DEFAULT_SCAN_INTERVAL = 15

# BLE Service UUIDs
SERVICE_UUID = "0000fdc1-0000-1000-8000-00805f9b34fb"  # Luxaflex Gen 3 Service
CHARACTERISTIC_UUID = "CAFE1001-C0FF-EE01-8000-A110CA7AB1E0"  # Command Characteristic

# Command constants
COMMAND_OPEN = 0x01
COMMAND_CLOSE = 0x02
COMMAND_STOP = 0x03
COMMAND_POSITION = 0x04
COMMAND_TILT = 0x05

# Device types
DEVICE_TYPE_ROLLER = "roller"
DEVICE_TYPE_DUAL = "dual"
DEVICE_TYPE_TILT = "tilt"

# BLE name prefixes for auto-discovery
BLE_NAME_PREFIXES = ["DUT", "SIL"]
