"""Donor / cluster knowledge levels (orthogonal to Confidence).

Confidence answers *how strongly we trust a claim*.
DonorKnowledge answers *what kind of claim* it is relative to cluster adaptation.

Never promote VEHICLE_PROTOCOL_DOCUMENTED → CLUSTER_RX_CONFIRMED without
cluster-side evidence (capture, CivicX RE with explicit RX claim, or bench).
"""

from __future__ import annotations

from enum import Enum


class DonorKnowledge(str, Enum):
    """Where a signal/message sits in the donor-cluster adaptation pipeline."""

    UNKNOWN = "UNKNOWN"
    VEHICLE_PROTOCOL_DOCUMENTED = "VEHICLE_PROTOCOL_DOCUMENTED"
    CLUSTER_RELEVANT_SIGNAL_DOCUMENTED = "CLUSTER_RELEVANT_SIGNAL_DOCUMENTED"
    CLUSTER_RX_CONFIRMED = "CLUSTER_RX_CONFIRMED"
    CLUSTER_TIMING_CONFIRMED = "CLUSTER_TIMING_CONFIRMED"
    CLUSTER_CHECKSUM_CONFIRMED = "CLUSTER_CHECKSUM_CONFIRMED"
    CLUSTER_STARTUP_CONFIRMED = "CLUSTER_STARTUP_CONFIRMED"
    CLUSTER_ENVIRONMENT_COMPLETE = "CLUSTER_ENVIRONMENT_COMPLETE"
    BENCH_VERIFIED = "BENCH_VERIFIED"


# Signals often needed by digital clusters (relevance, not RX confirmation).
CLUSTER_RELEVANT_TAXONOMY: frozenset[str] = frozenset(
    {
        "powertrain.engine_rpm",
        "vehicle.speed",
        "vehicle.odometer",
        "transmission.gear",
        "fuel.level",
        "powertrain.coolant_temperature",
        "lighting.left_indicator",
        "lighting.right_indicator",
        "lighting.high_beam",
        "lighting.low_beam",
        "brakes.parking_brake",
        "brakes.abs_warning",
        "stability.vsa_warning",
        "safety.srs_warning",
        "safety.check_engine",
        "safety.seatbelt_driver",
        "body.driver_door",
        "body.passenger_door",
        "body.trunk",
        "vehicle.ignition_state",
    }
)


def default_knowledge_for_dbc_signal(taxonomy: str | None) -> DonorKnowledge:
    """DBC import always starts as vehicle-protocol documentation."""
    if taxonomy and taxonomy in CLUSTER_RELEVANT_TAXONOMY:
        return DonorKnowledge.CLUSTER_RELEVANT_SIGNAL_DOCUMENTED
    return DonorKnowledge.VEHICLE_PROTOCOL_DOCUMENTED
