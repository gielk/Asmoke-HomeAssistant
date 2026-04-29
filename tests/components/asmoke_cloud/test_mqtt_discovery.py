from __future__ import annotations

from custom_components.asmoke_cloud.mqtt import (
    _apply_discovery_message,
    _sorted_discovery_candidates,
)


def test_discovery_candidate_merges_device_topics() -> None:
    candidates = {}

    _apply_discovery_message(
        candidates,
        "device/status/A08241009A12582",
        {
            "deviceID": "A08241009A12582",
            "status": "idle",
            "mode": "QUICK",
            "batteryLevel": 47,
            "temperatures": {
                "grillTemp1": 135,
                "grillTemp2": 159,
                "probeATemp": 499,
                "probeBTemp": 65,
            },
        },
    )
    _apply_discovery_message(
        candidates,
        "device/temperatures/A08241009A12582",
        {
            "grillTemp1": 136,
            "grillTemp2": 160,
            "probeATemp": 499,
            "probeBTemp": 66,
        },
    )

    candidate = candidates["A08241009A12582"]

    assert candidate["message_count"] == 2
    assert candidate["payload_matches_topic"] is True
    assert candidate["status"] == "idle"
    assert candidate["mode"] == "QUICK"
    assert candidate["battery_level"] == 47
    assert candidate["grill_temp_1"] == 136
    assert candidate["probe_a_temp"] is None
    assert candidate["probe_b_temp"] == 66
    assert candidate["topic_types"] == ["status", "temperatures"]


def test_discovery_candidates_sort_by_signal_strength() -> None:
    candidates = {}

    _apply_discovery_message(
        candidates,
        "device/temperatures/A08241009A99999",
        {"grillTemp1": 120},
    )
    _apply_discovery_message(
        candidates,
        "device/status/A08241009A12582",
        {"deviceID": "A08241009A12582", "status": "running"},
    )

    sorted_candidates = _sorted_discovery_candidates(candidates)

    assert sorted_candidates[0]["device_id"] == "A08241009A12582"


def test_discovery_ignores_mismatched_topic_and_payload_device_ids() -> None:
    candidates = {}

    _apply_discovery_message(
        candidates,
        "device/status/A08241009A12582",
        {"deviceID": "A08241009A99999", "status": "running"},
    )

    assert candidates == {}
