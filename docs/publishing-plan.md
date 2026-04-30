# HACS and Publishing Plan

## Status

This repository is now a publishable HACS `integration` repository. The integration lives under `custom_components/asmoke_cloud`, has a config flow, tests, a `hacs.json`, semantic versions, and GitHub Releases.

## Current publishing model

- distribution model: Home Assistant custom integration;
- HACS type: `integration`;
- repository status: public GitHub repository with semantic version GitHub Releases;
- current installation route: custom repository in HACS.

The default branch is hidden in HACS so users install a named release instead of a commit hash.

## What HACS uses here today

For this repository, the relevant sources are:

- `custom_components/asmoke_cloud/manifest.json` for the integration version;
- `hacs.json` for HACS metadata;
- GitHub Releases for visible version numbers in HACS;
- `README.md` and `docs/user-guide.md` for installation and usage instructions.

Tags alone are not enough here; HACS looks at published GitHub Releases.

## Release checklist

Use this order for every new release:

1. Update code and documentation.
2. Run `pytest tests/components/asmoke_cloud -q`.
3. Update `custom_components/asmoke_cloud/manifest.json` to the new semantic version.
4. Add a new English entry to `CHANGELOG.md`.
5. Write changelog entries from user impact, not from internal commit details.
6. Commit the release preparation.
7. Create and push a git tag with the same version, for example `v0.4.2`.
8. Create a GitHub Release for that tag.

## Current validation

The repository currently has:

- component tests through `pytest-homeassistant-custom-component`;
- a GitHub Actions workflow that runs `pytest`;
- documentation for onboarding, dashboard cards, troubleshooting, and release history.

## Logical next steps

For later iterations, these are the most logical improvements:

- add `hassfest` or extra linting to CI;
- add release automation through GitHub Actions;
- only after that, evaluate whether inclusion in the HACS default store makes sense.
