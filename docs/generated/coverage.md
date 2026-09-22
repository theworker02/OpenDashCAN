# Coverage

# Honda coverage matrix

_Auto-generated. Confidence labels only — not hardware claims._

| Platform | RPM | SPEED | FUEL | TEMP | GEAR | TURN | ABS | SRS |
|----------|------|------|------|------|------|------|------|------|
| `honda.accord.gen10.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.accord.gen11.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.civic.gen10.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.civic.gen11.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.civic.gen7.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.civic.gen8.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.civic.gen9.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.crv.gen5.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.crv.gen6.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.element.gen1.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.fit.gen3.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.hrv.gen2.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.insight.gen3.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.odyssey.gen5.us` | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN | DOCUMENTED | DOCUMENTED | UNKNOWN | UNKNOWN |
| `honda.pilot.gen3.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.pilot.gen4.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.prelude.gen5.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `honda.ridgeline.gen2.us` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

# Adaptation readiness

_Requirement states — not percentages. Mode: DOCUMENTATION_ONLY._

## `honda.civic.gen8.us.r18.auto` → `honda.civic.gen10.cluster.digital`

Protocol compatibility: **INCOMPLETE**

| Signal | Source | Target | Priority | Readiness |
|--------|--------|--------|----------|-----------|
| `adas.acc_state` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.driver_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.passenger_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_left_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_right_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.trunk` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.parking_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.service_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `chassis.steering_angle` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `fuel.level` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `lighting.headlights_on` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.high_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.left_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.low_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.right_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `powertrain.coolant_temperature` | UNKNOWN | UNKNOWN | COSMETIC | REQUIRES_CAN_CAPTURE |
| `powertrain.engine_rpm` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |
| `powertrain.throttle_position` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_driver` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_passenger` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `stability.vsa_warning` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `transmission.gear` | UNKNOWN | DOCUMENTED | OPTIONAL | BLOCKED_SOURCE |
| `vehicle.ignition_state` | UNKNOWN | UNKNOWN | REQUIRED | REQUIRES_CAN_CAPTURE |
| `vehicle.odometer` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `vehicle.speed` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |

Summary: BLOCKED_SOURCE=22, REQUIRES_CAN_CAPTURE=3

## `honda.civic.gen8.us.r18.auto` → `honda.civic.gen11.cluster.digital`

Protocol compatibility: **INCOMPLETE**

| Signal | Source | Target | Priority | Readiness |
|--------|--------|--------|----------|-----------|
| `adas.acc_state` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.driver_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.passenger_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_left_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_right_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.trunk` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.parking_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.service_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `fuel.level` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `lighting.high_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.left_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.low_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.right_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `powertrain.coolant_temperature` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `powertrain.engine_rpm` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |
| `powertrain.throttle_position` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_driver` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_passenger` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `stability.vsa_warning` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `transmission.gear` | UNKNOWN | DOCUMENTED | OPTIONAL | BLOCKED_SOURCE |
| `vehicle.ignition_state` | UNKNOWN | UNKNOWN | REQUIRED | REQUIRES_CAN_CAPTURE |
| `vehicle.odometer` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `vehicle.speed` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |

Summary: BLOCKED_SOURCE=20, REQUIRES_CAN_CAPTURE=3

## `honda.civic.gen8.us.r18.auto` → `honda.accord.gen10.cluster.digital`

Protocol compatibility: **INCOMPLETE**

| Signal | Source | Target | Priority | Readiness |
|--------|--------|--------|----------|-----------|
| `adas.acc_state` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.driver_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.passenger_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_left_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_right_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.trunk` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.parking_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.service_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `fuel.level` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `lighting.high_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.left_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.low_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.right_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `powertrain.coolant_temperature` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `powertrain.engine_rpm` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |
| `powertrain.throttle_position` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_driver` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_passenger` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `stability.vsa_warning` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `transmission.gear` | UNKNOWN | DOCUMENTED | OPTIONAL | BLOCKED_SOURCE |
| `vehicle.ignition_state` | UNKNOWN | UNKNOWN | REQUIRED | REQUIRES_CAN_CAPTURE |
| `vehicle.odometer` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `vehicle.speed` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |

Summary: BLOCKED_SOURCE=20, REQUIRES_CAN_CAPTURE=3

## `honda.civic.gen8.us.r18.auto` → `honda.crv.gen5.cluster.digital`

Protocol compatibility: **INCOMPLETE**

| Signal | Source | Target | Priority | Readiness |
|--------|--------|--------|----------|-----------|
| `adas.acc_state` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.driver_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.passenger_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_left_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.rear_right_door` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `body.trunk` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.parking_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `brakes.service_brake` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `fuel.level` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `lighting.high_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.left_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.low_beam` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `lighting.right_indicator` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `powertrain.coolant_temperature` | UNKNOWN | UNKNOWN | UNKNOWN | REQUIRES_CAN_CAPTURE |
| `powertrain.engine_rpm` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |
| `powertrain.throttle_position` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_driver` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `safety.seatbelt_passenger` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `stability.vsa_warning` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `transmission.gear` | UNKNOWN | DOCUMENTED | OPTIONAL | BLOCKED_SOURCE |
| `vehicle.ignition_state` | UNKNOWN | UNKNOWN | REQUIRED | REQUIRES_CAN_CAPTURE |
| `vehicle.odometer` | UNKNOWN | DOCUMENTED | UNKNOWN | BLOCKED_SOURCE |
| `vehicle.speed` | UNKNOWN | DOCUMENTED | REQUIRED | BLOCKED_SOURCE |

Summary: BLOCKED_SOURCE=20, REQUIRES_CAN_CAPTURE=3
