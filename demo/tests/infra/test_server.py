def test_nginx_configuration(host):
    result = host.run("nginx -t")
    assert result.rc == 0, result.stderr


def test_release_content(host):
    page = host.file("/usr/share/nginx/html/index.html")
    assert page.is_file
    assert page.contains("devops6-demo")
