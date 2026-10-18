FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# uv: Python package manager used for the docs toolchain
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /usr/local/bin/

# LibreOffice + poppler: render lecture decks/scripts to PNG for visual QA (lecture-materials skill).
# Caladea/Carlito/Liberation are metric-compatible with Cambria/Calibri/Courier New, so text fit in renders is true.
# The base image's yarn apt repo has an expired key and breaks apt-get update, so it is removed first.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libreoffice-impress libreoffice-writer poppler-utils \
       fonts-crosextra-caladea fonts-crosextra-carlito fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Claude Code (native installer), installed for the non-root user
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash
ENV PATH="/home/vscode/.local/bin:${PATH}"
