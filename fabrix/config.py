import os.path
import copy
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from fabric.api import env, abort
from fabrix.ioutil import read_local_file, debug


class _ConfAttributeDict(dict):
    super__setitem__ = dict.__setitem__
    super__getitem__ = dict.__getitem__

    def __getattr__(self, key):
        try:
            return self.super__getitem__(env.host_string)[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self.super__getitem__(env.host_string)[key] = value

    def __getitem__(self, key):
        return self.super__getitem__(env.host_string)[key]

    def __setitem__(self, key, value):
        self.super__getitem__(env.host_string)[key] = value

    def __nonzero__(self):
        return True


class _AttributeDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __nonzero__(self):
        return True


conf = _ConfAttributeDict()
local_conf = _AttributeDict()


def parse_config(config_text):
    config = load(config_text, Loader=Loader)
    config_yaml = dump(config, Dumper=Dumper)
    debug('config_text:', config_text, 'config_yaml:', config_yaml, 'config:', config)
    if 'hosts' in config and 'roles' in config:
        abort('read_config: hosts and roles can\'t be simultaneously defined in config')
    if 'hosts' not in config and 'roles' not in config:
        abort('read_config: hosts or roles must be defined in config')
    hosts = list()
    if 'hosts' in config:
        if not isinstance(config['hosts'], list):
            abort('read_config: hosts must be list type')
        if not config['hosts']:
            abort('read_config: hosts must not be empty')
        hosts_set = set()
        for host in config['hosts']:
            if host is None or host == '':
                abort('read_config: hosts host can\'t be empty string')
            if not isinstance(host, basestring):
                abort('read_config: hosts must be list of strings')
            if host in hosts_set:
                abort('read_config: host \'%s\' already defined in hosts list' % host)
            hosts_set.add(host)
        hosts = config['hosts']
        del config['hosts']
    roles = dict()
    roles_hosts = set()
    host_roles = dict()
    if 'roles' in config:
        if not isinstance(config['roles'], list):
            abort('read_config: roles must be list type')
        if not config['roles']:
            abort('read_config: roles must not be empty')
        for entry in config['roles']:
            if 'role' not in entry:
                abort('read_config: roles role required')
            role = entry['role']
            del entry['role']
            if role is None or role == '':
                abort('read_config: roles role can\'t be empty string')
            if not isinstance(role, basestring):
                abort('read_config: roles role must be string type')
            if 'hosts' not in entry:
                abort('read_config: roles hosts required')
            if not isinstance(entry['hosts'], list):
                abort('read_config: roles hosts must be list type')
            hosts_set = set()
            for host in entry['hosts']:
                if host is None or host == '':
                    abort('read_config: role hosts host can\'t be empty string')
                if not isinstance(host, basestring):
                    abort('read_config: role hosts must be list of strings')
                if host in hosts_set:
                    abort('read_config: host \'%s\' already defined in role \'%s\' hosts list' % (host, role))
                hosts_set.add(host)
                if host not in host_roles:
                    host_roles[host] = list()
                host_roles[host].append(role)
                roles_hosts.add(host)
            if role in roles:
                abort('read_config: role \'%s\' already defined' % role)
            roles[role] = entry['hosts']
            del entry['hosts']
            if entry:
                abort('read_config: unexpected roles entry: %s' % dump(entry, Dumper=Dumper))
        if not roles_hosts:
            abort('read_config: roles hosts must not be empty')
        del config['roles']
    host_vars = dict()
    if 'host_vars' in config:
        if not isinstance(config['host_vars'], list):
            abort('read_config: host_vars must be list type')
        for entry in config['host_vars']:
            if 'host' not in entry:
                abort('read_config: host_vars host required')
            if not isinstance(entry['host'], basestring):
                abort('read_config: host_vars host must be string type')
            host = entry['host']
            del entry['host']
            if hosts and host not in hosts:
                abort('read_config: host_vars host \'%s\' not defined in hosts list' % host)
            elif roles and host not in roles_hosts:
                abort('read_config: host_vars host \'%s\' not defined in roles hosts list' % host)
            if 'vars' not in entry:
                abort('read_config: host_vars vars required')
            if not isinstance(entry['vars'], dict):
                abort('read_config: host_vars vars must be dictionary type')
            if host in host_vars:
                abort('read_config: host_vars host \'%s\' already defined' % host)
            host_vars[host] = entry['vars']
            del entry['vars']
            if entry:
                abort('read_config: unexpected host_vars entry: %s' % dump(entry, Dumper=Dumper))
        del config['host_vars']
    role_vars = dict()
    if 'role_vars' in config:
        if not roles:
            abort('read_config: unexpected role_vars, because roles is not defined')
        if not isinstance(config['role_vars'], list):
            abort('read_config: role_vars must be list type')
        for entry in config['role_vars']:
            if 'role' not in entry:
                abort('read_config: role_vars role required')
            if not isinstance(entry['role'], basestring):
                abort('read_config: role_vars role must be string type')
            role = entry['role']
            del entry['role']
            if role not in roles:
                abort('read_config: role_vars role \'%s\' not defined in roles' % roles)
            if 'vars' not in entry:
                abort('read_config: role_vars vars required')
            if not isinstance(entry['vars'], dict):
                abort('read_config: role_vars vars must be dictionary type')
            if role in role_vars:
                abort('read_config: role_vars role \'%s\' already defined' % role)
            role_vars[role] = entry['vars']
            del entry['vars']
            if entry:
                abort('read_config: unexpected role_vars entry: %s' % dump(entry, Dumper=Dumper))
        del config['role_vars']
    defaults = dict()
    if 'defaults' in config:
        if not isinstance(config['defaults'], dict):
            abort('read_config: defaults must be dictionary type')
        defaults = config['defaults']
        del config['defaults']
    local_vars = dict()
    if 'local_vars' in config:
        if not isinstance(config['local_vars'], dict):
            abort('read_config: local_vars must be dictionary type')
        local_vars = config['local_vars']
        del config['local_vars']
    if config:
        abort('read_config: unexpected config entry:\n\n%s' % dump(config, Dumper=Dumper))
    for key, value in local_vars.items():
        local_conf[key] = value
    if hosts:
        env.hosts = hosts
        env.roledefs = dict()
        for host in hosts:
            host_variables = _AttributeDict()
            if defaults:
                for key, value in defaults.items():
                    host_variables[key] = copy.deepcopy(value)
            if host in host_vars:
                for key, value in host_vars[host].items():
                    host_variables[key] = copy.deepcopy(value)
            conf.super__setitem__(host, host_variables)
    else:
        env.hosts = list()
        env.roledefs = roles
        for host in roles_hosts:
            host_variables = _AttributeDict()
            if defaults:
                for key, value in defaults.items():
                    host_variables[key] = copy.deepcopy(value)
            for role in host_roles[host]:
                if role in role_vars:
                    for key, value in role_vars[role].items():
                        host_variables[key] = copy.deepcopy(value)
            if host in host_vars:
                for key, value in host_vars[host].items():
                    host_variables[key] = copy.deepcopy(value)
            conf.super__setitem__(host, host_variables)
    debug(
        'hosts:', hosts, 'roles:', roles, 'roles_hosts:', roles_hosts,
        'host_roles:', host_roles, 'host_vars:', host_vars, 'role_vars:',
        role_vars, 'defaults:', defaults, 'local_vars:', local_vars,
        'conf:', conf, 'local_conf:', local_conf)


def read_config(argument_config_filename=None):
    if env.real_fabfile is None:
        return
    if argument_config_filename is None:
        dirname = os.path.dirname(env.real_fabfile)
        basename = os.path.basename(env.real_fabfile)
        name, ext = os.path.splitext(basename)
        config_filename = os.path.join(dirname, name + '.yaml')
    elif not os.path.isabs(argument_config_filename):
        dirname = os.path.dirname(env.real_fabfile)
        config_filename = os.path.join(dirname, argument_config_filename)
    else:
        config_filename = argument_config_filename
    if not os.path.isfile(config_filename):
        if argument_config_filename is None:
            return
        else:
            abort('read_config: config \'%s\' not exists' % config_filename)
    else:
        debug('fabrix: using config \'%s\'' % config_filename)
        parse_config(read_local_file(config_filename))


read_config()
