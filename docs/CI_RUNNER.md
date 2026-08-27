# CI Runner Operations

This guide documents how the template chooses between ephemeral ECS Fargate, GitHub-hosted, and persistent self-hosted runners.

## When To Use Which Runner

### ECS Fargate

Use `fargate` when:

- the repository is authorized on the shared Fargate runner GitHub App
- you want one isolated, ephemeral runner per job
- you want normal CI and secret scanning off GitHub-hosted billing

The template defaults to `fargate`. If you do not operate the shared dispatcher, select `github_hosted` when running `setup_template.py`.

### GitHub-hosted fallback

Use `github_hosted` when:

- you want the lowest-setup path
- your project does not need persistent self-hosted infrastructure
- you want GitHub to manage runner lifecycle and OS patching

### Self-hosted

Use `self_hosted_linux` or `self_hosted_linux_arm64` when:

- you need a fixed machine, architecture, or private network access
- you want to reuse a local Docker cache or pre-pulled CI image
- you need parity with deployment hardware or ARM-specific behavior

## Runner Contract

The main workflow executes natively on the selected runner. The runner must be able to:

- run GitHub Actions jobs
- run `actions/setup-python`
- reach PyPI and GitHub to install dependencies and actions

Fargate deliberately does not run nested Docker job containers. Each job checks out under `repo/`, selects Python with `actions/setup-python`, and installs the dependencies it needs. The image under `infra/ci/` remains an optional local or persistent-runner tool, not the Fargate execution environment.

## Authorize A Repository On The Shared Fargate App

Before changing a repository to `[self-hosted, fargate]`, add it to the shared GitHub App installation. With an owner token and the installation ID:

```bash
repository_id="$(gh api repos/{{GITHUB_OWNER}}/{{PROJECT_NAME}} --jq .id)"
gh api -X PUT \
  "user/installations/<installation-id>/repositories/${repository_id}"
```

Verify the first workflow run is claimed by a runner named `fargate-<job-id>` before treating activation as complete. A generated repository outside the infrastructure owner's account should use `github_hosted` until it has its own dispatcher and App installation.

## Workflow Surface

`ci.yml` resolves runner selection centrally:

- default target: `{{CI_RUNNER}}`
- manual override via `workflow_dispatch` input `runner_target`
- supported values:
  - `fargate`
  - `github_hosted`
  - `self_hosted_linux`
  - `self_hosted_linux_arm64`

Downstream jobs consume `runs-on: ${{ fromJSON(needs.resolve-runner.outputs.runner) }}`. The `Secret Scanning` workflow uses `[self-hosted, fargate]` directly so Gitleaks follows the same runner policy.

## Register A Self-Hosted Runner

1. Create a Linux host that can run GitHub Actions jobs.
2. Create a GitHub runner registration token for the repository.
3. Copy and adapt `infra/home-worker/ci_runner_setup.yml` for your environment.
4. Keep the runner labels aligned with `.github/workflows/ci.yml`.
5. Verify the host can run `actions/setup-python` and install project dependencies.

Suggested baseline labels:

- `self-hosted`
- `linux`

Add `arm64` if the host should satisfy the ARM-specific target.

## Use The Docker CI Image Locally

```bash
docker build -t {{PROJECT_NAME}}-ci:test -f infra/ci/Dockerfile .
docker compose -f infra/ci/docker-compose.ci.yml run --rm ci bash
```

Inside the container, run the same commands CI uses:

```bash
python3.12 -m pytest {{TEST_DIR}}/ -v --cov={{SOURCE_DIR}}
bandit -r {{SOURCE_DIR}}/ -ll
pip-audit --requirement requirements.txt
```

## Bootstrap Checklist For Persistent Self-Hosted Linux

- install the GitHub Actions runner binary for the host architecture
- register the runner for `https://github.com/{{GITHUB_OWNER}}/{{PROJECT_NAME}}`
- configure the runner as a persistent service
- verify Python setup and dependency installation work
- run a manual `workflow_dispatch` CI job against the self-hosted target

## Operational Notes

- If you rename CI jobs, update the required status contexts in `scripts/github/branch-protection-config.json`.
- If you change runner labels, keep `docs/CI_RUNNER.md`, `infra/home-worker/ci_runner_setup.yml`, and `.github/workflows/ci.yml` aligned.
- Keep `.github/workflows/gitleaks.yml` on the Fargate labels and avoid `sudo`; the ephemeral runner executes the downloaded binary from its workspace.
- If you change the optional shared toolchain, rebuild the CI image before using it locally or on a persistent runner.
