# =============================================================================
# Arah — Hermes auto-setup stack
# JorahOne
#
# Arah is a setup/orchestration toolkit. This Dockerfile provides a CLI
# container for running arah scripts and managing the stack.
# =============================================================================
FROM alpine:3.24

RUN apk add --no-cache \
    bash curl jq yq git openssh-client \
    docker-cli docker-compose \
    python3 py3-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy arah scripts and configs
COPY scripts/ ./scripts/
COPY profiles/ ./profiles/
COPY docs/ ./docs/
COPY j1.yaml ./
COPY live-manifest.json ./

# Make scripts executable
RUN find scripts/ -name "*.sh" -exec chmod +x {} \;

# Default entrypoint: bootstrap
ENTRYPOINT ["bash", "scripts/bootstrap.sh"]
CMD ["--help"]

HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -c "test -f /app/live-manifest.json && echo 'healthy' || exit 1"
