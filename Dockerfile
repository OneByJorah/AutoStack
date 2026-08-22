# =============================================================================
# AutoStack — Hermes auto-setup stack
# JorahOne
#
# AutoStack is a setup/orchestration toolkit. This Dockerfile provides a CLI
# container for running AutoStack scripts and managing the stack.
# =============================================================================
FROM alpine:3.24

RUN apk add --no-cache \
    bash curl jq yq git openssh-client \
    docker-cli docker-compose \
    python3 py3-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy AutoStack scripts and configs
COPY scripts/ ./scripts/
COPY profiles/ ./profiles/
COPY docs/ ./docs/

# Make scripts executable
RUN find scripts/ -name "*.sh" -exec chmod +x {} \;

# Default entrypoint: bootstrap
ENTRYPOINT ["bash", "scripts/bootstrap.sh"]
CMD ["--help"]
