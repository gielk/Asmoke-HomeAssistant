from __future__ import annotations

from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)

DOMAIN = "asmoke_cloud"
NAME = "Asmoke Cloud"

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
]

CONF_DEBUG_LOGGING = "debug_logging"
CONF_EXTRA_TOPICS = "extra_topics"
CONF_KEEPALIVE = "keepalive"
CONF_OFFLINE_TIMEOUT = "offline_timeout"

DEFAULT_BROKER_HOST = "47.253.1.220"
DEFAULT_BROKER_PORT = 1883
DEFAULT_KEEPALIVE = 60
DEFAULT_OFFLINE_TIMEOUT = 900
DEFAULT_UPDATE_INTERVAL = 30

DEFAULT_TARGET_TEMPERATURE = 110
MIN_TARGET_TEMPERATURE = 0
MAX_TARGET_TEMPERATURE = 300

ACTION_TOPIC_TEMPLATE = "asmoke/action/{device_id}"
STATUS_TOPIC_TEMPLATE = "device/status/{device_id}"
TEMPERATURES_TOPIC_TEMPLATE = "device/temperatures/{device_id}"
RESULT_TOPIC_TEMPLATE = "device/result/{device_id}"

SERVICE_PUBLISH_RAW_ACTION = "publish_raw_action"
SERVICE_SET_SMOKE_TARGET_TEMP = "set_smoke_target_temp"

ATTR_ENTRY_ID = "entry_id"
ATTR_PAYLOAD = "payload"
ATTR_TARGET_TEMP = "target_temp"

LOCAL_AUTH_FILE = "local_auth.json"
LOCAL_AUTH_CONFIG_FILE = f"{DOMAIN}_local_auth.json"

SENSITIVE_KEYS = {
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_CLIENT_ID,
}

MQTT_CONFIG_KEYS = (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_KEEPALIVE,
)


def action_topic(device_id: str) -> str:
    return ACTION_TOPIC_TEMPLATE.format(device_id=device_id)


def status_topic(device_id: str) -> str:
    return STATUS_TOPIC_TEMPLATE.format(device_id=device_id)


def temperatures_topic(device_id: str) -> str:
    return TEMPERATURES_TOPIC_TEMPLATE.format(device_id=device_id)


def result_topic(device_id: str) -> str:
    return RESULT_TOPIC_TEMPLATE.format(device_id=device_id)
