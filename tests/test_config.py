from conftest import abort
from fabric.api import env
from fabrix.config import read_config


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


def test_hosts_and_roles_not_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            defaults:
                hosts_defined: False
                roles_defined: False
        """)
    with abort('read_config: hosts or roles must be defined in config'):
        read_config()


def test_hosts_and_roles_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 172.22.22.99
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: hosts and roles can\'t be simultaneously defined in config'):
        read_config()


def test_hosts_is_not_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              host:172.22.22.99
        """)
    with abort('read_config: hosts must be list type'):
        read_config()


def test_hosts_must_not_be_empty(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts: []
        """)
    with abort('read_config: hosts must not be empty'):
        read_config()


def test_hosts_must_be_list_of_strings(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - host: 172.22.22.99
        """)
    with abort('read_config: hosts must be list of strings'):
        read_config()


def test_hosts_host_cant_be_empty_string(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - ""
        """)
    with abort('read_config: hosts host can\'t be empty string'):
        read_config()
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              -
        """)
    with abort('read_config: hosts host can\'t be empty string'):
        read_config()


def test_host_already_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
              - 10.10.10.10
              - 11.11.11.11
        """)
    with abort('read_config: host \'%s\' already defined in hosts list' % '11.11.11.11'):
        read_config()


def test_roles_is_not_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
                role: test
        """)
    with abort('read_config: roles must be list type'):
        read_config()


def test_roles_must_not_be_empty(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles: []
        """)
    with abort('read_config: roles must not be empty'):
        read_config()


def test_roles_role_cant_be_empty_string(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role:
                hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role can\'t be empty string'):
        read_config()
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: ""
                hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role can\'t be empty string'):
        read_config()


def test_roles_role_required(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role required'):
        read_config()


def test_roles_role_must_be_string_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: ['test']
              - hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role must be string type'):
        read_config()


def test_roles_hosts_required(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
        """)
    with abort('read_config: role \'%s\' hosts required' % 'test'):
        read_config()


def test_roles_hosts_must_be_list_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts: 10.10.10.10
        """)
    with abort('read_config: role \'%s\' hosts must be list type' % 'test'):
        read_config()


def test_roles_hosts_host_cant_be_empty_string(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - ""
        """)
    with abort('read_config: role \'%s\' hosts host can\'t be empty string' % 'test'):
        read_config()
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  -
        """)
    with abort('read_config: role \'%s\' hosts host can\'t be empty string' % 'test'):
        read_config()


def test_role_hosts_must_be_list_of_strings(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - ['10.10.10.10', '11.11.11.11']
        """)
    with abort('read_config: role \'%s\' hosts must be list of strings' % 'test'):
        read_config()


def test_roles_hosts_already_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
                  - 10.10.10.10
                  - 11.11.11.11
        """)
    with abort('read_config: host \'%s\' already defined in role \'%s\' hosts list' % ('11.11.11.11', 'test')):
        read_config()


def test_role_already_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
                  - 10.10.10.10
              - role: other-role
                hosts:
                  - 172.22.22.99
                  - 11.11.11.11
              - role: test
                hosts:
                  - 22.22.22.22
        """)
    with abort('read_config: role \'%s\' already defined' % 'test'):
        read_config()


def test_unexpected_roles_entry(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
                  - 10.10.10.10
                vars:
                  foo: bar
        """)
    with abort('read_config: unexpected roles entry: %s' % 'vars: {foo: bar}'):
        read_config()


def test_roles_empty_hosts_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test2
                hosts:
                  - 11.11.11.11
              - role: test
                hosts: []
        """)
    with abort('read_config: role \'%s\' hosts must not be empty' % 'test'):
        read_config()


def test_error_parsing_yaml(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
              host_vars: []
        """)
    with abort('read_config: error parsing config.*'):
        read_config()


def test_host_vars_must_be_list_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
                foo: bar
        """)
    with abort('read_config: host_vars must be list type'):
        read_config()
