# CS-XX-001: Python 3.12 with the dependencies of the repository snapshot.
# The snapshot is copied to /workspace/repo; nothing from solution/ or tests/ is in the image.
FROM python:3.12-slim-bookworm

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR=http://deb.debian.org

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    TZ=UTC

# With a mirror given, the package sources are replaced as a whole so that the
# three bookworm suites come from the same place.
RUN if [ "${APT_MIRROR}" != "http://deb.debian.org" ]; then \
        rm -f /etc/apt/sources.list.d/*; \
        printf 'deb %s/debian bookworm main\ndeb %s/debian bookworm-updates main\ndeb %s/debian-security bookworm-security main\n' \
            "${APT_MIRROR}" "${APT_MIRROR}" "${APT_MIRROR}" > /etc/apt/sources.list; \
    fi \
    && apt-get update \
    && apt-get install -y --no-install-recommends git patch ripgrep less \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock /opt/cs/requirements.lock
RUN pip install -i "${PIP_INDEX_URL}" -r /opt/cs/requirements.lock

RUN useradd -m -u 1000 -s /bin/bash dev
COPY --chown=dev:dev workspace/ /workspace/

# The repository's own tests import both `oscar` (src/) and `tests` (repository root).
ENV PYTHONPATH=/workspace/repo/src:/workspace/repo

USER dev
WORKDIR /workspace
# A git baseline so that the agent can use git and the harness can read the diff.
RUN cd /workspace/repo \
    && git init -q -b main \
    && git -c user.name=cs -c user.email=cs@example.invalid add -A \
    && git -c user.name=cs -c user.email=cs@example.invalid commit -q -m "snapshot"

CMD ["sleep", "infinity"]
