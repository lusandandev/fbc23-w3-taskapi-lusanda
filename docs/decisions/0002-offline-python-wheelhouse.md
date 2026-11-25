# Decision 0002: Install Python dependencies from a local wheelhouse

## Context

The initial Docker build failed during `pip install -r requirements.txt`. My Codespace terminal could reach `https://pypi.org/simple/fastapi/` and received HTTP 200, but pip inside a Docker container timed out. A direct TLS test also timed out when connecting from Docker to `pypi.org` and `files.pythonhosted.org`, while `example.com` completed TLS. Testing with Docker host networking did not resolve it. This showed that the build container's path to the Python package hosts was the blocker, the pinned FastAPI version itself was not the cause.

The Codespace interpreter was Python 3.14.2, while the API image uses Python 3.12. Downloading wheels using the host interpreter's default platform would therefore select the wrong binary dependencies.

## Decision

Download precompiled dependencies from the Codespace terminal into `wheelhouse/`, explicitly targeting CPython 3.12 and Linux AMD64. Keep the directory in the repository and install from it during the image build:

```dockerfile
COPY requirements.txt .
COPY wheelhouse/ /wheelhouse/

RUN python -m pip install \
    --no-cache-dir \
    --no-index \
    --find-links=/wheelhouse \
    -r requirements.txt
```

`--no-index` prevents pip from contacting PyPI; `--find-links=/wheelhouse` tells pip where to find the local wheel files. The first download missed the compatible `greenlet` wheel needed by SQLAlchemy, so `greenlet` was downloaded separately with the additional `manylinux_2_24_x86_64` platform tag.

## Consequences

- Docker can build the API image without accessing PyPI, provided the wheelhouse is included in the build context.
- The wheelhouse is about 19 MB and contains 35 wheel files in the reviewed project snapshot.
- The Compose API platform is pinned to `linux/amd64` to match these binary wheels.
- If a dependency version, Python version, platform or architecture changes, the wheelhouse must be regenerated for the target runtime.
- This is a workaround for the observed Codespaces/Docker network behaviour, not a general requirement for FastAPI or Docker. If container access to PyPI is restored, the project can be simplified to install directly from `requirements.txt` and the wheelhouse can be removed after a clean-build test.
