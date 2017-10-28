import re
import inspect
import collections
from fabric.api import run, abort, settings, hide


def _parse_packages(recursion_level, allow_empty_list_of_packages, *args):
    packages = set()
    for arg in args:
        if isinstance(arg, basestring):
            for line in arg.split('\n'):
                line = line.strip()
                if line == "":
                    continue
                packages.update(line.split())
        elif isinstance(arg, collections.Iterable):
            packages.update(_parse_packages(recursion_level + 1, True, *arg))
        else:
            caller = str(inspect.stack()[recursion_level + 1][3])
            fname = str(inspect.stack()[recursion_level + 2][1])
            nline = str(inspect.stack()[recursion_level + 2][2])
            abort('%s: unexpected object \'%s\' in list of packages in file %s line %s' % (caller, repr(arg), fname, nline))
    result = sorted(list(packages))
    if not result and not allow_empty_list_of_packages:
        caller = str(inspect.stack()[recursion_level + 1][3])
        fname = str(inspect.stack()[recursion_level + 2][1])
        nline = str(inspect.stack()[recursion_level + 2][2])
        abort('%s: unexpected empty list of packages in file %s line %s' % (caller, fname, nline))
    return result


def yum_install(*args):
    packages = _parse_packages(0, False, *args)
    command = "yum -y install " + " ".join(packages)
    with settings(hide('everything')):
        stdout = run(command)
    not_changed_regexp = re.compile(r'^Nothing to do$')
    changed = True
    for line in stdout.split('\n'):
        line = line.strip()
        if not_changed_regexp.match(line):
            changed = False
            break
    return changed


def yum_remove(*args):
    packages = _parse_packages(0, False, *args)
    command = "yum -y remove " + " ".join(packages)
    with settings(hide('everything')):
        stdout = run(command)
    not_changed_regexp = re.compile(r'^No Packages marked for removal$')
    changed = True
    for line in stdout.split('\n'):
        line = line.strip()
        if not_changed_regexp.match(line):
            changed = False
            break
    return changed


def yum_update(*args):
    if not args:
        packages = list()
    else:
        packages = _parse_packages(0, True, *args)
    command = "yum -y update " + " ".join(packages)
    with settings(hide('everything')):
        stdout = run(command)
    not_changed_regexp = re.compile(r'^No packages marked for update$')
    changed = True
    for line in stdout.split('\n'):
        line = line.strip()
        if not_changed_regexp.match(line):
            changed = False
            break
    return changed
