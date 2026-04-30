from __future__ import annotations

import json
from pathlib import Path


def _integration_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "custom_components" / "asmoke_cloud"


def test_brand_assets_exist_for_hacs_and_home_assistant() -> None:
    brand_dir = _integration_dir() / "brand"

    assert (brand_dir / "icon.png").is_file()
    assert (brand_dir / "icon@2x.png").is_file()
    assert (brand_dir / "logo.png").is_file()
    assert (brand_dir / "logo@2x.png").is_file()


def test_frontend_card_asset_is_shipped() -> None:
    card_path = _integration_dir() / "frontend" / "asmoke-smoker-card.js"
    assert card_path.is_file()

    card_source = card_path.read_text()
    assert "asmoke-smoker-card" in card_source
    assert "asmoke-smoker-history-card" in card_source
    assert "asmoke-smoker-session-card" in card_source
    assert "hide_offline_data" in card_source
    assert "offline_hide_after" in card_source
    assert "window.customCards" in card_source
    assert "customElements.define" in card_source


def test_dashboard_preview_image_exists() -> None:
    image_path = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "images"
        / "asmoke-dashboard-cards-preview.png"
    )

    assert image_path.is_file()


def test_icons_json_defines_custom_entity_icons() -> None:
    icons_path = _integration_dir() / "icons.json"
    icons = json.loads(icons_path.read_text())

    assert icons["entity"]["button"]["start_quick_cook"]["default"] == "mdi:play-circle-outline"
    assert icons["entity"]["button"]["stop_cook"]["default"] == "mdi:stop-circle-outline"
    assert icons["entity"]["climate"]["pit_controller"]["default"] == "mdi:grill"
    assert icons["entity"]["climate"]["pit_controller"]["state_attributes"]["preset_mode"]["state"] == {
        "smoke": "mdi:smoke",
        "quick": "mdi:lightning-bolt",
    }
    assert icons["entity"]["sensor"]["target_time"]["default"] == "mdi:timer-outline"
    assert icons["entity"]["sensor"]["mode"]["default"] == "mdi:grill"
    assert icons["entity"]["sensor"]["last_result_message"]["default"] == "mdi:message-text-outline"
    assert icons["entity"]["number"]["quick_target_time"]["default"] == "mdi:timer-outline"
