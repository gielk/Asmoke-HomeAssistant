const ASMOKE_SMOKER_CARD_VERSION = "0.4.0";
const ASMOKE_SMOKER_CARD_TAG = "asmoke-smoker-card";
const ASMOKE_SMOKER_CARD_EDITOR_TAG = "asmoke-smoker-card-editor";
const ASMOKE_HISTORY_CARD_TAG = "asmoke-smoker-history-card";
const ASMOKE_HISTORY_CARD_EDITOR_TAG = "asmoke-smoker-history-card-editor";
const ASMOKE_SESSION_CARD_TAG = "asmoke-smoker-session-card";
const ASMOKE_SESSION_CARD_EDITOR_TAG = "asmoke-smoker-session-card-editor";

const ASMOKE_UNAVAILABLE_STATES = new Set(["unknown", "unavailable", "", null, undefined]);
const ASMOKE_DEFAULT_OFFLINE_HIDE_AFTER = 600;

const ASMOKE_ENTITY_KEYS = [
  "climate",
  "quick_time",
  "start_quick",
  "stop",
  "grill_temp_1",
  "grill_temp_2",
  "probe_a_temp",
  "probe_b_temp",
  "battery",
  "target_time",
  "mode",
  "broker_connected",
  "device_online",
  "cook_active",
  "wifi_connected",
  "last_result",
];

const ASMOKE_EDITOR_LABELS = {
  name: "Name",
  device_id: "Asmoke device",
  climate: "Pit thermostat",
  quick_time: "Quick target time",
  start_quick: "Start quick button",
  stop: "Stop button",
  cook_active: "Cook active",
  device_online: "Device online",
  broker_connected: "Broker connected",
  hide_offline_data: "Hide live values when offline",
  offline_hide_after: "Hide after",
};

const ASMOKE_ENTITY_DEFINITIONS = {
  climate: {
    domain: "climate",
    suffixes: ["_pit_thermostat", "_pit_controller"],
    translationKeys: ["pit_controller"],
  },
  quick_time: {
    domain: "number",
    suffixes: ["_quick_target_time"],
    translationKeys: ["quick_target_time"],
    aliases: ["quick_target_time"],
  },
  start_quick: {
    domain: "button",
    suffixes: ["_start_quick_cook"],
    translationKeys: ["start_quick_cook"],
    aliases: ["start_quick_cook"],
  },
  stop: {
    domain: "button",
    suffixes: ["_stop_cook"],
    translationKeys: ["stop_cook"],
    aliases: ["stop_cook"],
  },
  grill_temp_1: {
    domain: "sensor",
    suffixes: ["_grill_temperature_1"],
    translationKeys: ["grill_temperature_1"],
  },
  grill_temp_2: {
    domain: "sensor",
    suffixes: ["_grill_temperature_2"],
    translationKeys: ["grill_temperature_2"],
  },
  probe_a_temp: {
    domain: "sensor",
    suffixes: ["_probe_a_temperature"],
    translationKeys: ["probe_a_temperature"],
  },
  probe_b_temp: {
    domain: "sensor",
    suffixes: ["_probe_b_temperature"],
    translationKeys: ["probe_b_temperature"],
  },
  battery: {
    domain: "sensor",
    suffixes: ["_battery_level"],
    translationKeys: ["battery_level"],
  },
  target_time: {
    domain: "sensor",
    suffixes: ["_target_time"],
    translationKeys: ["target_time"],
  },
  mode: {
    domain: "sensor",
    suffixes: ["_mode"],
    translationKeys: ["mode"],
  },
  broker_connected: {
    domain: "binary_sensor",
    suffixes: ["_broker_connected"],
    translationKeys: ["broker_connected"],
  },
  device_online: {
    domain: "binary_sensor",
    suffixes: ["_device_online"],
    translationKeys: ["device_online"],
  },
  cook_active: {
    domain: "binary_sensor",
    suffixes: ["_cook_active"],
    translationKeys: ["cook_active"],
  },
  wifi_connected: {
    domain: "binary_sensor",
    suffixes: ["_wi_fi_connected", "_wifi_connected"],
    translationKeys: ["wifi_connected"],
  },
  last_result: {
    domain: "sensor",
    suffixes: ["_last_result_message"],
    translationKeys: ["last_result_message"],
  },
};

const html = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (char) => {
    const escapes = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return escapes[char];
  });

const percent = (value, max) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || max <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(100, (numeric / max) * 100));
};

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const firstFinite = (...values) => {
  for (const value of values) {
    const numeric = Number(value);
    if (Number.isFinite(numeric)) {
      return numeric;
    }
  }
  return null;
};

const deriveAsmokePrefix = (entityId) => {
  const objectId = String(entityId ?? "").replace(/^climate\./, "");
  for (const suffix of ["_pit_thermostat", "_pit_controller"]) {
    if (objectId.endsWith(suffix)) {
      return objectId.slice(0, -suffix.length);
    }
  }
  return objectId;
};

const registryEntry = (hass, entityId) => hass?.entities?.[entityId];

const entityDomain = (entityId) => String(entityId ?? "").split(".")[0];

const entityObjectId = (entityId) =>
  String(entityId ?? "").includes(".") ? String(entityId).split(".").slice(1).join(".") : "";

const configuredEntity = (config, key) => {
  if (config[key]) {
    return config[key];
  }
  for (const alias of ASMOKE_ENTITY_DEFINITIONS[key]?.aliases ?? []) {
    if (config[alias]) {
      return config[alias];
    }
  }
  return undefined;
};

const entityMatchesDefinition = (hass, entityId, key) => {
  const definition = ASMOKE_ENTITY_DEFINITIONS[key];
  if (!definition || entityDomain(entityId) !== definition.domain) {
    return false;
  }
  const objectId = entityObjectId(entityId);
  const entry = registryEntry(hass, entityId);
  return (
    definition.suffixes.some((suffix) => objectId.endsWith(suffix)) ||
    definition.translationKeys.includes(entry?.translation_key) ||
    (key === "climate" && entry?.platform === "asmoke_cloud")
  );
};

const deviceEntity = (hass, deviceId, key) => {
  if (!hass?.states || !deviceId) {
    return undefined;
  }
  return Object.keys(hass.states)
    .filter((entityId) => registryEntry(hass, entityId)?.device_id === deviceId)
    .find((entityId) => entityMatchesDefinition(hass, entityId, key));
};

const findAsmokeClimateCandidates = (hass) =>
  Object.keys(hass?.states ?? {}).filter((entityId) =>
    entityMatchesDefinition(hass, entityId, "climate"),
  );

const resolveAsmokeClimate = (hass, config) => {
  if (config.climate) {
    return config.climate;
  }
  if (config.device_id) {
    const climate = deviceEntity(hass, config.device_id, "climate");
    if (climate) {
      return climate;
    }
  }
  const candidates = findAsmokeClimateCandidates(hass);
  return candidates.length === 1 ? candidates[0] : undefined;
};

const resolveAsmokeDeviceId = (hass, config, climate) =>
  config.device_id || registryEntry(hass, climate)?.device_id;

const defaultEntityForPrefix = (prefix, key) => {
  const definition = ASMOKE_ENTITY_DEFINITIONS[key];
  if (!prefix || !definition?.suffixes?.length) {
    return undefined;
  }
  return `${definition.domain}.${prefix}${definition.suffixes[0]}`;
};

const buildAsmokeEntities = (config, hass) => {
  const climate = resolveAsmokeClimate(hass, config);
  const deviceId = resolveAsmokeDeviceId(hass, config, climate);
  const prefix = config.entity_prefix || deriveAsmokePrefix(climate);
  const entities = { climate };

  for (const key of ASMOKE_ENTITY_KEYS) {
    if (key === "climate") {
      continue;
    }
    entities[key] =
      configuredEntity(config, key) ||
      deviceEntity(hass, deviceId, key) ||
      defaultEntityForPrefix(prefix, key);
  }

  return entities;
};

const timestampMs = (value) => {
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : null;
};

const secondsConfig = (value, fallback) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric >= 0 ? numeric : fallback;
};

const isOnState = (stateObj) => String(stateObj?.state ?? "").toLowerCase() === "on";

const isUnavailableState = (stateObj) => ASMOKE_UNAVAILABLE_STATES.has(stateObj?.state);

const offlineHideState = (config, hass, entities) => {
  if (config?.hide_offline_data !== true) {
    return { hidden: false, offline: false, useCache: false, remainingMs: null };
  }

  const hideAfterMs =
    secondsConfig(config?.offline_hide_after, ASMOKE_DEFAULT_OFFLINE_HIDE_AFTER) * 1000;
  const now = Date.now();
  const checks = [
    {
      entity: entities?.broker_connected,
      isOffline: (stateObj) => !isOnState(stateObj),
    },
    {
      entity: entities?.device_online,
      isOffline: (stateObj) => !isOnState(stateObj),
    },
    {
      entity: entities?.climate,
      isOffline: (stateObj) => isUnavailableState(stateObj),
    },
  ]
    .map((check) => {
      const stateObj = check.entity ? hass?.states?.[check.entity] : undefined;
      if (!stateObj || !check.isOffline(stateObj)) {
        return null;
      }
      const changedAt =
        timestampMs(stateObj.last_changed) ??
        timestampMs(stateObj.last_updated) ??
        Number.NEGATIVE_INFINITY;
      return Math.max(0, now - changedAt);
    })
    .filter((elapsedMs) => elapsedMs !== null);

  if (!checks.length) {
    return { hidden: false, offline: false, useCache: false, remainingMs: null };
  }

  const elapsedMs = Math.max(...checks);
  const hidden = elapsedMs >= hideAfterMs;
  return {
    hidden,
    offline: true,
    useCache: !hidden,
    remainingMs: hidden ? null : hideAfterMs - elapsedMs,
  };
};

const historyState = (entry) => entry?.state ?? entry?.s;
const historyAttributes = (entry) => entry?.attributes ?? entry?.a ?? {};

const historyTime = (entry) => {
  const raw =
    entry?.last_changed ??
    entry?.lc ??
    entry?.last_updated ??
    entry?.lu;
  if (typeof raw === "number") {
    return raw * 1000;
  }
  const timestamp = Date.parse(raw);
  return Number.isFinite(timestamp) ? timestamp : null;
};

const numericHistoryPoints = (history, entityId) => {
  const rows = Array.isArray(history?.[entityId]) ? history[entityId] : [];
  return rows
    .map((entry) => ({
      time: historyTime(entry),
      value: Number(historyState(entry)),
      unit: historyAttributes(entry)?.unit_of_measurement,
    }))
    .filter((point) => Number.isFinite(point.time) && Number.isFinite(point.value))
    .sort((a, b) => a.time - b.time);
};

const stateHistoryPoints = (history, entityId) => {
  const rows = Array.isArray(history?.[entityId]) ? history[entityId] : [];
  return rows
    .map((entry) => ({
      time: historyTime(entry),
      state: historyState(entry),
    }))
    .filter((point) => Number.isFinite(point.time))
    .sort((a, b) => a.time - b.time);
};

const downsamplePoints = (points, maxPoints = 180) => {
  if (points.length <= maxPoints) {
    return points;
  }
  const bucketSize = Math.ceil(points.length / maxPoints);
  const sampled = [];
  for (let index = 0; index < points.length; index += bucketSize) {
    const bucket = points.slice(index, index + bucketSize);
    const value =
      bucket.reduce((total, point) => total + point.value, 0) / bucket.length;
    sampled.push({
      time: bucket[Math.floor(bucket.length / 2)].time,
      value,
      unit: bucket[0].unit,
    });
  }
  return sampled;
};

const formatTemperature = (value, fallback = "--") =>
  Number.isFinite(value) ? `${Math.round(value)}\u00b0C` : fallback;

const formatHours = (hours) => {
  if (hours < 24) {
    return `${hours}h`;
  }
  const days = hours / 24;
  return Number.isInteger(days) ? `${days}d` : `${hours}h`;
};

const formatDuration = (minutes) => {
  if (!Number.isFinite(minutes) || minutes <= 0) {
    return "0m";
  }
  const rounded = Math.round(minutes);
  const hours = Math.floor(rounded / 60);
  const mins = rounded % 60;
  if (!hours) {
    return `${mins}m`;
  }
  return mins ? `${hours}h ${mins}m` : `${hours}h`;
};

const formatClock = (timestamp) => {
  if (!Number.isFinite(timestamp)) {
    return "--";
  }
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp));
};

const formatDateTime = (timestamp) => {
  if (!Number.isFinite(timestamp)) {
    return "--";
  }
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp));
};

class AsmokeSmokerCard extends HTMLElement {
  static getStubConfig(hass) {
    const climate = resolveAsmokeClimate(hass, {});
    return climate ? { climate } : {};
  }

  static getConfigElement() {
    return document.createElement(ASMOKE_SMOKER_CARD_EDITOR_TAG);
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._entities = {};
    this._lastEntityStates = new Map();
    this._offlineHide = { hidden: false, offline: false, useCache: false, remainingMs: null };
    this._offlineRefreshTimer = undefined;
    this._handleClick = this._handleClick.bind(this);
  }

  setConfig(config) {
    this._config = {
      hide_offline_data: false,
      offline_hide_after: ASMOKE_DEFAULT_OFFLINE_HIDE_AFTER,
      ...(config ?? {}),
    };
    this._lastEntityStates.clear();
    this._entities = this._buildEntities();
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 6;
  }

  connectedCallback() {
    this._connected = true;
    this.shadowRoot.addEventListener("click", this._handleClick);
    this._render();
  }

  disconnectedCallback() {
    this._connected = false;
    window.clearTimeout(this._offlineRefreshTimer);
    this.shadowRoot.removeEventListener("click", this._handleClick);
  }

  _buildEntities() {
    return buildAsmokeEntities(this._config, this._hass);
  }

  _derivePrefix(entityId) {
    return deriveAsmokePrefix(entityId);
  }

  _state(entityId) {
    return entityId ? this._hass?.states?.[entityId] : undefined;
  }

  _cacheState(entityId, stateObj) {
    if (!entityId || !this._isAvailable(stateObj)) {
      return;
    }
    this._lastEntityStates.set(entityId, {
      ...stateObj,
      attributes: { ...(stateObj.attributes ?? {}) },
    });
  }

  _displayState(entityId) {
    const stateObj = this._state(entityId);
    if (this._isAvailable(stateObj)) {
      this._cacheState(entityId, stateObj);
      return stateObj;
    }
    return this._offlineHide.useCache
      ? this._lastEntityStates.get(entityId) || stateObj
      : stateObj;
  }

  _isAvailable(stateObj) {
    return Boolean(stateObj && !ASMOKE_UNAVAILABLE_STATES.has(stateObj.state));
  }

  _isOn(entityId) {
    return this._state(entityId)?.state === "on";
  }

  _number(entityId) {
    const numeric = Number(this._displayState(entityId)?.state);
    return Number.isFinite(numeric) ? numeric : null;
  }

  _formatValue(entityId, fallback = "--") {
    const stateObj = this._displayState(entityId);
    if (!this._isAvailable(stateObj)) {
      return fallback;
    }
    const unit = stateObj.attributes?.unit_of_measurement ?? "";
    return `${stateObj.state}${unit ? ` ${unit}` : ""}`;
  }

  _formatTemp(entityId) {
    const stateObj = this._displayState(entityId);
    if (!this._isAvailable(stateObj)) {
      return "--";
    }
    const value = Math.round(Number(stateObj.state));
    if (!Number.isFinite(value)) {
      return "--";
    }
    return `${value}${stateObj.attributes?.unit_of_measurement ?? "\u00b0C"}`;
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }

    if (!this._hass) {
      this.shadowRoot.innerHTML = this._styles();
      return;
    }

    this._entities = this._buildEntities();
    if (!this._entities.climate) {
      this._renderEntitySetupHelp(
        "Asmoke smoker card",
        "No Asmoke smoker could be selected automatically. Add a climate entity or choose an Asmoke device in the card editor.",
      );
      return;
    }
    const climate = this._state(this._entities.climate);
    this._offlineHide = offlineHideState(this._config, this._hass, this._entities);
    this._scheduleOfflineHideRefresh();
    const climateDisplay = this._displayState(this._entities.climate) || climate;

    if (!climate) {
      this._renderError(
        "Asmoke smoker card",
        `Entity not found: ${this._entities.climate}`,
      );
      return;
    }

    const currentTemp = firstFinite(
      climateDisplay.attributes?.current_temperature,
      this._number(this._entities.grill_temp_1),
      this._number(this._entities.grill_temp_2),
    );
    const targetTemp = Number(climateDisplay.attributes?.temperature);
    const minTemp = Number(climateDisplay.attributes?.min_temp) || 0;
    const maxTemp = Number(climateDisplay.attributes?.max_temp) || 300;
    const targetDisplay = Number.isFinite(targetTemp)
      ? `${Math.round(targetTemp)}\u00b0C`
      : "--";
    const currentDisplay = Number.isFinite(currentTemp)
      ? `${Math.round(currentTemp)}\u00b0`
      : "--";
    const preset =
      climateDisplay.attributes?.preset_mode ||
      this._displayState(this._entities.mode)?.state;
    const mode = this._formatMode(preset);
    const cookActive = this._isOn(this._entities.cook_active) || climate.state === "heat";
    const brokerConnected = this._isOn(this._entities.broker_connected);
    const deviceOnline = this._isOn(this._entities.device_online);
    const status = this._statusLabel(cookActive, brokerConnected, deviceOnline);
    const statusClass = this._statusClass(cookActive, brokerConnected, deviceOnline);
    const quickTime = this._formatValue(this._entities.quick_time, "-- min");
    const battery = this._formatValue(this._entities.battery);
    const lastResult = this._formatValue(this._entities.last_result, "No result yet");
    const title =
      this._config.name ||
      climateDisplay.attributes?.friendly_name ||
      "Asmoke smoker";

    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="card-shell ${html(statusClass)} ${
          this._offlineHide.hidden ? "hide-offline-data" : ""
        }">
          <header class="header">
            <button class="title-button" data-action="more-info" data-entity="${html(
              this._entities.climate,
            )}">
              <span class="hero-icon"><ha-icon icon="mdi:grill"></ha-icon></span>
              <span class="title-copy">
                <span class="eyebrow">Asmoke</span>
                <span class="title">${html(title)}</span>
              </span>
            </button>
            <span class="status-pill">
              <span class="status-dot"></span>
              ${html(status)}
            </span>
          </header>

          <section class="summary offline-data">
            <button class="temperature-focus" data-action="more-info" data-entity="${html(
              this._entities.climate,
            )}">
              <span class="current-temp">${html(currentDisplay)}</span>
              <span class="current-label">pit temperature</span>
            </button>
            <div class="summary-side">
              <span class="mini-chip strong">
                <ha-icon icon="mdi:bullseye-arrow"></ha-icon>
                ${html(targetDisplay)}
              </span>
              <span class="mini-chip">
                <ha-icon icon="${cookActive ? "mdi:fire" : "mdi:smoke"}"></ha-icon>
                ${html(mode)}
              </span>
            </div>
          </section>

          <section class="control-panel offline-data">
            <div class="stepper">
              <span class="stepper-label">Target</span>
              <button data-action="temp-down" aria-label="Lower target temperature">
                <ha-icon icon="mdi:minus"></ha-icon>
              </button>
              <span class="stepper-value">${html(targetDisplay)}</span>
              <button data-action="temp-up" aria-label="Raise target temperature">
                <ha-icon icon="mdi:plus"></ha-icon>
              </button>
            </div>
            <div class="stepper">
              <span class="stepper-label">Quick</span>
              <button data-action="time-down" aria-label="Lower Quick target time">
                <ha-icon icon="mdi:minus"></ha-icon>
              </button>
              <span class="stepper-value">${html(quickTime)}</span>
              <button data-action="time-up" aria-label="Raise Quick target time">
                <ha-icon icon="mdi:plus"></ha-icon>
              </button>
            </div>
          </section>

          <section class="actions offline-data">
            <button class="action-button start" data-action="start-quick" ${
              brokerConnected ? "" : "disabled"
            }>
              <ha-icon icon="mdi:rocket-launch-outline"></ha-icon>
              <span>Start quick</span>
            </button>
            <button class="action-button stop" data-action="stop-cook" ${
              brokerConnected ? "" : "disabled"
            }>
              <ha-icon icon="mdi:stop-circle-outline"></ha-icon>
              <span>Stop</span>
            </button>
          </section>

          <section class="tiles offline-data">
            ${this._temperatureTile(
              "Grill 1",
              this._entities.grill_temp_1,
              "mdi:grill",
              maxTemp,
              "hot",
            )}
            ${this._temperatureTile(
              "Grill 2",
              this._entities.grill_temp_2,
              "mdi:grill-outline",
              maxTemp,
              "hot",
            )}
            ${this._temperatureTile(
              "Probe A",
              this._entities.probe_a_temp,
              "mdi:thermometer-lines",
              120,
              "probe",
            )}
            ${this._temperatureTile(
              "Probe B",
              this._entities.probe_b_temp,
              "mdi:thermometer-lines",
              120,
              "probe",
            )}
          </section>

          <section class="footer offline-data">
            ${this._statusChip("Broker", brokerConnected, "mdi:access-point-network")}
            ${this._statusChip("Device", deviceOnline, "mdi:wifi")}
            ${this._statusChip("Wi-Fi", this._isOn(this._entities.wifi_connected), "mdi:wifi-check")}
            <button class="footer-chip" data-action="more-info" data-entity="${html(
              this._entities.battery,
            )}">
              <ha-icon icon="mdi:battery-medium"></ha-icon>
              <span>${html(battery)}</span>
            </button>
          </section>

          <button class="result-line offline-data" data-action="more-info" data-entity="${html(
            this._entities.last_result,
          )}">
            <ha-icon icon="mdi:message-text-outline"></ha-icon>
            <span>${html(lastResult)}</span>
          </button>

          <div class="heat-track offline-data" aria-hidden="true">
            <span style="width: ${percent(currentTemp, maxTemp)}%"></span>
          </div>
        </div>
      </ha-card>
    `;

    const track = this.shadowRoot.querySelector(".heat-track span");
    if (track) {
      track.style.width = `${percent(currentTemp, maxTemp)}%`;
    }
    this._setStepperState(minTemp, maxTemp, targetTemp);
  }

  _scheduleOfflineHideRefresh() {
    window.clearTimeout(this._offlineRefreshTimer);
    if (!this._connected || !Number.isFinite(this._offlineHide.remainingMs)) {
      return;
    }
    this._offlineRefreshTimer = window.setTimeout(
      () => this._render(),
      Math.max(250, this._offlineHide.remainingMs + 50),
    );
  }

  _renderError(title, detail) {
    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="card-shell error-state">
          <header class="header">
            <span class="title-button">
              <span class="hero-icon"><ha-icon icon="mdi:alert-circle-outline"></ha-icon></span>
              <span class="title-copy">
                <span class="eyebrow">Configuration</span>
                <span class="title">${html(title)}</span>
              </span>
            </span>
          </header>
          <p class="error-copy">${html(detail)}</p>
        </div>
      </ha-card>
    `;
  }

  _renderEntitySetupHelp(title, detail) {
    const candidates = findAsmokeClimateCandidates(this._hass);
    const candidateText = candidates.length
      ? ` Candidates: ${candidates.join(", ")}.`
      : "";
    this._renderError(title, `${detail}${candidateText}`);
  }

  _temperatureTile(label, entityId, icon, max, tone) {
    const value = this._number(entityId);
    const display = this._formatTemp(entityId);
    const width = percent(value, max);
    const unavailable = value === null ? " unavailable" : "";
    return `
      <button class="tile ${html(tone)}${unavailable}" data-action="more-info" data-entity="${html(
        entityId,
      )}">
        <span class="tile-icon"><ha-icon icon="${html(icon)}"></ha-icon></span>
        <span class="tile-copy">
          <span class="tile-label">${html(label)}</span>
          <span class="tile-value">${html(display)}</span>
        </span>
        <span class="tile-meter" aria-hidden="true"><span style="width: ${width}%"></span></span>
      </button>
    `;
  }

  _statusChip(label, active, icon) {
    return `
      <span class="footer-chip ${active ? "active" : "inactive"}">
        <ha-icon icon="${html(icon)}"></ha-icon>
        <span>${html(label)}</span>
      </span>
    `;
  }

  _statusLabel(cookActive, brokerConnected, deviceOnline) {
    if (!brokerConnected) {
      return "Broker offline";
    }
    if (!deviceOnline) {
      return "Device offline";
    }
    if (cookActive) {
      return "Cooking";
    }
    return "Idle";
  }

  _statusClass(cookActive, brokerConnected, deviceOnline) {
    if (!brokerConnected || !deviceOnline) {
      return "offline";
    }
    if (cookActive) {
      return "cooking";
    }
    return "idle";
  }

  _formatMode(value) {
    if (!value || ASMOKE_UNAVAILABLE_STATES.has(value)) {
      return "Ready";
    }
    return String(value).toLowerCase().replace(/^\w/, (char) => char.toUpperCase());
  }

  _setStepperState(minTemp, maxTemp, targetTemp) {
    const canLower = Number.isFinite(targetTemp) && targetTemp > minTemp;
    const canRaise = Number.isFinite(targetTemp) && targetTemp < maxTemp;
    this._setDisabled("temp-down", !canLower);
    this._setDisabled("temp-up", !canRaise);
    this._setDisabled("time-down", this._number(this._entities.quick_time) === null);
    this._setDisabled("time-up", this._number(this._entities.quick_time) === null);
  }

  _setDisabled(action, disabled) {
    const button = this.shadowRoot.querySelector(`[data-action="${action}"]`);
    if (button) {
      button.disabled = disabled;
    }
  }

  _handleClick(event) {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) {
      return;
    }

    const action = button.dataset.action;
    if (action === "more-info") {
      this._showMoreInfo(button.dataset.entity);
      return;
    }
    if (action === "temp-down") {
      this._setTargetTemperature(-1);
      return;
    }
    if (action === "temp-up") {
      this._setTargetTemperature(1);
      return;
    }
    if (action === "time-down") {
      this._setQuickTime(-5);
      return;
    }
    if (action === "time-up") {
      this._setQuickTime(5);
      return;
    }
    if (action === "start-quick") {
      this._pressButton(this._entities.start_quick);
      return;
    }
    if (action === "stop-cook") {
      this._pressButton(this._entities.stop);
    }
  }

  _showMoreInfo(entityId) {
    if (!entityId) {
      return;
    }
    const event = new CustomEvent("hass-more-info", {
      detail: { entityId },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  _setTargetTemperature(direction) {
    const climate = this._state(this._entities.climate);
    const current = Number(climate?.attributes?.temperature);
    if (!Number.isFinite(current)) {
      return;
    }
    const step = Number(climate.attributes?.target_temp_step) || 10;
    const min = Number(climate.attributes?.min_temp) || 0;
    const max = Number(climate.attributes?.max_temp) || 300;
    const temperature = clamp(current + direction * step, min, max);
    this._hass.callService("climate", "set_temperature", {
      entity_id: this._entities.climate,
      temperature,
    });
  }

  _setQuickTime(delta) {
    const current = this._number(this._entities.quick_time);
    if (current === null) {
      return;
    }
    this._hass.callService("number", "set_value", {
      entity_id: this._entities.quick_time,
      value: Math.max(0, current + delta),
    });
  }

  _pressButton(entityId) {
    if (!entityId) {
      return;
    }
    this._hass.callService("button", "press", {
      entity_id: entityId,
    });
  }

  _styles() {
    return `
      <style>
        :host {
          display: block;
          --asmoke-accent: var(--primary-color, #03a9f4);
          --asmoke-hot: #ff6b2c;
          --asmoke-amber: #ffb300;
          --asmoke-green: #43a047;
          --asmoke-muted: var(--secondary-text-color, #727272);
          --asmoke-tile-bg: color-mix(in srgb, var(--primary-text-color) 5%, transparent);
          --asmoke-soft-accent: color-mix(in srgb, var(--asmoke-accent) 15%, transparent);
          --asmoke-soft-hot: color-mix(in srgb, var(--asmoke-hot) 16%, transparent);
          --asmoke-soft-amber: color-mix(in srgb, var(--asmoke-amber) 18%, transparent);
          --asmoke-soft-green: color-mix(in srgb, var(--asmoke-green) 16%, transparent);
        }

        ha-card {
          overflow: hidden;
          border-radius: var(--ha-card-border-radius, 24px);
          background: var(--ha-card-background, var(--card-background-color, #fff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
          box-shadow: var(--ha-card-box-shadow, 0 2px 10px rgba(0, 0, 0, 0.08));
          color: var(--primary-text-color, #1f1f1f);
        }

        button {
          color: inherit;
          font: inherit;
          letter-spacing: 0;
        }

        button:focus-visible {
          outline: 2px solid var(--asmoke-accent);
          outline-offset: 2px;
        }

        .card-shell {
          position: relative;
          display: grid;
          gap: 16px;
          padding: 18px;
        }

        .header,
        .summary,
        .actions,
        .footer {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header {
          justify-content: space-between;
        }

        .title-button,
        .temperature-focus,
        .tile,
        .result-line {
          appearance: none;
          background: none;
          border: 0;
          padding: 0;
          text-align: left;
        }

        .title-button {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .hero-icon,
        .tile-icon {
          display: inline-grid;
          place-items: center;
          border-radius: 18px;
        }

        .hero-icon {
          width: 50px;
          height: 50px;
          flex: 0 0 50px;
          color: var(--asmoke-hot);
          background: var(--asmoke-soft-hot);
        }

        .title-copy,
        .tile-copy {
          min-width: 0;
          display: grid;
          gap: 2px;
        }

        .eyebrow {
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 600;
          line-height: 1.2;
        }

        .title {
          overflow: hidden;
          font-size: 18px;
          font-weight: 700;
          line-height: 1.2;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .status-pill,
        .mini-chip,
        .footer-chip {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          min-height: 34px;
          border-radius: 999px;
          box-sizing: border-box;
          white-space: nowrap;
        }

        .status-pill {
          flex: 0 0 auto;
          padding: 0 12px;
          color: var(--asmoke-muted);
          background: var(--asmoke-tile-bg);
          font-size: 13px;
          font-weight: 700;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 999px;
          background: var(--asmoke-green);
        }

        .offline .status-dot {
          background: var(--error-color, #d93025);
        }

        .hide-offline-data .offline-data {
          visibility: hidden;
          pointer-events: none;
        }

        .cooking .status-dot {
          background: var(--asmoke-hot);
          box-shadow: 0 0 0 5px var(--asmoke-soft-hot);
        }

        .summary {
          justify-content: space-between;
          align-items: flex-end;
        }

        .temperature-focus {
          display: grid;
          gap: 2px;
        }

        .current-temp {
          font-size: 48px;
          font-weight: 800;
          line-height: 0.95;
        }

        .current-label {
          color: var(--asmoke-muted);
          font-size: 13px;
          font-weight: 600;
        }

        .summary-side {
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: 8px;
        }

        .mini-chip {
          padding: 0 11px;
          background: var(--asmoke-tile-bg);
          color: var(--asmoke-muted);
          font-size: 13px;
          font-weight: 700;
        }

        .mini-chip.strong {
          background: var(--asmoke-soft-hot);
          color: var(--asmoke-hot);
        }

        .mini-chip ha-icon,
        .footer-chip ha-icon {
          --mdc-icon-size: 18px;
        }

        .control-panel {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }

        .stepper {
          display: grid;
          grid-template-columns: auto 36px minmax(54px, 1fr) 36px;
          align-items: center;
          gap: 6px;
          min-height: 48px;
          padding: 6px;
          border-radius: 20px;
          background: var(--asmoke-tile-bg);
        }

        .stepper-label {
          padding-left: 8px;
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 700;
        }

        .stepper-value {
          min-width: 0;
          text-align: center;
          font-size: 14px;
          font-weight: 800;
        }

        .stepper button {
          width: 36px;
          height: 36px;
          border: 0;
          border-radius: 14px;
          background: var(--ha-card-background, var(--card-background-color, #fff));
          box-shadow: inset 0 0 0 1px var(--divider-color, rgba(0, 0, 0, 0.12));
        }

        .stepper button:disabled,
        .action-button:disabled {
          cursor: not-allowed;
          opacity: 0.45;
        }

        .actions {
          display: grid;
          grid-template-columns: 1fr 1fr;
        }

        .action-button {
          min-height: 48px;
          border: 0;
          border-radius: 18px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 9px;
          font-weight: 800;
        }

        .action-button ha-icon {
          --mdc-icon-size: 20px;
        }

        .action-button.start {
          color: #fff;
          background: linear-gradient(135deg, var(--asmoke-hot), var(--asmoke-amber));
        }

        .action-button.stop {
          color: var(--error-color, #d93025);
          background: color-mix(in srgb, var(--error-color, #d93025) 13%, transparent);
        }

        .tiles {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }

        .tile {
          position: relative;
          min-width: 0;
          min-height: 82px;
          display: grid;
          grid-template-columns: 42px minmax(0, 1fr);
          align-items: center;
          gap: 10px;
          padding: 12px;
          border-radius: 20px;
          background: var(--asmoke-tile-bg);
          box-sizing: border-box;
          overflow: hidden;
        }

        .tile-icon {
          width: 42px;
          height: 42px;
          background: var(--asmoke-soft-accent);
          color: var(--asmoke-accent);
        }

        .tile.hot .tile-icon {
          color: var(--asmoke-hot);
          background: var(--asmoke-soft-hot);
        }

        .tile.probe .tile-icon {
          color: var(--asmoke-amber);
          background: var(--asmoke-soft-amber);
        }

        .tile.unavailable .tile-icon,
        .tile.unavailable .tile-value {
          color: var(--disabled-text-color, #9e9e9e);
        }

        .tile-label {
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 700;
        }

        .tile-value {
          overflow: hidden;
          font-size: 22px;
          font-weight: 800;
          line-height: 1.15;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .tile-meter {
          position: absolute;
          left: 12px;
          right: 12px;
          bottom: 9px;
          height: 5px;
          overflow: hidden;
          border-radius: 999px;
          background: color-mix(in srgb, var(--primary-text-color) 9%, transparent);
        }

        .tile-meter span,
        .heat-track span {
          display: block;
          height: 100%;
          border-radius: inherit;
          background: linear-gradient(90deg, var(--asmoke-hot), var(--asmoke-amber));
        }

        .footer {
          flex-wrap: wrap;
          gap: 8px;
        }

        .footer-chip {
          min-width: 0;
          border: 0;
          padding: 0 10px;
          background: var(--asmoke-tile-bg);
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 700;
        }

        .footer-chip.active {
          color: var(--asmoke-green);
          background: var(--asmoke-soft-green);
        }

        .footer-chip.inactive {
          color: var(--asmoke-muted);
        }

        .result-line {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 600;
        }

        .result-line span {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .result-line ha-icon {
          --mdc-icon-size: 17px;
          flex: 0 0 auto;
        }

        .heat-track {
          height: 7px;
          overflow: hidden;
          border-radius: 999px;
          background: color-mix(in srgb, var(--primary-text-color) 7%, transparent);
        }

        .error-copy {
          margin: 0;
          color: var(--asmoke-muted);
          font-size: 14px;
        }

        @media (max-width: 520px) {
          .card-shell {
            padding: 16px;
          }

          .header,
          .summary {
            align-items: flex-start;
          }

          .status-pill {
            max-width: 44%;
            white-space: normal;
          }

          .current-temp {
            font-size: 42px;
          }

          .control-panel,
          .tiles,
          .actions {
            grid-template-columns: 1fr;
          }

          .stepper {
            grid-template-columns: minmax(56px, auto) 36px minmax(64px, 1fr) 36px;
          }
        }
      </style>
    `;
  }
}

class AsmokeSmokerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const form = this.shadowRoot.querySelector("ha-form");
    if (form) {
      form.hass = hass;
      return;
    }
    this._render();
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: 12px 0;
        }
      </style>
      <div id="form"></div>
    `;

    const form = document.createElement("ha-form");
    form.hass = this._hass;
    form.data = this._config;
    form.schema = [
      { name: "name", selector: { text: {} } },
      {
        name: "device_id",
        selector: { device: { integration: "asmoke_cloud" } },
      },
      {
        name: "climate",
        selector: { entity: { domain: "climate" } },
      },
      { name: "quick_time", selector: { entity: { domain: "number" } } },
      { name: "start_quick", selector: { entity: { domain: "button" } } },
      { name: "stop", selector: { entity: { domain: "button" } } },
      { name: "cook_active", selector: { entity: { domain: "binary_sensor" } } },
      { name: "device_online", selector: { entity: { domain: "binary_sensor" } } },
      { name: "broker_connected", selector: { entity: { domain: "binary_sensor" } } },
      { name: "hide_offline_data", selector: { boolean: {} } },
      {
        name: "offline_hide_after",
        selector: {
          number: {
            min: 0,
            step: 30,
            mode: "box",
            unit_of_measurement: "s",
          },
        },
      },
    ];
    form.computeLabel = (schema) => ASMOKE_EDITOR_LABELS[schema.name] ?? schema.name;
    form.addEventListener("value-changed", (event) => {
      this._config = event.detail.value;
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: this._config },
          bubbles: true,
          composed: true,
        }),
      );
    });

    this.shadowRoot.getElementById("form").replaceChildren(form);
  }
}

class AsmokeSmokerHistoryCard extends HTMLElement {
  static getStubConfig(hass) {
    return {
      ...AsmokeSmokerCard.getStubConfig(hass),
      hours_to_show: 6,
    };
  }

  static getConfigElement() {
    return document.createElement(ASMOKE_HISTORY_CARD_EDITOR_TAG);
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._entities = {};
    this._history = {};
    this._error = "";
    this._loading = false;
    this._lastFetchAt = 0;
    this._refreshTimer = undefined;
    this._handleClick = this._handleClick.bind(this);
  }

  setConfig(config) {
    this._config = {
      hours_to_show: 6,
      refresh_interval: 300,
      ...(config ?? {}),
    };
    this._entities = buildAsmokeEntities(this._config, this._hass);
    this._history = {};
    this._lastFetchAt = 0;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
    this._maybeLoadHistory();
  }

  connectedCallback() {
    this._connected = true;
    this.shadowRoot.addEventListener("click", this._handleClick);
    this._render();
    this._maybeLoadHistory();
    if (this._lastFetchAt) {
      this._scheduleRefresh();
    }
  }

  disconnectedCallback() {
    this._connected = false;
    this.shadowRoot.removeEventListener("click", this._handleClick);
    window.clearTimeout(this._refreshTimer);
  }

  getCardSize() {
    return 5;
  }

  _hoursToShow() {
    return Math.max(1, Number(this._config.hours_to_show) || 6);
  }

  _refreshMs() {
    return Math.max(60, Number(this._config.refresh_interval) || 300) * 1000;
  }

  _historyEntities() {
    return [
      this._entities.grill_temp_1,
      this._entities.grill_temp_2,
      this._entities.probe_a_temp,
      this._entities.probe_b_temp,
    ].filter(Boolean);
  }

  _maybeLoadHistory(force = false) {
    this._entities = buildAsmokeEntities(this._config, this._hass);
    if (!this._hass || !this._entities.climate || this._loading) {
      return;
    }
    if (!force && Date.now() - this._lastFetchAt < this._refreshMs()) {
      return;
    }
    this._loadHistory();
  }

  async _loadHistory() {
    if (typeof this._hass?.callWS !== "function") {
      this._error = "Home Assistant history is not available in this view.";
      this._render();
      return;
    }

    window.clearTimeout(this._refreshTimer);
    this._loading = true;
    this._error = "";
    this._render();

    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - this._hoursToShow() * 3600 * 1000);

    try {
      this._history = await this._hass.callWS({
        type: "history/history_during_period",
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        entity_ids: this._historyEntities(),
        include_start_time_state: true,
        significant_changes_only: false,
        minimal_response: false,
        no_attributes: false,
      });
      this._lastFetchAt = Date.now();
    } catch (error) {
      this._error = error?.message || "Could not load Home Assistant history.";
    } finally {
      this._loading = false;
      this._render();
      this._scheduleRefresh();
    }
  }

  _scheduleRefresh() {
    window.clearTimeout(this._refreshTimer);
    if (!this._connected) {
      return;
    }
    this._refreshTimer = window.setTimeout(
      () => this._maybeLoadHistory(true),
      this._refreshMs(),
    );
  }

  _series() {
    return [
      {
        key: "grill1",
        label: "Grill 1",
        entity: this._entities.grill_temp_1,
        color: "#ff6b2c",
      },
      {
        key: "grill2",
        label: "Grill 2",
        entity: this._entities.grill_temp_2,
        color: "#ffb300",
      },
      {
        key: "probeA",
        label: "Probe A",
        entity: this._entities.probe_a_temp,
        color: "#00a6a6",
      },
      {
        key: "probeB",
        label: "Probe B",
        entity: this._entities.probe_b_temp,
        color: "#8e5ad7",
      },
    ].map((series) => ({
      ...series,
      points: downsamplePoints(numericHistoryPoints(this._history, series.entity)),
    }));
  }

  _stateNumber(entityId) {
    const numeric = Number(this._hass?.states?.[entityId]?.state);
    return Number.isFinite(numeric) ? numeric : null;
  }

  _summary(series) {
    const pitPoints = series
      .filter((item) => item.key === "grill1" || item.key === "grill2")
      .flatMap((item) => item.points);
    const probePoints = series
      .filter((item) => item.key === "probeA" || item.key === "probeB")
      .flatMap((item) => item.points);
    const allPoints = [...pitPoints, ...probePoints];
    const pitNow = firstFinite(
      this._hass?.states?.[this._entities.climate]?.attributes?.current_temperature,
      this._stateNumber(this._entities.grill_temp_1),
      this._stateNumber(this._entities.grill_temp_2),
    );
    const target = Number(
      this._hass?.states?.[this._entities.climate]?.attributes?.temperature,
    );

    const average = pitPoints.length
      ? pitPoints.reduce((total, point) => total + point.value, 0) / pitPoints.length
      : null;
    const peak = allPoints.length
      ? Math.max(...allPoints.map((point) => point.value))
      : null;
    const probePeak = probePoints.length
      ? Math.max(...probePoints.map((point) => point.value))
      : null;
    const lastQuarter = pitPoints.slice(Math.floor(pitPoints.length * 0.75));
    const spread = lastQuarter.length
      ? Math.max(...lastQuarter.map((point) => point.value)) -
        Math.min(...lastQuarter.map((point) => point.value))
      : null;

    return {
      pitNow,
      target: Number.isFinite(target) ? target : null,
      average,
      peak,
      probePeak,
      spread,
      samples: allPoints.length,
    };
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }
    this._entities = buildAsmokeEntities(this._config, this._hass);

    if (!this._hass) {
      this.shadowRoot.innerHTML = this._styles();
      return;
    }

    if (!this._entities.climate) {
      this._renderEntitySetupHelp(
        "Asmoke temperature history",
        "No Asmoke smoker could be selected automatically. Add a climate entity or choose an Asmoke device in the card editor.",
      );
      return;
    }

    const series = this._series();
    const summary = this._summary(series);
    const title = this._config.name || "Temperature history";
    const hoursLabel = formatHours(this._hoursToShow());

    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="history-shell">
          <header class="history-header">
            <button class="history-title" data-action="more-info" data-entity="${html(
              this._entities.climate,
            )}">
              <span class="history-icon"><ha-icon icon="mdi:chart-bell-curve-cumulative"></ha-icon></span>
              <span class="history-copy">
                <span class="history-eyebrow">BBQ history</span>
                <span class="history-heading">${html(title)}</span>
              </span>
            </button>
            <span class="history-pill">
              <ha-icon icon="mdi:clock-outline"></ha-icon>
              ${html(hoursLabel)}
            </span>
          </header>

          <section class="metric-grid">
            ${this._metricTile("Pit now", formatTemperature(summary.pitNow), "mdi:grill")}
            ${this._metricTile("Target", formatTemperature(summary.target), "mdi:bullseye-arrow")}
            ${this._metricTile("Pit avg", formatTemperature(summary.average), "mdi:waves-arrow-up")}
            ${this._metricTile("Peak", formatTemperature(summary.peak), "mdi:fire-alert")}
          </section>

          <section class="chart-card">
            ${this._chart(series, summary.target)}
          </section>

          <section class="history-footer">
            <span class="footer-chip">
              <ha-icon icon="mdi:thermometer-lines"></ha-icon>
              Probe peak ${html(formatTemperature(summary.probePeak))}
            </span>
            <span class="footer-chip">
              <ha-icon icon="mdi:approximately-equal"></ha-icon>
              Last spread ${html(formatTemperature(summary.spread))}
            </span>
            <button class="footer-chip clickable" data-action="refresh">
              <ha-icon icon="${this._loading ? "mdi:loading" : "mdi:refresh"}"></ha-icon>
              ${this._loading ? "Loading" : "Refresh"}
            </button>
          </section>

          ${this._error ? `<p class="history-error">${html(this._error)}</p>` : ""}
        </div>
      </ha-card>
    `;
  }

  _metricTile(label, value, icon) {
    return `
      <span class="metric-tile">
        <span class="metric-icon"><ha-icon icon="${html(icon)}"></ha-icon></span>
        <span class="metric-copy">
          <span class="metric-label">${html(label)}</span>
          <span class="metric-value">${html(value)}</span>
        </span>
      </span>
    `;
  }

  _chart(series, target) {
    const width = 320;
    const height = 172;
    const padX = 24;
    const padTop = 16;
    const padBottom = 28;
    const plotWidth = width - padX * 2;
    const plotHeight = height - padTop - padBottom;
    const end = Date.now();
    const start = end - this._hoursToShow() * 3600 * 1000;
    const values = series.flatMap((item) => item.points.map((point) => point.value));

    if (!values.length) {
      return `
        <div class="empty-chart">
          <ha-icon icon="mdi:chart-line"></ha-icon>
          <span>No temperature history yet</span>
        </div>
      `;
    }

    const configuredMin = Number(this._config.min_temp);
    const configuredMax = Number(this._config.max_temp);
    const minValue = Number.isFinite(configuredMin)
      ? configuredMin
      : Math.max(0, Math.floor(Math.min(...values) / 10) * 10 - 10);
    const maxValue = Number.isFinite(configuredMax)
      ? configuredMax
      : Math.ceil(Math.max(...values, target || 0) / 10) * 10 + 10;
    const range = Math.max(1, maxValue - minValue);
    const xFor = (time) =>
      padX + clamp((time - start) / Math.max(1, end - start), 0, 1) * plotWidth;
    const yFor = (value) =>
      padTop + (1 - clamp((value - minValue) / range, 0, 1)) * plotHeight;
    const gridValues = [0, 0.25, 0.5, 0.75, 1].map(
      (step) => minValue + range * step,
    );
    const grid = gridValues
      .map((value) => {
        const y = yFor(value);
        return `
          <line x1="${padX}" y1="${y}" x2="${width - padX}" y2="${y}" class="grid-line"></line>
          <text x="2" y="${y + 4}" class="axis-label">${html(Math.round(value))}</text>
        `;
      })
      .join("");
    const targetY =
      Number.isFinite(target) && target >= minValue && target <= maxValue
        ? yFor(target)
        : null;
    const paths = series
      .filter((item) => item.points.length > 1)
      .map((item) => {
        const d = item.points
          .map((point, index) => {
            const command = index === 0 ? "M" : "L";
            return `${command}${xFor(point.time).toFixed(1)},${yFor(point.value).toFixed(1)}`;
          })
          .join(" ");
        return `<path d="${d}" stroke="${html(item.color)}" class="series-line"></path>`;
      })
      .join("");
    const legend = series
      .filter((item) => item.points.length)
      .map(
        (item) => `
          <span class="legend-item">
            <span style="background: ${html(item.color)}"></span>
            ${html(item.label)}
          </span>
        `,
      )
      .join("");

    return `
      <svg class="history-chart" viewBox="0 0 ${width} ${height}" role="img">
        <rect x="${padX}" y="${padTop}" width="${plotWidth}" height="${plotHeight}" class="plot-bg"></rect>
        ${grid}
        ${
          targetY === null
            ? ""
            : `<line x1="${padX}" y1="${targetY}" x2="${width - padX}" y2="${targetY}" class="target-line"></line>`
        }
        ${paths}
        <text x="${padX}" y="${height - 6}" class="time-label">${html(formatClock(start))}</text>
        <text x="${width - padX}" y="${height - 6}" class="time-label end">${html(formatClock(end))}</text>
      </svg>
      <div class="legend">${legend}</div>
    `;
  }

  _handleClick(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) {
      return;
    }
    if (button.dataset.action === "refresh") {
      this._maybeLoadHistory(true);
      return;
    }
    if (button.dataset.action === "more-info") {
      this.dispatchEvent(
        new CustomEvent("hass-more-info", {
          detail: { entityId: button.dataset.entity },
          bubbles: true,
          composed: true,
        }),
      );
    }
  }

  _renderEntitySetupHelp(title, detail) {
    const candidates = findAsmokeClimateCandidates(this._hass);
    const candidateText = candidates.length
      ? ` Candidates: ${candidates.join(", ")}.`
      : "";
    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="history-shell">
          <header class="history-header">
            <span class="history-title">
              <span class="history-icon"><ha-icon icon="mdi:alert-circle-outline"></ha-icon></span>
              <span class="history-copy">
                <span class="history-eyebrow">Configuration</span>
                <span class="history-heading">${html(title)}</span>
              </span>
            </span>
          </header>
          <p class="history-error">${html(`${detail}${candidateText}`)}</p>
        </div>
      </ha-card>
    `;
  }

  _styles() {
    return `
      <style>
        :host {
          display: block;
          --asmoke-hot: #ff6b2c;
          --asmoke-amber: #ffb300;
          --asmoke-teal: #00a6a6;
          --asmoke-purple: #8e5ad7;
          --asmoke-muted: var(--secondary-text-color, #727272);
          --asmoke-surface: color-mix(in srgb, var(--primary-text-color) 5%, transparent);
          --asmoke-soft-hot: color-mix(in srgb, var(--asmoke-hot) 16%, transparent);
        }

        ha-card {
          overflow: hidden;
          border-radius: var(--ha-card-border-radius, 24px);
          background: var(--ha-card-background, var(--card-background-color, #fff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
          box-shadow: var(--ha-card-box-shadow, 0 2px 10px rgba(0, 0, 0, 0.08));
          color: var(--primary-text-color, #1f1f1f);
        }

        button {
          color: inherit;
          font: inherit;
          letter-spacing: 0;
        }

        button:focus-visible {
          outline: 2px solid var(--primary-color, #03a9f4);
          outline-offset: 2px;
        }

        .history-shell {
          display: grid;
          gap: 14px;
          padding: 18px;
        }

        .history-header,
        .history-title,
        .history-footer,
        .history-pill,
        .footer-chip,
        .legend,
        .legend-item {
          display: flex;
          align-items: center;
        }

        .history-header {
          justify-content: space-between;
          gap: 12px;
        }

        .history-title,
        .footer-chip.clickable {
          appearance: none;
          background: none;
          border: 0;
          padding: 0;
          text-align: left;
        }

        .history-title {
          min-width: 0;
          gap: 12px;
        }

        .history-icon,
        .metric-icon {
          display: inline-grid;
          place-items: center;
          border-radius: 18px;
          color: var(--asmoke-hot);
          background: var(--asmoke-soft-hot);
        }

        .history-icon {
          width: 48px;
          height: 48px;
          flex: 0 0 48px;
        }

        .history-copy,
        .metric-copy {
          min-width: 0;
          display: grid;
          gap: 2px;
        }

        .history-eyebrow,
        .metric-label {
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 700;
          line-height: 1.2;
        }

        .history-heading {
          overflow: hidden;
          font-size: 18px;
          font-weight: 800;
          line-height: 1.2;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .history-pill,
        .footer-chip {
          gap: 7px;
          min-height: 34px;
          padding: 0 11px;
          border-radius: 999px;
          background: var(--asmoke-surface);
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 800;
          white-space: nowrap;
        }

        .history-pill ha-icon,
        .footer-chip ha-icon {
          --mdc-icon-size: 17px;
        }

        .metric-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 10px;
        }

        .metric-tile {
          min-width: 0;
          min-height: 68px;
          display: grid;
          grid-template-columns: 38px minmax(0, 1fr);
          align-items: center;
          gap: 9px;
          padding: 10px;
          border-radius: 18px;
          background: var(--asmoke-surface);
        }

        .metric-icon {
          width: 38px;
          height: 38px;
        }

        .metric-value {
          overflow: hidden;
          font-size: 18px;
          font-weight: 850;
          line-height: 1.15;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .chart-card {
          min-height: 224px;
          padding: 10px;
          border-radius: 22px;
          background: linear-gradient(
            180deg,
            color-mix(in srgb, var(--asmoke-hot) 7%, transparent),
            var(--asmoke-surface)
          );
        }

        .history-chart {
          width: 100%;
          min-height: 172px;
          overflow: visible;
        }

        .plot-bg {
          fill: color-mix(in srgb, var(--primary-text-color) 3%, transparent);
          rx: 14px;
        }

        .grid-line {
          stroke: color-mix(in srgb, var(--primary-text-color) 12%, transparent);
          stroke-width: 1;
        }

        .series-line {
          fill: none;
          stroke-linecap: round;
          stroke-linejoin: round;
          stroke-width: 3.4;
          filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.14));
        }

        .target-line {
          stroke: var(--primary-color, #03a9f4);
          stroke-dasharray: 6 5;
          stroke-width: 2;
        }

        .axis-label,
        .time-label {
          fill: var(--asmoke-muted);
          font-size: 10px;
          font-weight: 700;
        }

        .time-label.end {
          text-anchor: end;
        }

        .legend {
          flex-wrap: wrap;
          gap: 8px;
          padding: 4px 2px 0;
        }

        .legend-item {
          gap: 6px;
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 800;
        }

        .legend-item span {
          width: 9px;
          height: 9px;
          border-radius: 999px;
        }

        .history-footer {
          flex-wrap: wrap;
          gap: 8px;
        }

        .history-error {
          margin: 0;
          color: var(--error-color, #d93025);
          font-size: 13px;
          font-weight: 700;
        }

        .empty-chart {
          min-height: 202px;
          display: grid;
          place-items: center;
          align-content: center;
          gap: 8px;
          color: var(--asmoke-muted);
          font-weight: 800;
        }

        .empty-chart ha-icon {
          --mdc-icon-size: 34px;
        }

        @media (max-width: 560px) {
          .history-shell {
            padding: 16px;
          }

          .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }

          .history-header {
            align-items: flex-start;
          }
        }
      </style>
    `;
  }
}

class AsmokeSmokerSessionCard extends HTMLElement {
  static getStubConfig(hass) {
    return {
      ...AsmokeSmokerCard.getStubConfig(hass),
      hours_to_show: 24,
    };
  }

  static getConfigElement() {
    return document.createElement(ASMOKE_SESSION_CARD_EDITOR_TAG);
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._entities = {};
    this._history = {};
    this._error = "";
    this._loading = false;
    this._lastFetchAt = 0;
    this._refreshTimer = undefined;
    this._handleClick = this._handleClick.bind(this);
  }

  setConfig(config) {
    this._config = {
      hours_to_show: 24,
      refresh_interval: 300,
      ...(config ?? {}),
    };
    this._entities = buildAsmokeEntities(this._config, this._hass);
    this._history = {};
    this._lastFetchAt = 0;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
    this._maybeLoadHistory();
  }

  connectedCallback() {
    this._connected = true;
    this.shadowRoot.addEventListener("click", this._handleClick);
    this._render();
    this._maybeLoadHistory();
    if (this._lastFetchAt) {
      this._scheduleRefresh();
    }
  }

  disconnectedCallback() {
    this._connected = false;
    this.shadowRoot.removeEventListener("click", this._handleClick);
    window.clearTimeout(this._refreshTimer);
  }

  getCardSize() {
    return 4;
  }

  _hoursToShow() {
    return Math.max(1, Number(this._config.hours_to_show) || 24);
  }

  _refreshMs() {
    return Math.max(60, Number(this._config.refresh_interval) || 300) * 1000;
  }

  _historyEntities() {
    return [
      this._entities.cook_active,
      this._entities.mode,
      this._entities.device_online,
    ].filter(Boolean);
  }

  _maybeLoadHistory(force = false) {
    this._entities = buildAsmokeEntities(this._config, this._hass);
    if (!this._hass || !this._entities.climate || this._loading) {
      return;
    }
    if (!force && Date.now() - this._lastFetchAt < this._refreshMs()) {
      return;
    }
    this._loadHistory();
  }

  async _loadHistory() {
    if (typeof this._hass?.callWS !== "function") {
      this._error = "Home Assistant history is not available in this view.";
      this._render();
      return;
    }

    window.clearTimeout(this._refreshTimer);
    this._loading = true;
    this._error = "";
    this._render();

    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - this._hoursToShow() * 3600 * 1000);

    try {
      this._history = await this._hass.callWS({
        type: "history/history_during_period",
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        entity_ids: this._historyEntities(),
        include_start_time_state: true,
        significant_changes_only: false,
        minimal_response: false,
        no_attributes: false,
      });
      this._lastFetchAt = Date.now();
    } catch (error) {
      this._error = error?.message || "Could not load Home Assistant history.";
    } finally {
      this._loading = false;
      this._render();
      this._scheduleRefresh();
    }
  }

  _scheduleRefresh() {
    window.clearTimeout(this._refreshTimer);
    if (!this._connected) {
      return;
    }
    this._refreshTimer = window.setTimeout(
      () => this._maybeLoadHistory(true),
      this._refreshMs(),
    );
  }

  _isOnState(state) {
    return ["on", "true", "running", "heat"].includes(String(state).toLowerCase());
  }

  _sessions() {
    const end = Date.now();
    const start = end - this._hoursToShow() * 3600 * 1000;
    const points = stateHistoryPoints(this._history, this._entities.cook_active);
    let activeStart = null;
    const sessions = [];

    for (const point of points) {
      const isOn = this._isOnState(point.state);
      if (isOn && activeStart === null) {
        activeStart = Math.max(start, point.time);
      }
      if (!isOn && activeStart !== null) {
        sessions.push({
          start: activeStart,
          end: point.time,
          active: false,
        });
        activeStart = null;
      }
    }

    if (activeStart !== null || this._isOnState(this._hass?.states?.[this._entities.cook_active]?.state)) {
      sessions.push({
        start: activeStart ?? start,
        end,
        active: true,
      });
    }

    return sessions.filter((session) => session.end > session.start);
  }

  _summary(sessions) {
    const durations = sessions.map((session) => (session.end - session.start) / 60000);
    const total = durations.reduce((sum, duration) => sum + duration, 0);
    const longest = durations.length ? Math.max(...durations) : 0;
    const current = sessions.find((session) => session.active);
    const last = current || sessions.at(-1);
    const mode =
      this._hass?.states?.[this._entities.mode]?.state ||
      this._hass?.states?.[this._entities.climate]?.attributes?.preset_mode ||
      "Ready";

    return {
      total,
      longest,
      count: sessions.length,
      current,
      last,
      mode,
    };
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }
    this._entities = buildAsmokeEntities(this._config, this._hass);

    if (!this._hass) {
      this.shadowRoot.innerHTML = this._styles();
      return;
    }

    if (!this._entities.climate) {
      this._renderEntitySetupHelp(
        "Asmoke cook sessions",
        "No Asmoke smoker could be selected automatically. Add a climate entity or choose an Asmoke device in the card editor.",
      );
      return;
    }

    const sessions = this._sessions();
    const summary = this._summary(sessions);
    const title = this._config.name || "Cook sessions";
    const hoursLabel = formatHours(this._hoursToShow());

    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="session-shell">
          <header class="session-header">
            <button class="session-title" data-action="more-info" data-entity="${html(
              this._entities.cook_active,
            )}">
              <span class="session-icon"><ha-icon icon="mdi:grill-outline"></ha-icon></span>
              <span class="session-copy">
                <span class="session-eyebrow">BBQ log</span>
                <span class="session-heading">${html(title)}</span>
              </span>
            </button>
            <span class="session-pill">
              <ha-icon icon="mdi:calendar-clock"></ha-icon>
              ${html(hoursLabel)}
            </span>
          </header>

          <section class="session-stats">
            ${this._stat("Runtime", formatDuration(summary.total), "mdi:timer-sand")}
            ${this._stat("Cooks", String(summary.count), "mdi:counter")}
            ${this._stat("Longest", formatDuration(summary.longest), "mdi:clock-plus-outline")}
          </section>

          <section class="timeline-card">
            ${this._timeline(sessions)}
          </section>

          <section class="session-detail">
            <span class="detail-chip active-${Boolean(summary.current)}">
              <ha-icon icon="${summary.current ? "mdi:fire" : "mdi:smoke"}"></ha-icon>
              ${summary.current ? "Cooking now" : "Idle"}
            </span>
            <span class="detail-chip">
              <ha-icon icon="mdi:chef-hat"></ha-icon>
              ${html(String(summary.mode).toLowerCase())}
            </span>
            <button class="detail-chip clickable" data-action="refresh">
              <ha-icon icon="${this._loading ? "mdi:loading" : "mdi:refresh"}"></ha-icon>
              ${this._loading ? "Loading" : "Refresh"}
            </button>
          </section>

          ${this._sessionList(sessions)}
          ${this._error ? `<p class="session-error">${html(this._error)}</p>` : ""}
        </div>
      </ha-card>
    `;
  }

  _stat(label, value, icon) {
    return `
      <span class="stat-tile">
        <ha-icon icon="${html(icon)}"></ha-icon>
        <span>
          <span class="stat-label">${html(label)}</span>
          <span class="stat-value">${html(value)}</span>
        </span>
      </span>
    `;
  }

  _timeline(sessions) {
    const end = Date.now();
    const start = end - this._hoursToShow() * 3600 * 1000;
    const range = Math.max(1, end - start);
    const segments = sessions
      .map((session) => {
        const left = clamp(((session.start - start) / range) * 100, 0, 100);
        const right = clamp(((session.end - start) / range) * 100, 0, 100);
        const width = Math.max(1.5, right - left);
        return `<span class="timeline-segment ${session.active ? "active" : ""}" style="left: ${left}%; width: ${width}%"></span>`;
      })
      .join("");

    return `
      <div class="timeline-track">
        ${segments || '<span class="timeline-empty">No cook sessions in this window</span>'}
      </div>
      <div class="timeline-labels">
        <span>${html(formatClock(start))}</span>
        <span>${html(formatClock(end))}</span>
      </div>
    `;
  }

  _sessionList(sessions) {
    const recent = sessions.slice(-3).reverse();
    if (!recent.length) {
      return "";
    }
    const rows = recent
      .map(
        (session) => `
          <button class="session-row" data-action="more-info" data-entity="${html(
            this._entities.cook_active,
          )}">
            <span class="row-icon"><ha-icon icon="${session.active ? "mdi:fire" : "mdi:check-circle-outline"}"></ha-icon></span>
            <span class="row-copy">
              <span class="row-title">${html(session.active ? "Current cook" : "Cook")}</span>
              <span class="row-subtitle">${html(formatDateTime(session.start))} - ${html(
                session.active ? "now" : formatClock(session.end),
              )}</span>
            </span>
            <span class="row-duration">${html(formatDuration((session.end - session.start) / 60000))}</span>
          </button>
        `,
      )
      .join("");
    return `<section class="session-list">${rows}</section>`;
  }

  _handleClick(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) {
      return;
    }
    if (button.dataset.action === "refresh") {
      this._maybeLoadHistory(true);
      return;
    }
    if (button.dataset.action === "more-info") {
      this.dispatchEvent(
        new CustomEvent("hass-more-info", {
          detail: { entityId: button.dataset.entity },
          bubbles: true,
          composed: true,
        }),
      );
    }
  }

  _renderEntitySetupHelp(title, detail) {
    const candidates = findAsmokeClimateCandidates(this._hass);
    const candidateText = candidates.length
      ? ` Candidates: ${candidates.join(", ")}.`
      : "";
    this.shadowRoot.innerHTML = `
      ${this._styles()}
      <ha-card>
        <div class="session-shell">
          <header class="session-header">
            <span class="session-title">
              <span class="session-icon"><ha-icon icon="mdi:alert-circle-outline"></ha-icon></span>
              <span class="session-copy">
                <span class="session-eyebrow">Configuration</span>
                <span class="session-heading">${html(title)}</span>
              </span>
            </span>
          </header>
          <p class="session-error">${html(`${detail}${candidateText}`)}</p>
        </div>
      </ha-card>
    `;
  }

  _styles() {
    return `
      <style>
        :host {
          display: block;
          --asmoke-hot: #ff6b2c;
          --asmoke-amber: #ffb300;
          --asmoke-green: #43a047;
          --asmoke-muted: var(--secondary-text-color, #727272);
          --asmoke-surface: color-mix(in srgb, var(--primary-text-color) 5%, transparent);
          --asmoke-soft-hot: color-mix(in srgb, var(--asmoke-hot) 16%, transparent);
          --asmoke-soft-green: color-mix(in srgb, var(--asmoke-green) 16%, transparent);
        }

        ha-card {
          overflow: hidden;
          border-radius: var(--ha-card-border-radius, 24px);
          background: var(--ha-card-background, var(--card-background-color, #fff));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
          box-shadow: var(--ha-card-box-shadow, 0 2px 10px rgba(0, 0, 0, 0.08));
          color: var(--primary-text-color, #1f1f1f);
        }

        button {
          color: inherit;
          font: inherit;
          letter-spacing: 0;
        }

        .session-shell {
          display: grid;
          gap: 14px;
          padding: 18px;
        }

        .session-header,
        .session-title,
        .session-pill,
        .session-stats,
        .session-detail,
        .detail-chip,
        .stat-tile,
        .session-row {
          display: flex;
          align-items: center;
        }

        .session-header {
          justify-content: space-between;
          gap: 12px;
        }

        .session-title,
        .detail-chip.clickable,
        .session-row {
          appearance: none;
          background: none;
          border: 0;
          padding: 0;
          text-align: left;
        }

        .session-title {
          min-width: 0;
          gap: 12px;
        }

        .session-icon,
        .row-icon {
          display: inline-grid;
          place-items: center;
          border-radius: 18px;
          color: var(--asmoke-hot);
          background: var(--asmoke-soft-hot);
        }

        .session-icon {
          width: 48px;
          height: 48px;
          flex: 0 0 48px;
        }

        .session-copy,
        .row-copy,
        .stat-tile span {
          min-width: 0;
          display: grid;
          gap: 2px;
        }

        .session-eyebrow,
        .stat-label,
        .row-subtitle {
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 700;
          line-height: 1.2;
        }

        .session-heading {
          overflow: hidden;
          font-size: 18px;
          font-weight: 850;
          line-height: 1.2;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .session-pill,
        .detail-chip {
          gap: 7px;
          min-height: 34px;
          padding: 0 11px;
          border-radius: 999px;
          background: var(--asmoke-surface);
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 850;
          white-space: nowrap;
        }

        .session-pill ha-icon,
        .detail-chip ha-icon {
          --mdc-icon-size: 17px;
        }

        .session-stats {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 10px;
        }

        .stat-tile {
          min-width: 0;
          gap: 9px;
          min-height: 62px;
          padding: 10px;
          border-radius: 18px;
          background: var(--asmoke-surface);
        }

        .stat-tile ha-icon {
          --mdc-icon-size: 24px;
          color: var(--asmoke-hot);
        }

        .stat-value {
          overflow: hidden;
          font-size: 18px;
          font-weight: 850;
          line-height: 1.15;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .timeline-card {
          display: grid;
          gap: 9px;
          padding: 14px;
          border-radius: 22px;
          background: linear-gradient(
            180deg,
            color-mix(in srgb, var(--asmoke-hot) 8%, transparent),
            var(--asmoke-surface)
          );
        }

        .timeline-track {
          position: relative;
          min-height: 52px;
          overflow: hidden;
          border-radius: 18px;
          background: color-mix(in srgb, var(--primary-text-color) 8%, transparent);
        }

        .timeline-segment {
          position: absolute;
          top: 8px;
          bottom: 8px;
          border-radius: 999px;
          background: linear-gradient(90deg, var(--asmoke-hot), var(--asmoke-amber));
          box-shadow: 0 6px 14px rgba(255, 107, 44, 0.24);
        }

        .timeline-segment.active {
          background: linear-gradient(90deg, var(--asmoke-hot), var(--asmoke-green));
        }

        .timeline-empty {
          display: grid;
          min-height: 52px;
          place-items: center;
          color: var(--asmoke-muted);
          font-size: 12px;
          font-weight: 800;
        }

        .timeline-labels {
          display: flex;
          justify-content: space-between;
          color: var(--asmoke-muted);
          font-size: 11px;
          font-weight: 800;
        }

        .session-detail {
          flex-wrap: wrap;
          gap: 8px;
        }

        .detail-chip.active-true {
          color: var(--asmoke-green);
          background: var(--asmoke-soft-green);
        }

        .session-list {
          display: grid;
          gap: 8px;
        }

        .session-row {
          min-width: 0;
          display: grid;
          grid-template-columns: 38px minmax(0, 1fr) auto;
          gap: 10px;
          align-items: center;
          min-height: 58px;
          padding: 10px;
          border-radius: 18px;
          background: var(--asmoke-surface);
        }

        .row-icon {
          width: 38px;
          height: 38px;
        }

        .row-title {
          overflow: hidden;
          font-size: 14px;
          font-weight: 850;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .row-duration {
          color: var(--asmoke-hot);
          font-size: 13px;
          font-weight: 850;
          white-space: nowrap;
        }

        .session-error {
          margin: 0;
          color: var(--error-color, #d93025);
          font-size: 13px;
          font-weight: 700;
        }

        @media (max-width: 560px) {
          .session-shell {
            padding: 16px;
          }

          .session-stats {
            grid-template-columns: 1fr;
          }

          .session-header {
            align-items: flex-start;
          }
        }
      </style>
    `;
  }
}

class AsmokeSmokerHistoryCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const form = this.shadowRoot.querySelector("ha-form");
    if (form) {
      form.hass = hass;
      return;
    }
    this._render();
  }

  _render() {
    this.shadowRoot.innerHTML = `<style>:host{display:block;padding:12px 0;}</style><div id="form"></div>`;
    const form = document.createElement("ha-form");
    form.hass = this._hass;
    form.data = this._config;
    form.schema = [
      { name: "name", selector: { text: {} } },
      { name: "device_id", selector: { device: { integration: "asmoke_cloud" } } },
      { name: "climate", selector: { entity: { domain: "climate" } } },
      { name: "hours_to_show", selector: { number: { min: 1, max: 168, step: 1, mode: "box" } } },
      { name: "refresh_interval", selector: { number: { min: 60, max: 3600, step: 30, mode: "box" } } },
      { name: "grill_temp_1", selector: { entity: { domain: "sensor" } } },
      { name: "grill_temp_2", selector: { entity: { domain: "sensor" } } },
      { name: "probe_a_temp", selector: { entity: { domain: "sensor" } } },
      { name: "probe_b_temp", selector: { entity: { domain: "sensor" } } },
    ];
    form.computeLabel = (schema) => ({
      name: "Name",
      device_id: "Asmoke device",
      climate: "Pit thermostat",
      hours_to_show: "Hours to show",
      refresh_interval: "Refresh interval seconds",
      grill_temp_1: "Grill 1 temperature",
      grill_temp_2: "Grill 2 temperature",
      probe_a_temp: "Probe A temperature",
      probe_b_temp: "Probe B temperature",
    })[schema.name] ?? schema.name;
    form.addEventListener("value-changed", (event) => {
      this._config = event.detail.value;
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: this._config },
          bubbles: true,
          composed: true,
        }),
      );
    });
    this.shadowRoot.getElementById("form").replaceChildren(form);
  }
}

class AsmokeSmokerSessionCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const form = this.shadowRoot.querySelector("ha-form");
    if (form) {
      form.hass = hass;
      return;
    }
    this._render();
  }

  _render() {
    this.shadowRoot.innerHTML = `<style>:host{display:block;padding:12px 0;}</style><div id="form"></div>`;
    const form = document.createElement("ha-form");
    form.hass = this._hass;
    form.data = this._config;
    form.schema = [
      { name: "name", selector: { text: {} } },
      { name: "device_id", selector: { device: { integration: "asmoke_cloud" } } },
      { name: "climate", selector: { entity: { domain: "climate" } } },
      { name: "hours_to_show", selector: { number: { min: 1, max: 336, step: 1, mode: "box" } } },
      { name: "refresh_interval", selector: { number: { min: 60, max: 3600, step: 30, mode: "box" } } },
      { name: "cook_active", selector: { entity: { domain: "binary_sensor" } } },
      { name: "mode", selector: { entity: { domain: "sensor" } } },
      { name: "device_online", selector: { entity: { domain: "binary_sensor" } } },
    ];
    form.computeLabel = (schema) => ({
      name: "Name",
      device_id: "Asmoke device",
      climate: "Pit thermostat",
      hours_to_show: "Hours to show",
      refresh_interval: "Refresh interval seconds",
      cook_active: "Cook active",
      mode: "Mode",
      device_online: "Device online",
    })[schema.name] ?? schema.name;
    form.addEventListener("value-changed", (event) => {
      this._config = event.detail.value;
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: this._config },
          bubbles: true,
          composed: true,
        }),
      );
    });
    this.shadowRoot.getElementById("form").replaceChildren(form);
  }
}

if (!customElements.get(ASMOKE_SMOKER_CARD_EDITOR_TAG)) {
  customElements.define(ASMOKE_SMOKER_CARD_EDITOR_TAG, AsmokeSmokerCardEditor);
}

if (!customElements.get(ASMOKE_SMOKER_CARD_TAG)) {
  customElements.define(ASMOKE_SMOKER_CARD_TAG, AsmokeSmokerCard);
}

if (!customElements.get(ASMOKE_HISTORY_CARD_EDITOR_TAG)) {
  customElements.define(
    ASMOKE_HISTORY_CARD_EDITOR_TAG,
    AsmokeSmokerHistoryCardEditor,
  );
}

if (!customElements.get(ASMOKE_HISTORY_CARD_TAG)) {
  customElements.define(ASMOKE_HISTORY_CARD_TAG, AsmokeSmokerHistoryCard);
}

if (!customElements.get(ASMOKE_SESSION_CARD_EDITOR_TAG)) {
  customElements.define(
    ASMOKE_SESSION_CARD_EDITOR_TAG,
    AsmokeSmokerSessionCardEditor,
  );
}

if (!customElements.get(ASMOKE_SESSION_CARD_TAG)) {
  customElements.define(ASMOKE_SESSION_CARD_TAG, AsmokeSmokerSessionCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === ASMOKE_SMOKER_CARD_TAG)) {
  window.customCards.push({
    type: ASMOKE_SMOKER_CARD_TAG,
    name: "Asmoke Smoker Card",
    description: "Mushroom-style controls and telemetry for Asmoke smokers.",
  });
}
if (!window.customCards.some((card) => card.type === ASMOKE_HISTORY_CARD_TAG)) {
  window.customCards.push({
    type: ASMOKE_HISTORY_CARD_TAG,
    name: "Asmoke Temperature History",
    description: "BBQ-style temperature history for Asmoke grill and probe sensors.",
  });
}
if (!window.customCards.some((card) => card.type === ASMOKE_SESSION_CARD_TAG)) {
  window.customCards.push({
    type: ASMOKE_SESSION_CARD_TAG,
    name: "Asmoke Cook Sessions",
    description: "Cook runtime and session history for Asmoke smokers.",
  });
}

console.info(
  `%cASMOKE-SMOKER-CARD ${ASMOKE_SMOKER_CARD_VERSION}`,
  "color: #ff6b2c; font-weight: 700;",
);
