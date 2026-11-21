import os
import subprocess
from math import isfinite
from typing import NamedTuple
from urllib.parse import urlsplit


class Target(NamedTuple):
    base_url: str
    expected_release: str
    deadline: float


def load_target():
    address = os.getenv("BASE_URL", "").strip().rstrip("/")
    release = os.getenv("EXPECTED_RELEASE", "").strip()
    url = urlsplit(address)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("Set BASE_URL to an HTTP(S) origin")
    if url.path or url.query or url.fragment or url.username is not None:
        raise ValueError("BASE_URL must contain only a scheme, host and optional port")
    if not release:
        raise ValueError("Set EXPECTED_RELEASE")
    deadline = float(os.getenv("CHECK_TIMEOUT", "2.5"))
    if not isfinite(deadline) or deadline <= 0:
        raise ValueError("CHECK_TIMEOUT must be positive and finite")
    return Target(address, release, deadline)


def main():
    try:
        target = load_target()
    except ValueError as error:
        print(f"CHECK_FAILED configuration: {error}")
        return 1

    homepage = target.base_url + "/"
    args = ["curl", "-q", "-fsS", "--noproxy", "*", "--", homepage]
    try:
        reply = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=target.deadline,
        )
    except subprocess.TimeoutExpired:
        print(f"DEADLINE {target.deadline:g}s exceeded at {homepage}")
        return 2
    except OSError as error:
        print(f"CHECK_FAILED cannot launch curl: {error}")
        return 1

    if reply.returncode != 0:
        print(f"CHECK_FAILED curl={reply.returncode} {reply.stderr.strip()}")
        return 1
    if target.expected_release not in reply.stdout:
        print(f"CHECK_FAILED expected release {target.expected_release} is missing")
        return 1

    print(f"SUCCESS {target.expected_release} served at {homepage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
