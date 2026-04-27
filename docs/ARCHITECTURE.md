# Architecture Documentation

This document describes the technical architecture of {{PROJECT_NAME}}.

## Overview

[High-level description of the system architecture]

## Delivery And Deployment Control Plane

The template now includes a deployment control plane alongside the application scaffold:

- `.github/workflows/release.yml` is the operator entry point for manual and release-driven deployments
- `scripts/github/resolve_release_context.py` converts trigger-specific GitHub metadata into stable deployment inputs
- `scripts/redeploy.sh` and `scripts/release_smoke_check.sh` define the handoff between GitHub Actions and the infrastructure playbooks
- `infra/hetzner/`, `infra/home-worker/`, and `infra/site/` provide the inventory, secrets, and orchestration skeletons that projects customize per environment

```mermaid
flowchart LR
    A["workflow_dispatch / release: published"] --> B["resolve_release_context.py"]
    B --> C["tag create or verify"]
    C --> D["GitHub Release status update"]
    D --> E["materialize SSH, inventory, secrets"]
    E --> F["scripts/redeploy.sh"]
    F --> G["Ansible playbooks under infra/"]
    G --> H["scripts/release_smoke_check.sh"]
    H --> I["success/failure status update on Release"]
```

## System Components

### Component Diagram

```
┌─────────────────┐     ┌─────────────────┐
│   Component A   │────▶│   Component B   │
└─────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Component C   │     │   Component D   │
└─────────────────┘     └─────────────────┘
```

### Component A

**Purpose**: [Description]

**Responsibilities**:
- Responsibility 1
- Responsibility 2

**Key Files**:
- `{{SOURCE_DIR}}/component_a.py`

### Component B

**Purpose**: [Description]

**Responsibilities**:
- Responsibility 1
- Responsibility 2

**Key Files**:
- `{{SOURCE_DIR}}/component_b.py`

## Data Flow

1. Step 1: [Description]
2. Step 2: [Description]
3. Step 3: [Description]

## Design Decisions

### Decision 1: [Title]

**Context**: [Why this decision was needed]

**Decision**: [What was decided]

**Consequences**:
- Pro: [Positive consequence]
- Con: [Negative consequence]

### Decision 2: [Title]

**Context**: [Why this decision was needed]

**Decision**: [What was decided]

**Consequences**:
- Pro: [Positive consequence]
- Con: [Negative consequence]

## Performance Considerations

- [Consideration 1]
- [Consideration 2]

## Security Considerations

- [Security measure 1]
- [Security measure 2]

## Future Enhancements

- [ ] Enhancement 1
- [ ] Enhancement 2
- [ ] Enhancement 3
