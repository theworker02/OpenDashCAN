# Honda Civic Gen 7 (`honda.civic.gen7.us`)

Years ≈2001–2005 (EM2/ES/EP). Research package with **explicit negative findings**
on proprietary CAN encodings.

## Documented / community-supported

- OBD-II emissions access: **ISO 9141-2 / KWP2000 K-line** on DLC pin 7 (≈10.4 kbaud)
- Pinout catalogs list Civic mid-2000s under ISO 9141-2 / 14230-4; CAN OBD entries appear later (~2006+)
- Community (Honda-Tech): generic readers use K-line; MICU may gateway proprietary paths for HDS

## Explicit negatives

- **No** OpenDBC Civic 2001–2005 DBC in this repo
- **No** AiM Civic CAN stock-ECU sheet for 2001–2005 (AiM Civic CAN starts 2006–2011)
- **No** asserted F-CAN/B-CAN bitrates, arbitration IDs, or byte layouts
- Racelogic “Civic 2005–2011” is OBD CAN + channel names with **year overlap** — not proof for all US 2001–2004

## UNKNOWN

All taxonomy signal encodings for cluster adaptation (RPM/speed/fuel/gear/lamps on proprietary buses).

SAE J1979 OBD PIDs ≠ Honda cluster protocol. Gen7 is not the reference adaptation source
(that remains Civic gen8 R18 auto).

Protocol package: `opendashcan/protocols/honda/civic/gen7/us/`
