# Deployment

This repository includes deployment-facing skeletons rather than a project-specific deploy implementation.

## Service Naming

When deploying with `systemd`, keep unit names aligned with the observability conventions described in [OBSERVABILITY.md](OBSERVABILITY.md):
- `{{PROJECT_NAME}}.service`
- `{{PROJECT_NAME}}-<job>.service`
- `{{PROJECT_NAME}}-<job>.timer`

Matching unit names, Syslog identifiers, and Loki labels makes operator workflows simpler.

## Release Metadata

Expose release metadata through `{{SOURCE_DIR}}/release_info.py` so health endpoints and startup logs can report the running tag and commit.

## Loki Integration

If your deployment ships journald logs into Loki, prefer the `component="{{PROJECT_NAME}}"` label described in [OBSERVABILITY.md](OBSERVABILITY.md). That keeps project queries stable across environments.

## Graceful Shutdown

Long-running tasks should use a longer `TimeoutStopSec=` than the systemd default so in-flight work can finalize and write any session artifacts before forceful termination.
