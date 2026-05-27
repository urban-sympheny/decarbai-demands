"""On-demand S3 model cache: download a city archive once, reuse from disk."""

import shutil
import tarfile
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


S3_BASE_URL = "https://prod-eu-north-1-sympheny-public.s3.eu-north-1.amazonaws.com/decarbai"
_CACHE_ROOT = Path.home() / ".cache" / "decarbai" / "models"


def ensure_city_models(country: str, city: str) -> Path:
    """Return local path to extracted city models, downloading from S3 if needed."""
    city_dir = _CACHE_ROOT / country / city
    if city_dir.exists():
        return city_dir

    url = f"{S3_BASE_URL}/{country}/{city}.tar"
    city_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {city} models from S3…", flush=True)

    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with (
            urlopen(url) as resp,  # noqa: S310 — trusted Sympheny public S3 bucket; no auth required
            tmp_path.open("wb") as f,
        ):
            while chunk := resp.read(1 << 20):
                f.write(chunk)
        with tarfile.open(tmp_path) as tar:
            tar.extractall(city_dir)  # noqa: S202 — archive is from a trusted Sympheny-controlled S3 bucket
    except HTTPError as e:
        shutil.rmtree(city_dir, ignore_errors=True)
        if e.code == 404:
            raise FileNotFoundError(f"No models for '{country}/{city}' on S3; verify country/city spelling.") from e
        raise
    except Exception:
        shutil.rmtree(city_dir, ignore_errors=True)
        raise
    finally:
        tmp_path.unlink(missing_ok=True)

    return city_dir
