import pytest
from fabric.api import env
from fabrix.api import render_template


def test_render_template(tmpdir):
    fabfile_dir = tmpdir
    templates_dir = fabfile_dir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    template_file.write("Hello, {{ name}}!")
    env.real_fabfile = str(fabfile_dir.join("fabfile.py"))
    assert render_template("hello.txt.j2", name="World") == "Hello, World!"


def test_render_template_failed_if_templates_dir_not_exists(tmpdir):
    fabfile_dir = tmpdir
    templates_dir = str(fabfile_dir.join("templates"))
    env.real_fabfile = str(fabfile_dir.join("fabfile.py"))
    with pytest.raises(SystemExit, message='render_template: templates dir \'%s\' not exists' % templates_dir):
        render_template("hello.txt.j2", name="World")


def test_render_template_failed_if_template_file_not_exists(tmpdir):
    fabfile_dir = tmpdir
    templates_dir = fabfile_dir.mkdir("templates")
    template_file = templates_dir.join("hello.txt.j2")
    env.real_fabfile = str(fabfile_dir.join("fabfile.py"))
    with pytest.raises(SystemExit, message='render_template: template \'%s\' not exists' % template_file):
        render_template("hello.txt.j2", name="World")
