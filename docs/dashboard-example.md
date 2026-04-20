# Dashboard-voorbeeld

Dit document hoort bij de actuele entityset van de Asmoke-integratie en gebruikt:

- de climate-entity voor smoke en quick;
- `number.quick_target_time` als Quick-invoer;
- `binary_sensor.cook_active` als nette cook-status;
- de huidige button-entities voor `Start quick cook` en `Stop cook`.

## Gebruik

1. Kopieer de YAML uit [docs/dashboard-example.yaml](docs/dashboard-example.yaml).
2. Vervang overal de slug `asmoke_backyard` door de entity-prefix van jouw device.
3. Plak de inhoud in een YAML-dashboard of neem de view op onder `views:` in je bestaande Lovelace-config.

## Wat dit dashboard laat zien

- een centrale pit-bediening via de climate-kaart;
- een aparte Quick target time bediening;
- snelle start- en stopknoppen;
- een statusblok voor broker, device en cook active;
- gauges voor grill- en probe-temperaturen;
- een compacte telemetriekaart;
- een history graph voor de belangrijkste temperaturen.

## Belangrijke noot

Gebruik in dashboards en automations bij voorkeur `binary_sensor...cook_active` voor de vraag of de smoker echt aan of uit is. De losse `sensor...mode` blijft handig als vendor-informatie, maar kan na een stop nog even een oude mode laten zien.