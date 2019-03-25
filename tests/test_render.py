from conftest import abort
from fabric.api import env
from fabrix.api import render_template, render, read_config


def test_render_template(tmpdir, monkeypatch):
    fabfile_dir = tmpdir
    templates_dir = fabfile_dir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    template_file.write("Hello, {{ name }}!\n")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile_dir.join("fabfile.py")))
    assert render_template("hello.txt.j2", name="World") == "Hello, World!\n"


def test_render_template_failed_if_templates_dir_not_exists(tmpdir, monkeypatch):
    fabfile_dir = tmpdir
    templates_dir = str(fabfile_dir.join("templates"))
    monkeypatch.setitem(env, "real_fabfile", str(fabfile_dir.join("fabfile.py")))
    with abort('render_template: templates dir \'%s\' not exists' % templates_dir):
        render_template("hello.txt.j2", name="World")


def test_render_template_failed_if_template_file_not_exists(tmpdir, monkeypatch):
    fabfile_dir = tmpdir
    templates_dir = fabfile_dir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile_dir.join("fabfile.py")))
    with abort('render_template: template \'%s\' not exists' % template_file):
        render_template("hello.txt.j2", name="World")


def test_render_template_with_variables_from_conf(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars:
                  name: Test Server
        """)
    read_config()
    templates_dir = tmpdir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    template_file.write("Hello, {{ name }}!\n")
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    assert render_template("hello.txt.j2") == "Hello, Test Server!\n"
    assert render_template("hello.txt.j2", name="New Server") == "Hello, New Server!\n"


def test_render_template_with_variables_from_local_conf(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars:
                  name: Test Server
            local_vars:
              name: localhost
        """)
    read_config()
    templates_dir = tmpdir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    template_file.write("Hello, {{ name }}!\n")
    assert env.host_string is None
    assert render_template("hello.txt.j2") == "Hello, localhost!\n"
    assert render_template("hello.txt.j2", name="localdomain") == "Hello, localdomain!\n"


def test_render_template_with_undefined_variables(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars:
                  name: Test Server
        """)
    read_config()
    templates_dir = tmpdir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    template_file.write("Hello, {{ zzz.name }}!\n")
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    with abort("render_template: 'zzz' is undefined in file"):
        render_template("hello.txt.j2")


def test_render():
    assert render("Hello, {{ name }}!", name="World") == "Hello, World!\n"
    assert render("""

            Hello, {{ name }}!

            """, name="World") == "Hello, World!\n"
    with abort("render: 'zzz' is undefined in file .* line .*"):
        render("Hello, {{ zzz.name }}!\n")
