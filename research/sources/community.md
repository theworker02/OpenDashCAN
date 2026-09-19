# Source: Community / commercial channel lists

## Community

- Autosport Labs / enthusiast forums — speculative Civic 8 IDs `0x194`, `0x494`, `0x694`
  labeled **COMMUNITY_REPORTED** with **no encodings**.
- CivicX / other forum discussions pointing at opendbc (secondary citation only).
- Honda-Tech / Civic forums — gen7 OBD as **ISO 9141-2 K-line** (COMMUNITY_REPORTED);
  supports pre–OBD-CAN narrative, not encodings.

## Commercial datasheets (channel names only)

- **AiM** stock-ECU PDFs (e.g. Honda Civic US 2006–2011 Civic_US; Civic 2012–2015 CivicSi_2012):
  OBD pinout + Race Studio channel **names**. No arbitration IDs or bit packing.
  No AiM Civic CAN sheet for 2001–2005 gen7 is cited here.
- **Racelogic** Vehicle CAN Database PDFs (Civic 2005–2011, 2011–2015):
  OBD 500 kbps + channel **names**. Proprietary `.REF` files are not reverse-engineered
  into OpenDashCAN. The 2005–2011 window overlaps end-of-gen7 calendars — do not promote
  as proof that all US 2001–2004 Civics expose OBD-CAN.

These never promote encodings to PHYSICALLY_VERIFIED or CAPTURE_VERIFIED alone.
