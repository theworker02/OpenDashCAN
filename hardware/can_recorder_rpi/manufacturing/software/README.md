# Factory software — ODC-REC-RPI-1A

## Image recipe

1. Base: Raspberry Pi OS Lite 64-bit (current stable).
2. Enable SPI; append [`../../../boot_config_fragment.txt`](../../../boot_config_fragment.txt) to `/boot/firmware/config.txt` (or `/boot/config.txt` on older images).
3. Install `can-utils`.
4. Create user service from [`odc-recorder.service`](odc-recorder.service) + [`record_listen_only.sh`](../../../scripts/record_listen_only.sh).
5. **Remove or never install** tools used to transmit (`cansend` may exist in can-utils — block via sudoers/wrapper; prefer service-only access).
6. Default bring-up must include `listen-only on`.
7. Publish golden image; record `sha256sum` in release notes / FCT.

## First boot checklist

```bash
sudo ip link set can0 up type can bitrate 500000 listen-only on
ip -details link show can0   # must show listen-only
candump -n 5 can0            # with simulator attached
```

Desktop decode happens on a PC via OpenDashCAN — **not** on this image’s GUI (none shipped).
