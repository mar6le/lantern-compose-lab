from subprocess import CompletedProcess, TimeoutExpired

import pytest

import verify_lantern


@pytest.fixture
def shell_environment(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://lantern.invalid:9191/")
    monkeypatch.setenv("EXPECTED_RELEASE", "test-lantern")
    monkeypatch.setenv("CHECK_TIMEOUT", "1.125")


def test_passes_environment_and_reports_success(shell_environment, monkeypatch, capsys):
    def local_curl(args, **options):
        assert args == ["curl", "-q", "-fsS", "--noproxy", "*", "--", "http://lantern.invalid:9191/"]
        assert options == {"capture_output": True, "text": True, "timeout": 1.125}
        return CompletedProcess(args, 0, "<code>test-lantern</code>", "")

    monkeypatch.setattr(verify_lantern.subprocess, "run", local_curl)
    assert verify_lantern.main() == 0
    assert capsys.readouterr().out.startswith("SUCCESS test-lantern")


@pytest.mark.parametrize(
    ("return_code", "body", "message"),
    [(7, "", "curl=7"), (0, "<p>previous build</p>", "expected release test-lantern is missing")],
)
def test_check_failures(shell_environment, monkeypatch, capsys, return_code, body, message):
    def local_curl(args, **options):
        return CompletedProcess(args, return_code, body, "connection unavailable")

    monkeypatch.setattr(verify_lantern.subprocess, "run", local_curl)
    assert verify_lantern.main() == 1
    assert message in capsys.readouterr().out


def test_timeout(shell_environment, monkeypatch, capsys):
    def local_curl(args, **options):
        raise TimeoutExpired(args, options["timeout"])

    monkeypatch.setattr(verify_lantern.subprocess, "run", local_curl)
    assert verify_lantern.main() == 2
    assert "DEADLINE 1.125s" in capsys.readouterr().out


@pytest.mark.parametrize("invalid", ["0", "infinite"])
def test_invalid_timeout(shell_environment, monkeypatch, capsys, invalid):
    def local_curl(*args, **options):
        pytest.fail("Invalid timeout was passed to curl")

    monkeypatch.setenv("CHECK_TIMEOUT", invalid)
    monkeypatch.setattr(verify_lantern.subprocess, "run", local_curl)
    assert verify_lantern.main() == 1
    assert "CHECK_FAILED configuration" in capsys.readouterr().out
