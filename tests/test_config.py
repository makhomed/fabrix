import pytest
from conftest import abort
from fabric.api import env
from fabrix.config import read_config, conf, local_conf


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


def test_hosts_entry_none(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              -
        """)
    with abort('read_config: hosts host can\'t be empty string'):
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
              - role: ""
                hosts:
                  - 11.11.11.11
        """)
    with abort('read_config: roles role can\'t be empty string'):
        read_config()


def test_roles_role_is_none(tmpdir, monkeypatch):
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


def test_roles_hosts_host_is_none(tmpdir, monkeypatch):
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


def test_host_vars_host_required(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - foo: bar
        """)
    with abort('read_config: host_vars host required'):
        read_config()


def test_host_vars_host_cant_be_empty_string(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: ""
        """)
    with abort('read_config: host_vars host can\'t be empty string'):
        read_config()


def test_host_vars_host_is_none(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host:
        """)
    with abort('read_config: host_vars host can\'t be empty string'):
        read_config()


def test_host_vars_host_must_be_string_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: []
        """)
    with abort('read_config: host_vars host must be string type'):
        read_config()


def test_host_vars_host_not_defined_in_hosts_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 10.10.10.10
            host_vars:
              - host: 11.11.11.11
                vars: {}
        """)
    with abort('read_config: host_vars host \'%s\' not defined in hosts list' % '11.11.11.11'):
        read_config()


def test_host_vars_host_not_defined_in_roles_hosts_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 10.10.10.10
            host_vars:
              - host: 11.11.11.11
                vars: {}
        """)
    with abort('read_config: host_vars host \'%s\' not defined in roles hosts list' % '11.11.11.11'):
        read_config()


def test_host_vars_vars_required(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vsar:
        """)
    with abort('read_config: host_vars host \'%s\' vars required' % '11.11.11.11'):
        read_config()


def test_host_vars_vars_must_be_dict(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars: ['a', 'b', 'c']
        """)
    with abort('read_config: host_vars host \'%s\' vars must be dictionary type' % '11.11.11.11'):
        read_config()


def test_host_vars_host_already_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars:
                  foo: bar
              - host: 11.11.11.11
                vars:
                  foo: baz
        """)
    with abort('read_config: host_vars host \'%s\' already defined' % '11.11.11.11'):
        read_config()


def test_host_vars_unexpected_entry(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars:
                  foo: baz
                vras:
                  foo: bar
        """)
    with abort('read_config: unexpected host_vars entry: %s' % 'vras: {foo: bar}'):
        read_config()


def test_roles_vars_with_roles_not_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            role_vars:
              - role: test
                vars:
                  foo: baz
        """)
    with abort('read_config: unexpected role_vars, because roles is not defined'):
        read_config()


def test_role_vars_must_be_list_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              foo: baz
        """)
    with abort('read_config: role_vars must be list type'):
        read_config()


def test_role_vars_role_required(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - rloe: test
                vars:
                  foo: baz
        """)
    with abort('read_config: role_vars role required'):
        read_config()


def test_role_vars_role_is_none(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role:
                vars:
                  foo: baz
        """)
    with abort('read_config: role_vars role can\'t be empty string'):
        read_config()


def test_role_vars_role_is_not_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: [ 'test']
                vars:
                  foo: baz
        """)
    with abort('read_config: role_vars role must be string type'):
        read_config()


def test_role_vars_role_is_empty_string(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: ""
                vars:
                  foo: baz
        """)
    with abort('read_config: role_vars role can\'t be empty string'):
        read_config()


def test_role_vars_role_not_in_roles(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: text
                vars:
                  foo: baz
        """)
    with abort('read_config: role_vars role \'%s\' not defined in roles' % 'text'):
        read_config()


def test_role_vars_role_vars_not_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: test
        """)
    with abort('read_config: role_vars role \'%s\' vars required' % 'test'):
        read_config()


def test_role_vars_role_vars_must_be_list(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: test
                vars: ['a', 'b', 'c']
        """)
    with abort('read_config: role_vars role \'%s\' vars must be dictionary type' % 'test'):
        read_config()


def test_role_vars_role_already_defined(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: test
                vars: {}
              - role: test
                vars: {}
        """)
    with abort('read_config: role_vars role \'%s\' already defined' % 'test'):
        read_config()


def test_role_vars_unknown_entry(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: test
                vars: {}
                vras: {foo: bar}
        """)
    with abort('read_config: unexpected role_vars entry: %s' % 'vras: {foo: bar}'):
        read_config()


def test_defaults_must_be_list_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            roles:
              - role: test
                hosts:
                  - 11.11.11.11
            role_vars:
              - role: test
                vars: {}
            defaults: []
        """)
    with abort('read_config: defaults must be dictionary type'):
        read_config()


def test_local_vars_must_be_list_type(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars: {}
            local_vars: []
        """)
    with abort('read_config: local_vars must be dictionary type'):
        read_config()


def test_unexpected_entry(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars: {}
            lcal_vars: {foo: bar}
        """)
    with abort('read_config: unexpected config entry:\n\n%s' % 'lcal_vars: {foo: bar}'):
        read_config()


def test_defaults_and_local_vars(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            hosts:
              - 11.11.11.11
            host_vars:
              - host: 11.11.11.11
                vars: {}
            defaults:
              nginx: True
            local_vars: {foo: bar}
        """)
    read_config()
    assert conf.nginx is True
    assert local_conf.foo == 'bar'
    local_conf['foo'] = 'baz'
    assert local_conf.foo == 'baz'
    local_conf.foo = True
    assert local_conf.foo is True


def test_host_vars(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            hosts:
              - 11.11.11.11
              - 22.22.22.22
            host_vars:
              - host: 11.11.11.11
                vars:
                  override: new
            defaults:
              nginx: True
              override: old
            local_vars: {foo: bar}
        """)
    read_config()
    assert conf.override == 'new'
    monkeypatch.setitem(env, "host_string", '22.22.22.22')
    assert conf.override == 'old'


def test_conf(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            hosts:
              - 11.11.11.11
              - 22.22.22.22
            host_vars:
              - host: 11.11.11.11
                vars:
                  override: new
            defaults:
              nginx: True
              override: old
            local_vars: {foo: bar}
        """)
    read_config()
    conf.test = 'beta'
    assert conf['test'] == 'beta'
    conf['override'] = 'disable'
    assert conf.override == 'disable'


def test_roles(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            roles:
              - role: web
                hosts:
                  - 11.11.11.11
                  - 22.22.22.22
                  - 33.33.33.33
              - role: db
                hosts:
                  - 7.7.7.7
                  - 9.9.9.9
              - role: rest
                hosts:
                  - 44.44.44.44

            defaults:
              var1: def1
              var2: def2
              var3: def3
              var4: def4
              var5: def5

            host_vars:
              - host: 11.11.11.11
                vars:
                  var1: special_value_for_host_11
              - host: 9.9.9.9
                vars:
                  type: mysql

            role_vars:
              - role: web
                vars:
                  var1: from_web_role
                  var2: from_web_role
              - role: db
                vars:
                  var3: from_db_role
            local_vars:
              var1: loc1
              var2: loc2
              var3: loc3
              var4: loc4
              var5: loc5
        """)
    read_config()
    assert local_conf.var1 == 'loc1'
    assert local_conf.var2 == 'loc2'
    assert local_conf.var3 == 'loc3'
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    assert conf.var1 == 'special_value_for_host_11'
    assert conf.var2 == 'from_web_role'
    assert conf.var3 == 'def3'
    monkeypatch.setitem(env, "host_string", '22.22.22.22')
    assert conf.var1 == 'from_web_role'
    assert conf.var2 == 'from_web_role'
    assert conf.var3 == 'def3'
    monkeypatch.setitem(env, "host_string", '44.44.44.44')
    assert conf.var1 == 'def1'
    assert conf.var2 == 'def2'
    assert conf.var3 == 'def3'


def test_roles_without_defaults(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            roles:
              - role: web
                hosts:
                  - 11.11.11.11
                  - 22.22.22.22
                  - 33.33.33.33
              - role: db
                hosts:
                  - 7.7.7.7
                  - 9.9.9.9
              - role: rest
                hosts:
                  - 44.44.44.44

            host_vars:
              - host: 11.11.11.11
                vars:
                  var1: special_value_for_host_11
              - host: 9.9.9.9
                vars:
                  type: mysql

            role_vars:
              - role: web
                vars:
                  var1: from_web_role
                  var2: from_web_role
              - role: db
                vars:
                  var3: from_db_role
        """)
    read_config()
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    assert conf.var1 == 'special_value_for_host_11'
    assert conf.var2 == 'from_web_role'
    with pytest.raises(AttributeError):
        conf.var3
    monkeypatch.setitem(env, "host_string", '22.22.22.22')
    assert conf.var1 == 'from_web_role'
    assert conf.var2 == 'from_web_role'
    with pytest.raises(AttributeError):
        conf.var3
    monkeypatch.setitem(env, "host_string", '44.44.44.44')
    with pytest.raises(AttributeError):
        conf.var1
    with pytest.raises(AttributeError):
        conf.var2
    with pytest.raises(AttributeError):
        conf.var3


def test_dict_methods(tmpdir, monkeypatch):
    fabfile = tmpdir.join("fabfile.py")
    config_file = tmpdir.join("fabfile.yaml")
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    config_file.write("""
            roles:
              - role: web
                hosts:
                  - 11.11.11.11
                  - 22.22.22.22
                  - 33.33.33.33
              - role: db
                hosts:
                  - 7.7.7.7
                  - 9.9.9.9
              - role: rest
                hosts:
                  - 44.44.44.44

            host_vars:
              - host: 11.11.11.11
                vars:
                  var1: special_value_for_host_11
              - host: 9.9.9.9
                vars:
                  type: mysql

            role_vars:
              - role: web
                vars:
                  var1: from_web_role
                  var2: from_web_role
                  var3: value3
                  var4: value4
                  var5: value5
              - role: db
                vars:
                  var3: from_db_role
            local_vars:
              var1: value1

        """)
    read_config()
    assert local_conf.var1 == 'value1'
    del local_conf.var1
    with pytest.raises(AttributeError):
        local_conf.var1
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    del conf.var1
    with pytest.raises(AttributeError):
        conf.var1
    del conf['var2']
    with pytest.raises(AttributeError):
        conf.var2
    conf.var1 = 'value1'
    conf.var2 = 'value2'
    assert len(repr(conf)) == len("{'var1': 'value1', 'var2': 'value2', 'var3': 'value3', 'var4': 'value4', 'var5': 'value5'}")
    conf_copy = conf.copy()
    assert conf == conf_copy
    assert conf == {'var1': 'value1', 'var2': 'value2', 'var3': 'value3', 'var4': 'value4', 'var5': 'value5'}
    assert conf != {'VAR1': 'value1', 'var2': 'value2', 'var3': 'value3', 'var4': 'value4', 'var5': 'value5'}
    assert conf.__hash__ is None
    assert len(conf) == 5
    for key in conf:
        assert key[0:3] == 'var'
    assert 'var3' in conf
    assert 'bar3' not in conf
    assert len(conf.keys()) == 5
    assert sorted(conf.keys()) == ['var1', 'var2', 'var3', 'var4', 'var5']
    for key, value in conf.items():
        assert key[0:3] == 'var'
        assert value[0:5] == 'value'
    for key, value in conf.iteritems():
        assert key[0:3] == 'var'
        assert value[0:5] == 'value'
    for key in conf.iterkeys():
        assert key[0:3] == 'var'
    for value in conf.itervalues():
        assert value[0:5] == 'value'
    assert sorted(conf.values()) == ['value1', 'value2', 'value3', 'value4', 'value5']
    assert conf.has_key('var5') # noqa
    assert not conf.has_key('var7') # noqa
    conf.update(dict(var6='oldvalue6', var7='oldvalue7'))
    assert conf.var6 == 'oldvalue6'
    assert conf.var7 == 'oldvalue7'
    conf.update(var6='value6', var7='value7')
    assert conf.var6 == 'value6'
    assert conf.var7 == 'value7'
    assert conf.get('var8') is None
    assert conf.get('var8', 'provided-default') is 'provided-default'
    assert conf.get('var5') == 'value5'
    assert conf.setdefault('var7') == 'value7'
    assert conf.var7 == 'value7'
    assert 'var8' not in conf
    assert conf.setdefault('var8', 'value8') == 'value8'
    assert conf.var8 == 'value8'
    with pytest.raises(KeyError):
        conf.pop('var9')
    before = conf.copy()
    assert conf.pop('var9', 'value9') == 'value9'
    after = conf.copy()
    assert before == after
    assert conf.__cmp__(before) == 0
    assert conf.__cmp__(after) == 0
    assert conf.pop('var8') == 'value8'
    assert len(conf) == 7
    for i in range(0, 7):
        key, value = conf.popitem()
        assert key[0:3] == 'var'
        assert value[0:5] == 'value'
    assert len(conf) == 0
    with pytest.raises(KeyError):
        conf.popitem()
    conf.clear()
    assert len(conf) == 0
    assert conf == dict()
