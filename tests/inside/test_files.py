import pytest


ROOT = "/usr/share/lantern"


def test_nginx_checks_its_configuration(host):
    result = host.run("nginx -t")
    assert result.rc == 0, result.stderr


@pytest.mark.parametrize(
    "name",
    ["/etc/nginx/conf.d/default.conf", f"{ROOT}/index.html", f"{ROOT}/health.json"],
    ids=["nginx", "index", "health"],
)
def test_packaged_file_exists(host, name):
    assert host.file(name).is_file


def test_packaged_index_contains_release(host, lantern_target):
    assert host.file(f"{ROOT}/index.html").contains(lantern_target.expected_release)
