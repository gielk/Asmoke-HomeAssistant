# HACS En Publicatieplan

## Status

Deze repository is inmiddels een publiceerbare HACS `integration` repository. De integratie staat onder `custom_components/asmoke_cloud`, heeft een config flow, tests, een `hacs.json`, semver-versies en GitHub Releases.

## Huidige publicatievorm

- distributievorm: Home Assistant custom integration;
- HACS type: `integration`;
- repositorystatus: publieke GitHub-repo met semver GitHub Releases;
- actuele installatieroute: custom repository in HACS.

De default branch is in HACS verborgen, zodat gebruikers een named release installeren in plaats van een commit-hash.

## Wat HACS hier nu gebruikt

Voor deze repo zijn de relevante bronnen:

- `custom_components/asmoke_cloud/manifest.json` voor de integratieversie;
- `hacs.json` voor HACS metadata;
- GitHub Releases voor zichtbare versienummers in HACS;
- `README.md` en `docs/user-guide.md` voor installatie- en gebruiksinstructies.

Alleen tags zijn hiervoor niet genoeg; HACS kijkt naar gepubliceerde GitHub Releases.

## Releasechecklist

Gebruik voor iedere nieuwe release deze volgorde:

1. Werk code en documentatie bij.
2. Draai `pytest tests/components/asmoke_cloud -q`.
3. Werk `custom_components/asmoke_cloud/manifest.json` bij naar de nieuwe semver-versie.
4. Voeg een nieuwe entry toe aan `CHANGELOG.md`.
5. Commit de releasevoorbereiding.
6. Maak en push een git-tag met dezelfde versie, bijvoorbeeld `v0.3.2`.
7. Maak daarna een GitHub Release voor die tag.

## Huidige validatie

De repo heeft op dit moment:

- componenttests via `pytest-homeassistant-custom-component`;
- een GitHub Actions workflow die `pytest` draait;
- documentatie voor onboarding, local auth, troubleshooting en releasegeschiedenis.

## Logische vervolgstappen

Voor latere iteraties zijn dit de meest logische verbeteringen:

- `hassfest` of extra linting toevoegen aan CI;
- releaseautomatisering toevoegen via GitHub Actions;
- pas daarna bekijken of opname in de HACS default store zinvol is.
