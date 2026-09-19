# FCT — ODC-REC-RPI-1A

**Fixture:** 12 V PSU (current-limited), CAN simulator or second adapter, USB serial console to Pi, CAN analyzer on the bus.

## Procedure

1. Power DUT via OBD pin 16 / VIN pad at 12.0 V. Current < 800 mA idle typical.
2. Console: confirm `can0` exists; `ip -details link show can0` shows **listen-only**.
3. Start simulator frames at 500 kbit/s; DUT `candump -n 20 can0` receives ≥ 1 frame within 5 s.
4. **TX interlock:** analyzer must show **no** frames with DUT as source for 60 s while DUT runs recorder service.
5. Write capture sample to `/home/pi/captures/`; confirm file non-empty.
6. LEDs: PWR on; ACT blinks or steady per design.
7. Record serial, image `sha256`, FCT result PASS/FAIL on traveler.

## Fail criteria

- No `can0`
- listen-only flag missing
- Any TX from DUT
- 5 V rail out of ±0.15 V @ ≥1 A load (if load fixture available)
- Fuse missing / wrong rating
