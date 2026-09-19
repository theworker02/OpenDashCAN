# Netlist — ODC-REC-RPI-1A (readable)

## Power

| Net | Members |
|-----|---------|
| VIN_RAW | J_OBD.16, F1.in |
| VIN_FUSED | F1.out, D_REV.A, D_TVS.cathode |
| VIN_PROT | D_REV.K, U3.VIN, C_BULK_IN+ |
| GND | J_OBD.4, J_OBD.5, all IC GND, D_TVS.anode, chassis |
| +5V | U3.VOUT, J_PI.2, J_PI.4, LED_PWR anode via R |
| +3V3 | J_PI.1, U1.VDD, U2.VCC, R_PU_RST |

## CAN differential

| Net | Members |
|-----|---------|
| CANH | J_OBD.6, D_ESD.CANH, U2.CANH, R_TERM via JP_TERM |
| CANL | J_OBD.14, D_ESD.CANL, U2.CANL, R_TERM via JP_TERM |

## MCP2515 digital

| Net | Members |
|-----|---------|
| SPI_CE0 | U1.CS, J_PI.24 (BCM8) |
| SPI_SCLK | U1.SCK, J_PI.23 (BCM11) |
| SPI_MOSI | U1.SI, J_PI.19 (BCM10) |
| SPI_MISO | U1.SO, J_PI.21 (BCM9) |
| CAN_INT | U1.INT, J_PI.22 (BCM25), LED_ACT optional |
| CAN_RXD | U1.RXCAN, U2.RXD |
| CAN_TXD | U1.TXCAN — **tie inactive / no software TX**; U2.TXD pulled to recessive idle per transceiver datasheet |
| XTAL | Y1 across U1 OSC1/OSC2 with C_Y1 pair to GND |

## Pi header (subset used)

Power pins 2/4 (+5V), 6/9/14/20/25/30/34/39 (GND), 1 (+3V3), SPI pins above, GPIO25.
