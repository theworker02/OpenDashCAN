#!/bin/bash
# Listen-only bring-up for ODC-REC-RPI-1 (run as root)
set -euo pipefail
BITRATE="${ODC_CAN_BITRATE:-500000}"
IFACE="${ODC_CAN_IFACE:-can0}"
OUT_DIR="${ODC_CAPTURE_DIR:-/home/pi/captures}"
mkdir -p "$OUT_DIR"
ip link set "$IFACE" down 2>/dev/null || true
ip link set "$IFACE" up type can bitrate "$BITRATE" listen-only on
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG="$OUT_DIR/${STAMP}_${IFACE}.asc"
echo "Recording listen-only on $IFACE @ $BITRATE -> $LOG"
exec candump -L "$IFACE" | tee "$LOG"
