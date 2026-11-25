## Docker build and offline dependency installation

**What I used AI for:** I used Google Gemini to diagnose repeated Docker build failures while `pip install -r requirements.txt` tried to reach PyPI. The Codespace terminal returned HTTP 200 from `pypi.org`, but pip inside Docker timed out. Additional checks showed that a Docker container could open TCP connections but timed out during TLS handshakes to `pypi.org` and `files.pythonhosted.org`; TLS to `example.com` worked. Host networking did not resolve the issue.

**What I accepted:** I accepted the wheelhouse workaround: download precompiled wheels from the Codespace terminal, then install them from the build context with pip's `--no-index` and `--find-links` options. The Docker image uses Python 3.12 while the Codespace interpreter was Python 3.14.2, so the download was explicitly targeted to CPython 3.12.

**Commands used:**

First, download the packages in `requirements.txt` for the Docker target:

```bash
python -m pip download \
  --only-binary=:all: \
  --dest wheelhouse \
  --platform manylinux_2_28_x86_64 \
  --platform manylinux_2_17_x86_64 \
  --platform manylinux2014_x86_64 \
  --python-version 3.12 \
  --implementation cp \
  --abi cp312 \
  --abi abi3 \
  --abi none \
  -r requirements.txt
```

The first download did not include the compatible `greenlet` wheel required by SQLAlchemy, so it was downloaded separately:

```bash
python -m pip download \
  --only-binary=:all: \
  --dest wheelhouse \
  --platform manylinux_2_28_x86_64 \
  --platform manylinux_2_24_x86_64 \
  --platform manylinux_2_17_x86_64 \
  --platform manylinux2014_x86_64 \
  --python-version 3.12 \
  --implementation cp \
  --abi cp312 \
  --abi abi3 \
  --abi none \
  greenlet
```

**What I changed or verified:** I added the wheelhouse to the Docker build and installed packages offline. I added `platform: linux/amd64` to the API service so the build target matches the downloaded Linux x86-64 wheels. The image then built successfully; Compose started PostgreSQL as healthy; Alembic applied the initial migration; and Uvicorn started listening on port 8000. The wheelhouse must remain in the repository while the Dockerfile relies on offline installation.

## Repository and submission review

**What I used AI for:** I used Google Gemini to check the project against the Week 3 deliverables.

## Router and controller structure

**What I used AI for:** I used Google Gemini to help decide how to structure the code. FastAPI handles routing and controller duties together, so i was confused and my first plan was thin routers in `/routers` with services and repositories behind them. I checked that plan with my senior engineer.

**What I accepted and changed:** I then changed it. After asking Gemini, I separated routers from controllers, as in Week 2's MVC structure, so routers handle HTTP only and controllers translate service errors into HTTP responses. I then used it to explain how best to structure the project, how all the files map to each other in python.



