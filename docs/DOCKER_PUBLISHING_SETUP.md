# Docker Image Publishing Setup

## Overview

This project automatically builds and publishes Docker images to GitHub Container Registry (GHCR) on successful test completion on the main branch.

**Registry:** `ghcr.io/hlyl/ctss`
- **API image:** `ghcr.io/hlyl/ctss-api`
- **Streamlit image:** `ghcr.io/hlyl/ctss-streamlit`

## Prerequisites

1. **GitHub Account** with repository access
2. **GitHub Personal Access Token** with the following scopes:
   - `write:packages` (publish container images)
   - `read:packages` (pull container images)

## Setup Instructions

### 1. Create GitHub Personal Access Token

1. Go to GitHub Settings → [Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Click **Generate new token**
3. Configure:
   - **Token name:** `CTSR_DOCKER_PUBLISH`
   - **Expiration:** 90 days (or your preference)
   - **Repository access:** Select this repository
   - **Permissions:**
     - `Contents: read`
     - `Packages: write`
4. Click **Generate token**
5. **Copy the token immediately** (you won't see it again)

### 2. Add Token to GitHub Secrets

1. Go to Repository Settings → **Secrets and variables → Actions**
2. Click **New repository secret**
3. Configure:
   - **Name:** `GITHUB_TOKEN`
   - **Value:** Paste your personal access token
4. Click **Add secret**

### 3. (Optional) Add Token to Local .env

If you want to manually push images from your local machine:

```bash
# In .env file:
GITHUB_TOKEN=your_token_here

# Then login locally:
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

## Triggering Image Builds

### Automatic Triggers (on main branch only)

Images are automatically built and pushed when:

1. **Integration tests pass** (after workflow: `integration-tests.yml`)
2. **Push to main branch** with a git tag (e.g., `git tag v1.0.0 && git push --tags`)

### Manual Build from Local

```bash
# Install Docker
docker build -t ghcr.io/hlyl/ctss-api:local ./ctsr-api
docker build -t ghcr.io/hlyl/ctss-streamlit:local ./streamlit-app

# Login to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Push images
docker push ghcr.io/hlyl/ctss-api:local
docker push ghcr.io/hlyl/ctss-streamlit:local
```

## Image Versioning

### On Main Branch Push
- **Tag format:** `main-<short-commit-sha>` + `latest`
- Example: `ghcr.io/hlyl/ctss-api:main-a1b2c3d4e5f6 `, `ghcr.io/hlyl/ctss-api:latest`

### On Git Tag Push (Release)
- **Tag format:** `<tag-name>` + `latest`
- Example: `ghcr.io/hlyl/ctss-api:v1.0.0`, `ghcr.io/hlyl/ctss-api:latest`

## Using Published Images

### Docker Run (API)
```bash
docker run -d \
  --name ctsr-api \
  -p 8000:8000 \
  -e POSTGRES_HOST=your_host \
  -e POSTGRES_DB=ctsr \
  -e POSTGRES_USER=ctsr_user \
  -e POSTGRES_PASSWORD=your_password \
  ghcr.io/hlyl/ctss-api:latest
```

### Docker Run (Streamlit)
```bash
docker run -d \
  --name ctsr-streamlit \
  -p 8501:8501 \
  -e API_URL=http://your_api:8000 \
  ghcr.io/hlyl/ctss-streamlit:latest
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    image: ghcr.io/hlyl/ctss-api:latest
    ports:
      - "8000:8000"
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_DB: ctsr
      POSTGRES_USER: ctsr_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

  streamlit:
    image: ghcr.io/hlyl/ctss-streamlit:latest
    ports:
      - "8501:8501"
    environment:
      API_URL: http://api:8000
```

## Troubleshooting

### "Insufficient permissions" error
- Verify token has `write:packages` scope
- Ensure token hasn't expired

### Images not pushing to GHCR
- Check GitHub Actions workflow logs (Actions tab)
- Verify tests passed before publish workflow triggers
- Ensure you're on the main branch

### Local push fails with authentication error
```bash
# Re-login to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin --password-stdin
```

## References

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions: Publish Docker Images](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
