# Luxaflex Gen 3 Home Assistant Integration

Home Assistant custom component voor directe aansturing van Luxaflex (Hunter Douglas) PowerView Gen 3 shades via Bluetooth Low Energy (BLE).

## Overzicht

Dit project bevat een custom Home Assistant integration die Luxaflex Gen 3 shades direct via Bluetooth kan aansturen, zonder tussenkomst van de PowerView Hub of Gateway.

## Protocol Details

### BLE Communicatie
- Elke shade heeft een uniek 16-byte "home key" voor encryptie
- Commands worden verstuurd als 16-byte frames
- Encryptie: AES-ECB
- Communicatie via GATT characteristic

### Encryptie Key
- **Shades NIET in PowerView App:** Geen encryptie key nodig
- **Shades WEL in PowerView App:** Encryptie key vereist (dezelfde als de app gebruikt)

## Component Structuur

```
custom_components/luxaflex_gen3/
├── __init__.py          # Setup entry, coordinator
├── manifest.json        # Component metadata
├── config_flow.py       # UI configuratie
├── const.py             # Constants
├── entity.py            # Base entity class
├── cover.py             # Cover entity voor shades
├── ble_client.py        # BLE communicatie laag
└── strings.json         # UI teksten
```

## Features

- ✅ BLE discovery van Luxaflex Gen 3 shades
- ✅ Cover entities met position support (0-100%)
- ✅ Tilt support voor shades met lamellen (indien beschikbaar)
- ✅ Battery level monitoring
- ✅ RSSI signal strength
- ✅ Ondersteuning voor dual-action shades (top-down/bottom-up)
- ✅ UI configuratie via config flow

## Installatie

1. Kopieer de `custom_components/luxaflex_gen3/` map naar je Home Assistant `custom_components/` directory
2. Restart Home Assistant
3. Ga naar Settings → Devices & Services → Add Integration
4. Zoek naar "Luxaflex Gen 3"
5. Volg de configuratie wizard

## Configuratie

Via de UI configuratie kun je:
- Shades automatisch laten ontdekken via BLE
- Handmatig BLE MAC adres en encryptie key opgeven
- Timeout instellingen configureren

## Gebruik

Na configuratie worden shades beschikbaar als Cover entities in Home Assistant:
- Open/sluiten shades
- Positie instellen (0-100%)
- Lamellen kantelen (indien ondersteund)
- Batterijstatus bekijken

## Referenties

- [datahaag/esphome-luxaflex-gen3](https://github.com/datahaag/esphome-luxaflex-gen3) - ESPHome BLE analyzer
- [ajain189/powerview-ble-direct-control](https://github.com/ajain189/powerview-ble-direct-control) - Python BLE control scripts
- [openHAB Bluetooth PowerView Binding](https://www.openhab.org/addons/bindings/bluetooth.hdpowerview/) - openHAB implementatie

## Status

🚧 In ontwikkeling

## License

MIT
