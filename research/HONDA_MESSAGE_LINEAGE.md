# Honda Message Lineage

_Auto-generated from public opendbc Honda/Acura DBC indexes._

Lineage is vehicle-protocol comparison from public DBC. CROSS_PLATFORM_CANDIDATE ≠ Civic definition. Matching names ≠ identical encoding.

- Message instances: **578**
- Unique CAN IDs: **67**
- IDs with identical encoding across ≥2 vehicles: **36**
- IDs with encoding divergence: **20**
- Same-name / different-ID collisions: **8**

## Stable IDs (identical encoding)

- `0x91`
- `0xe5`
- `0xe8`
- `0x130`
- `0x13c`
- `0x14a`
- `0x158`
- `0x17c`
- `0x1a4`
- `0x1ab`
- `0x1d0`
- `0x1df`
- `0x1e7`
- `0x1ea`
- `0x1ef`
- `0x200`
- `0x201`
- `0x240`
- `0x241`
- `0x243`
- `0x244`
- `0x246`
- `0x247`
- `0x249`
- `0x24a`
- `0x296`
- `0x305`
- `0x309`
- `0x30c`
- `0x324`
- `0x374`
- `0x37b`
- `0x37c`
- `0x405`
- `0x000033DA`
- `0x000033DB`

## Divergent IDs (do not assume copy-paste)

- `0x94` names=['KINEMATICS', 'KINEMATICS_ALT'] vehicles=15 variants=2
  - vs `acura.rdx.gen3.us.2020`: mismatches=2 only_a=[] only_b=[]
  - vs `honda.accord.gen10.us.2018`: mismatches=2 only_a=[] only_b=[]
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=2 only_a=[] only_b=[]
- `0xe4` names=['STEERING_CONTROL'] vehicles=12 variants=3
  - vs `acura.rdx.gen3.us.2020`: mismatches=1 only_a=[] only_b=['SET_ME_X00_2', 'STEER_DOWN_TO_ZERO']
  - vs `honda.accord.gen10.us.2018`: mismatches=1 only_a=[] only_b=['SET_ME_X00_2', 'STEER_DOWN_TO_ZERO']
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=1 only_a=[] only_b=['SET_ME_X00_2', 'STEER_DOWN_TO_ZERO']
- `0x156` names=['STEERING_SENSORS'] vehicles=8 variants=2
  - vs `honda.crv.gen5.eu.executive_2016`: mismatches=1 only_a=[] only_b=[]
  - vs `honda.fit.gen3.us.hybrid_2018`: mismatches=1 only_a=[] only_b=[]
- `0x18f` names=['STEER_STATUS'] vehicles=15 variants=3
  - vs `acura.rdx.gen2.us.2018`: mismatches=5 only_a=['STEER_CONFIG_INDEX'] only_b=[]
  - vs `honda.crv.gen5.eu.executive_2016`: mismatches=5 only_a=['STEER_ANGLE_RATE', 'STEER_CONFIG_INDEX'] only_b=['STEER_TORQUE_MOTOR']
  - vs `honda.crv.gen5.us.touring_2016`: mismatches=5 only_a=['STEER_CONFIG_INDEX'] only_b=[]
- `0x191` names=['GEARBOX', 'GEARBOX_15T'] vehicles=7 variants=4
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=0 only_a=[] only_b=[]
  - vs `honda.civic.gen10.us.hatch_ex_2017`: mismatches=0 only_a=[] only_b=[]
  - vs `honda.civic.gen10.us.touring_2016`: mismatches=1 only_a=['BOH', 'GEAR2', 'ZEROS_BOH'] only_b=[]
- `0x194` names=['STEERING_CONTROL'] vehicles=3 variants=2
  - vs `honda.crv.gen5.eu.executive_2016`: mismatches=1 only_a=[] only_b=['SET_ME_X00_2']
  - vs `honda.crv.gen5.us.touring_2016`: mismatches=1 only_a=[] only_b=['SET_ME_X00_2']
- `0x1a3` names=['GEARBOX', 'GEARBOX_ALT'] vehicles=9 variants=4
  - vs `acura.rdx.gen3.us.2020`: mismatches=1 only_a=[] only_b=[]
  - vs `honda.accord.gen10.us.2018`: mismatches=2 only_a=[] only_b=[]
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=1 only_a=[] only_b=[]
- `0x1a6` names=['SCM_BUTTONS'] vehicles=6 variants=3
  - vs `acura.rdx.gen2.us.2018`: mismatches=0 only_a=[] only_b=['PARKING_BRAKE_LIGHT']
  - vs `honda.fit.gen3.us.ex_2018`: mismatches=0 only_a=[] only_b=['DRIVERS_DOOR_OPEN']
- `0x1b0` names=['STANDSTILL'] vehicles=15 variants=4
  - vs `acura.rdx.gen3.us.2020`: mismatches=0 only_a=['CONTROLLED_STANDSTILL', 'WHEELS_MOVING'] only_b=[]
  - vs `honda.accord.gen10.us.2018`: mismatches=0 only_a=['CONTROLLED_STANDSTILL'] only_b=[]
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=0 only_a=['CONTROLLED_STANDSTILL'] only_b=[]
- `0x1be` names=['BRAKE_MODULE'] vehicles=4 variants=2
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=0 only_a=[] only_b=['CRUISE_FAULT']
- `0x1c2` names=['EPB_STATUS'] vehicles=9 variants=2
  - vs `honda.odyssey.gen5.us.exl_2018`: mismatches=0 only_a=[] only_b=['EPB_BRAKE_AND_PULL']
- `0x1fa` names=['BRAKE_COMMAND', 'LEGACY_BRAKE_COMMAND'] vehicles=11 variants=2
  - vs `honda.accord.gen10.us.2018`: mismatches=1 only_a=['AEB_REQ_1', 'AEB_REQ_2', 'AEB_STATUS', 'BRAKE_LIGHTS', 'BRAKE_PUMP_REQUEST', 'BRAKE_PUMP_REQUEST_ALT', 'COMPUTER_BRAKE', 'COMPUTER_BRAKE_ALT', 'COMPUTER_BRAKE_REQUEST', 'CRUISE_CANCEL_CMD', 'CRUISE_FAULT_CMD', 'CRUISE_OVERRIDE', 'CRUISE_STATES', 'FCW', 'SET_ME_1', 'SET_ME_X00', 'SET_ME_X00_2', 'SET_ME_X00_3'] only_b=[]
  - vs `honda.civic.gen10.us.hatch_ex_2017`: mismatches=1 only_a=['AEB_REQ_1', 'AEB_REQ_2', 'AEB_STATUS', 'BRAKE_LIGHTS', 'BRAKE_PUMP_REQUEST', 'BRAKE_PUMP_REQUEST_ALT', 'COMPUTER_BRAKE', 'COMPUTER_BRAKE_ALT', 'COMPUTER_BRAKE_REQUEST', 'CRUISE_CANCEL_CMD', 'CRUISE_FAULT_CMD', 'CRUISE_OVERRIDE', 'CRUISE_STATES', 'FCW', 'SET_ME_1', 'SET_ME_X00', 'SET_ME_X00_2', 'SET_ME_X00_3'] only_b=[]
- `0x221` names=['ECON_STATUS', 'XXX_16'] vehicles=9 variants=3
  - vs `honda.civic.gen10.us.touring_2016`: mismatches=0 only_a=['DRIVE_MODE'] only_b=['ECON_ON_2']
  - vs `honda.clarity.gen1.us.hybrid_2018`: mismatches=0 only_a=['DRIVE_MODE'] only_b=['ECON_ON_2']
  - vs `honda.fit.gen3.us.hybrid_2018`: mismatches=2 only_a=['DRIVE_MODE'] only_b=[]
- `0x255` names=['ROUGH_WHEEL_SPEED'] vehicles=15 variants=2
  - vs `acura.rdx.gen3.us.2020`: mismatches=0 only_a=[] only_b=['LONG_COUNTER']
  - vs `honda.accord.gen10.us.2018`: mismatches=0 only_a=[] only_b=['LONG_COUNTER']
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=0 only_a=[] only_b=['LONG_COUNTER']
- `0x294` names=['SCM_FEEDBACK'] vehicles=6 variants=2
  - vs `acura.rdx.gen2.us.2018`: mismatches=0 only_a=[] only_b=['CHECKSUM', 'COUNTER']
  - vs `honda.crv.gen5.eu.executive_2016`: mismatches=0 only_a=[] only_b=['CHECKSUM', 'COUNTER']
  - vs `honda.crv.gen5.us.touring_2016`: mismatches=0 only_a=[] only_b=['CHECKSUM', 'COUNTER']
- `0x326` names=['SCM_FEEDBACK'] vehicles=9 variants=2
  - vs `honda.civic.gen10.us.touring_2016`: mismatches=0 only_a=['CMBS_STATES', 'DRIVERS_DOOR_OPEN'] only_b=['CMBS_BUTTON', 'REVERSE_LIGHT']
  - vs `honda.clarity.gen1.us.hybrid_2018`: mismatches=0 only_a=['CMBS_STATES', 'DRIVERS_DOOR_OPEN'] only_b=['CMBS_BUTTON', 'REVERSE_LIGHT']
  - vs `honda.odyssey.gen5.us.exl_2018`: mismatches=0 only_a=['CMBS_STATES', 'DRIVERS_DOOR_OPEN'] only_b=['CMBS_BUTTON', 'REVERSE_LIGHT']
- `0x33d` names=['LKAS_HUD'] vehicles=15 variants=2
  - vs `honda.civic.gen11.us.ex_2022`: mismatches=2 only_a=[] only_b=['LANE_LINES']
- `0x35e` names=['CAMERA_MESSAGES', 'HIGHBEAM_CONTROL'] vehicles=11 variants=2
  - vs `honda.civic.gen10.us.touring_2016`: mismatches=1 only_a=[] only_b=[]
  - vs `honda.clarity.gen1.us.hybrid_2018`: mismatches=1 only_a=[] only_b=[]
  - vs `honda.fit.gen3.us.ex_2018`: mismatches=1 only_a=[] only_b=[]
- `0x39f` names=['RADAR_HUD'] vehicles=10 variants=2
  - vs `honda.civic.gen10.us.touring_2016`: mismatches=4 only_a=['CMBS_OFF', 'HUD_LEAD', 'SET_TO_0', 'SET_TO_1', 'SET_TO_64', 'ZEROS_BOH4'] only_b=['LEAD_SPEED', 'LEAD_STATE']
  - vs `honda.clarity.gen1.us.hybrid_2018`: mismatches=4 only_a=['CMBS_OFF', 'HUD_LEAD', 'SET_TO_0', 'SET_TO_1', 'SET_TO_64', 'ZEROS_BOH4'] only_b=['LEAD_SPEED', 'LEAD_STATE']
  - vs `honda.fit.gen3.us.hybrid_2018`: mismatches=4 only_a=['CMBS_OFF', 'HUD_LEAD', 'SET_TO_0', 'SET_TO_1', 'SET_TO_64', 'ZEROS_BOH4'] only_b=['LEAD_SPEED', 'LEAD_STATE']
- `0x516` names=['ODOMETER', 'XXX_27'] vehicles=6 variants=2
  - vs `honda.clarity.gen1.us.hybrid_2018`: mismatches=0 only_a=[] only_b=[]

## Name collisions (different IDs)

- `ACC_CONTROL` → 0x1c8, 0x1df
- `CRUISE_PARAMS` → 0x372, 0x37c
- `GEARBOX` → 0x188, 0x191, 0x1a3
- `KINEMATICS` → 0x91, 0x94
- `SCM_BUTTONS` → 0x1a6, 0x296
- `SCM_FEEDBACK` → 0x294, 0x326
- `STEERING_CONTROL` → 0xe4, 0x194
- `STEERING_SENSORS` → 0x14a, 0x156

## Policy

- Never copy Accord fuel (or any absent signal) into Civic.
- `CROSS_PLATFORM_CANDIDATE` is a lead, not a Civic definition.
- DBC presence ≠ `CLUSTER_RX_CONFIRMED`.
