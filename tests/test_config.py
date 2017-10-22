from conftest import abort
from fabric.api import env
from fabrix.config import read_config, parse_config


def test_read_config_default_config_name_nox_exists(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    read_config()
    assert env.hosts == list()


def test_read_config_default_config_name_exists(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_filename = tmpdir.join("fabfile.yaml")
    config_filename.write("""
    hosts:
        - 172.22.22.99
    """)
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    read_config()
    assert env.hosts == ['172.22.22.99']


def test_read_config_explicit_relative_config_name(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_filename = tmpdir.join("stage.yaml")
    config_filename.write("""
    hosts:
        - 10.10.10.10
    """)
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    read_config("stage.yaml")
    assert env.hosts == ['10.10.10.10']


def test_read_config_explicit_absolute_config_name(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_filename = tmpdir.join("stage.yaml")
    config_filename.write("""
    hosts:
        - 10.20.30.40
    """)
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    read_config(str(config_filename))
    assert env.hosts == ['10.20.30.40']


def test_read_config_explicit_relative_config_name_not_exists(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_filename = tmpdir.join("stage.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    with abort('read_config: config \'%s\' not exists' % str(config_filename)):
        read_config("stage.yaml")


def test_hosts_and_roles_not_defined():
    with abort('read_config: hosts or roles must be defined in config'):
        parse_config("""
            defaults:
                hosts_defined: False
                roles_defined: False
        """)


def test_hosts_and_roles_defined():
    with abort('read_config: hosts and roles can\'t be simultaneously defined in config'):
        parse_config("""
            hosts:
              - 172.22.22.99
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
        """)


def test_hosts_is_not_list():
    with abort('read_config: hosts must be list type'):
        parse_config("""
            hosts:
              host:172.22.22.99
        """)


def test_hosts_must_not_be_empty():
    with abort('read_config: hosts must not be empty'):
        parse_config("""
            hosts: []
        """)


def test_hosts_must_be_list_of_strings():
    with abort('read_config: hosts must be list of strings'):
        parse_config("""
            hosts:
              - host: 172.22.22.99
        """)


def test_host_cant_be_empty_string():
    with abort('read_config: hosts host can\'t be empty string'):
        parse_config("""
            hosts:
              - ""
        """)
    with abort('read_config: hosts host can\'t be empty string'):
        parse_config("""
            hosts:
              -
        """)


def test_host_already_defined():
    with abort('read_config: host \'%s\' already defined in hosts list' % '11.11.11.11'):
        parse_config("""
            hosts:
              - 11.11.11.11
              - 10.10.10.10
              - 11.11.11.11
        """)


def test_roles_is_not_list():
    with abort('read_config: roles must be list type'):
        parse_config("""
            roles:
                role: test
        """)


def test_roles_must_not_be_empty():
    with abort('read_config: roles must not be empty'):
        parse_config("""
            roles: []
        """)


def test_roles_role_cant_be_empty_string():
    with abort('read_config: roles role can\'t be empty string'):
        parse_config("""
            roles:
              - role:
                hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role can\'t be empty string'):
        parse_config("""
            roles:
              - role: ""
                hosts:
                  - 11.11.11.11
        """)
