from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from collections.abc import Callable, Mapping
from copy import deepcopy
from datetime import UTC, datetime
from importlib import import_module
from json import JSONDecodeError
from typing import Any

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_TARGET_TEMP,
    CONF_DEBUG_LOGGING,
    CONF_EXTRA_TOPICS,
    CONF_KEEPALIVE,
    CONF_OFFLINE_TIMEOUT,
    DEFAULT_KEEPALIVE,
    DEFAULT_OFFLINE_TIMEOUT,
    DEFAULT_TARGET_TEMPERATURE,
    action_topic,
    result_topic,
    status_topic,
    temperatures_topic,
)

_LOGGER = logging.getLogger(__name__)


class AsmokeConnectionError(HomeAssistantError):
    """Raised when the broker cannot be reached."""


class AsmokeAuthenticationError(AsmokeConnectionError):
    """Raised when broker authentication is rejected."""


def _mqtt_module() -> Any:
    try:
        return import_module("paho.mqtt.client")
    except ModuleNotFoundError as err:
        raise AsmokeConnectionError(
            "paho-mqtt is not available yet; restart Home Assistant and try again"
        ) from err


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _normalize_bool(value: Any) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "on", "true", "yes", "active", "online"}:
            return True
        if normalized in {"0", "off", "false", "no", "inactive", "offline"}:
            return False

    return None


def _normalize_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_probe_temp(value: Any) -> int | None:
    normalized = _normalize_int(value)
    if normalized == 499:
        return None
    return normalized


def _clean_extra_topics(value: Any) -> list[str]:
    if value is None or value == "":
        return []

    if isinstance(value, list):
        return [topic.strip() for topic in value if str(topic).strip()]

    return [topic.strip() for topic in str(value).split(",") if topic.strip()]


def _default_client_id(device_id: str, entry_id: str) -> str:
    return f"ha_asmoke_{device_id.lower()}_{entry_id[:8]}"


async def async_validate_broker_connection(config: Mapping[str, Any]) -> None:
    await asyncio.to_thread(_validate_broker_connection, dict(config))


def _validate_broker_connection(config: dict[str, Any]) -> None:
    mqtt = _mqtt_module()
    username = str(config.get(CONF_USERNAME, "")).strip()
    password = str(config.get(CONF_PASSWORD, "")).strip()
    host = str(config.get(CONF_HOST, "")).strip()

    if not host:
        raise AsmokeConnectionError("Missing MQTT host")

    if not username or not password:
        raise AsmokeAuthenticationError("Missing MQTT credentials")

    event = threading.Event()
    result: dict[str, Any] = {"rc": None, "error": None}

    client = mqtt.Client(
        client_id=f"ha_validate_{int(time.time())}",
        protocol=mqtt.MQTTv311,
    )
    client.username_pw_set(username=username, password=password)

    def on_connect(
        _client: mqtt.Client,
        _userdata: Any,
        _flags: dict[str, Any],
        rc: int,
        _properties: Any = None,
    ) -> None:
        result["rc"] = rc
        event.set()

    def on_disconnect(
        _client: Any,
        _userdata: Any,
        rc: int,
        _properties: Any = None,
    ) -> None:
        if result["rc"] is None and rc != 0:
            result["error"] = rc
            event.set()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(
            host,
            int(config.get(CONF_PORT, 1883)),
            int(config.get(CONF_KEEPALIVE, DEFAULT_KEEPALIVE)),
        )
        client.loop_start()

        if not event.wait(10):
            raise AsmokeConnectionError("Timed out while waiting for MQTT CONNACK")
    except OSError as err:
        raise AsmokeConnectionError(str(err)) from err
    finally:
        try:
            client.disconnect()
        except OSError:
            pass
        client.loop_stop()

    if result["rc"] in {4, 5}:
        raise AsmokeAuthenticationError("Broker rejected username or password")

    if result["rc"] not in {0, None}:
        raise AsmokeConnectionError(f"Broker returned MQTT rc={result['rc']}")

    if result["error"] is not None:
        raise AsmokeConnectionError(f"Broker disconnected with rc={result['error']}")


class AsmokeMqttRuntime:
    """Handle vendor MQTT connectivity and local device state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        data: Mapping[str, Any],
        options: Mapping[str, Any],
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.device_id = str(data[CONF_DEVICE_ID])
        self.name = str(data.get(CONF_NAME) or f"Asmoke {self.device_id}")
        self.host = str(data[CONF_HOST])
        self.port = int(data[CONF_PORT])
        self.username = str(data[CONF_USERNAME])
        self.password = str(data[CONF_PASSWORD])
        self.keepalive = int(data.get(CONF_KEEPALIVE, DEFAULT_KEEPALIVE))
        self.offline_timeout = int(
            options.get(CONF_OFFLINE_TIMEOUT, DEFAULT_OFFLINE_TIMEOUT)
        )
        self.extra_topics = _clean_extra_topics(options.get(CONF_EXTRA_TOPICS))
        self.debug_logging = bool(options.get(CONF_DEBUG_LOGGING, False))
        self.client_id = _default_client_id(self.device_id, self.entry_id)

        self._client: Any | None = None
        self._started = False
        self._update_callback: Callable[[dict[str, Any]], None] | None = None
        self._state: dict[str, Any] = {
            "device_id": self.device_id,
            "friendly_name": self.name,
            "broker_connected": False,
            "device_online": False,
            "last_error": None,
            "last_message_at": None,
            "last_message_topic": None,
            "message_count": 0,
            "messages_by_topic": {},
            "client_id": self.client_id,
            "subscribed_topics": self._subscription_topics(),
            "grill_temp_1": None,
            "grill_temp_2": None,
            "probe_a_temp": None,
            "probe_b_temp": None,
            "battery_level": None,
            "roast_progress": None,
            "target_temp": None,
            "target_time": None,
            "mode": None,
            "wifi_status": None,
            "ignition_status": None,
            "last_result_message": None,
            "status_payload": {},
            "temperatures_payload": {},
            "result_payload": {},
        }

    def set_update_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._update_callback = callback

    def _subscription_topics(self) -> list[str]:
        topics = [
            status_topic(self.device_id),
            temperatures_topic(self.device_id),
            result_topic(self.device_id),
        ]
        topics.extend(self.extra_topics)
        return topics

    async def async_start(self) -> None:
        if self._started:
            return

        mqtt = _mqtt_module()
        client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        client.username_pw_set(username=self.username, password=self.password)
        client.reconnect_delay_set(min_delay=5, max_delay=60)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        if self.debug_logging:
            client.enable_logger(_LOGGER)

        client.connect_async(self.host, self.port, self.keepalive)
        client.loop_start()

        self._client = client
        self._started = True
        self._push_update()

    async def async_stop(self) -> None:
        if not self._started or self._client is None:
            return

        client = self._client
        self._client = None
        self._started = False

        await asyncio.to_thread(client.disconnect)
        await asyncio.to_thread(client.loop_stop)

        self._state["broker_connected"] = False
        self._push_update()

    async def async_publish_action(
        self,
        command: str,
        data: Mapping[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"type": "action", "command": command}
        if data:
            payload["data"] = dict(data)

        await self.async_publish_json(action_topic(self.device_id), payload)

    async def async_publish_smoke_target_temp(self, target_temp: int) -> None:
        await self.async_publish_action(
            "Smoke",
            {ATTR_TARGET_TEMP: int(target_temp)},
        )

    async def async_publish_json(self, topic: str, payload: Mapping[str, Any]) -> None:
        if self._client is None:
            raise AsmokeConnectionError("MQTT client is not running")

        message = json.dumps(payload, separators=(",", ":"))
        info = await asyncio.to_thread(self._client.publish, topic, message, 0, False)

        if info.rc != 0:
            raise AsmokeConnectionError(f"MQTT publish failed with rc={info.rc}")

    def snapshot(self) -> dict[str, Any]:
        snapshot = deepcopy(self._state)
        last_message_at: datetime | None = snapshot["last_message_at"]
        snapshot["subscribed_topics"] = self._subscription_topics()
        snapshot["offline_timeout"] = self.offline_timeout
        snapshot["broker_host"] = self.host
        snapshot["broker_port"] = self.port
        snapshot["device_online"] = bool(
            last_message_at
            and (_utcnow() - last_message_at).total_seconds() <= self.offline_timeout
        )
        return snapshot

    def diagnostics_snapshot(self) -> dict[str, Any]:
        snapshot = self.snapshot()
        if snapshot["last_message_at"] is not None:
            snapshot["last_message_at"] = snapshot["last_message_at"].isoformat()
        return snapshot

    def _push_update(self) -> None:
        if self._update_callback is not None:
            self._update_callback(self.snapshot())

    def _on_connect(
        self,
        _client: Any,
        _userdata: Any,
        _flags: dict[str, Any],
        rc: int,
        _properties: Any = None,
    ) -> None:
        self.hass.loop.call_soon_threadsafe(self._handle_connect, rc)

    def _on_disconnect(
        self,
        _client: Any,
        _userdata: Any,
        rc: int,
        _properties: Any = None,
    ) -> None:
        self.hass.loop.call_soon_threadsafe(self._handle_disconnect, rc)

    def _on_message(
        self,
        _client: Any,
        _userdata: Any,
        message: Any,
    ) -> None:
        self.hass.loop.call_soon_threadsafe(
            self._handle_message,
            message.topic,
            bytes(message.payload),
        )

    def _handle_connect(self, rc: int) -> None:
        self._state["broker_connected"] = rc == 0
        self._state["last_error"] = None if rc == 0 else f"mqtt_rc_{rc}"

        if rc == 0 and self._client is not None:
            for topic in self._subscription_topics():
                self._client.subscribe(topic, qos=0)

        self._push_update()

    def _handle_disconnect(self, rc: int) -> None:
        self._state["broker_connected"] = False
        if rc != 0:
            self._state["last_error"] = f"disconnect_rc_{rc}"
        self._push_update()

    def _handle_message(self, topic: str, payload: bytes) -> None:
        decoded_payload = self._decode_payload(payload)

        if self.debug_logging:
            _LOGGER.debug("Received Asmoke MQTT message on %s: %s", topic, decoded_payload)

        self._state["last_message_at"] = _utcnow()
        self._state["last_message_topic"] = topic
        self._state["message_count"] += 1
        self._state["messages_by_topic"][topic] = (
            self._state["messages_by_topic"].get(topic, 0) + 1
        )

        if topic == status_topic(self.device_id):
            self._apply_status_payload(decoded_payload)
        elif topic == temperatures_topic(self.device_id):
            self._apply_temperatures_payload(decoded_payload)
        elif topic == result_topic(self.device_id):
            self._apply_result_payload(decoded_payload)

        self._push_update()

    def _decode_payload(self, payload: bytes) -> Any:
        text = payload.decode("utf-8", errors="replace")

        try:
            return json.loads(text)
        except JSONDecodeError:
            return text

    def _apply_status_payload(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return

        grill = payload.get("grill") if isinstance(payload.get("grill"), dict) else {}

        self._state["status_payload"] = payload
        self._state["battery_level"] = _normalize_int(payload.get("batteryLevel"))
        self._state["roast_progress"] = _normalize_int(payload.get("roastProgress"))
        self._state["target_temp"] = _normalize_int(
            payload.get("targetTemp", grill.get("targetTemp"))
        )
        self._state["target_time"] = _normalize_int(
            payload.get("targetTime", grill.get("targetTime"))
        )
        self._state["mode"] = payload.get("mode")
        self._state["wifi_status"] = payload.get("wifiStatus")

        ignition = _normalize_bool(payload.get("ignitionStatus"))
        if ignition is None:
            ignition = _normalize_bool(payload.get("status"))
        self._state["ignition_status"] = ignition

        temperatures = payload.get("temperatures")
        if isinstance(temperatures, dict):
            self._apply_temperatures_payload(temperatures)

    def _apply_temperatures_payload(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return

        self._state["temperatures_payload"] = payload
        self._state["grill_temp_1"] = _normalize_int(payload.get("grillTemp1"))
        self._state["grill_temp_2"] = _normalize_int(payload.get("grillTemp2"))
        self._state["probe_a_temp"] = _normalize_probe_temp(payload.get("probeATemp"))
        self._state["probe_b_temp"] = _normalize_probe_temp(payload.get("probeBTemp"))

    def _apply_result_payload(self, payload: Any) -> None:
        self._state["result_payload"] = payload if isinstance(payload, dict) else {"raw": payload}

        if isinstance(payload, dict):
            self._state["last_result_message"] = payload.get("message")
        elif isinstance(payload, str):
            self._state["last_result_message"] = payload
