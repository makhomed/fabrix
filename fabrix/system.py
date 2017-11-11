import re
import time
import inspect
import os.path
from fabric.state import connections
from fabric.api import env, abort, settings
from fabrix.editor import edit_file, replace_line, strip_text
from fabrix.ioutil import run, remove_file, remove_directory, create_directory, write_file


def is_reboot_required():
    """Is reboot required?

    .. note::
        This function uses internally ``/usr/bin/needs-restarting`` from ``yum-utils`` package.

    Returns:
        True if server reboot is required after ``yum_update()``, False otherwise.
    """
    if run('if [ ! -e /usr/bin/needs-restarting ] ; then echo notexists ; fi') == 'notexists':
        run('yum -y install yum-utils')
    stdout = run('/usr/bin/needs-restarting -r')
    reboot_required_regexp = re.compile(r'^Reboot is required to ensure that your system benefits from these updates\.$')
    reboot_required = False
    for line in stdout.split('\n'):
        line = line.strip()
        if reboot_required_regexp.match(line):
            reboot_required = True
            break
    return reboot_required


def reboot_and_wait(wait=120, command='reboot'):
    """Reboot the remote system.

    Args:
        wait: Time to wait remote system after reboot in seconds.
        command: Command for rebooting remote system.

    Returns:
        None
    """
    # Shorter timeout for a more granular cycle than the default.
    timeout = 3
    # Use 'wait' as max total wait time
    attempts = int(round(float(wait) / float(timeout)))
    # Don't bleed settings, since this is supposed to be self-contained.
    # User adaptations will probably want to drop the "with settings()" and
    # just have globally set timeout/attempts values.
    with settings(timeout=timeout, connection_attempts=attempts):
        run(command)
        # Try to make sure we don't slip in before pre-reboot lockdown
        time.sleep(5)
        # This is actually an internal-ish API call, but users can simply drop
        # it in real fabfile use -- the next run/sudo/put/get/etc call will
        # automatically trigger a reconnect.
        # We use it here to force the reconnect while this function is still in
        # control and has the above timeout settings enabled.
        connections.connect(env.host_string)
    # At this point we should be reconnected to the newly rebooted server.


def disable_selinux():
    """Disable SELinux.

    Edit ``/etc/selinux/config`` and write ``SELINUX=disabled`` to it.
    Also call ``setenforce 0`` to switch SELinux into Permissive mode.

    Returns:
        True if ``/etc/selinux/config`` changed or if SELinux ``Enforcing`` mode switched into ``Permissive`` mode, False otherwise.

    """
    if run('if [ -e /etc/selinux/config ] ; then echo exists ; fi') == 'exists':
        changed1 = edit_file('/etc/selinux/config', replace_line(r'\s*SELINUX\s*=\s*.*', 'SELINUX=disabled'))
    else:
        changed1 = False
    if run('if [ -e /usr/sbin/setenforce ] && [ -e /usr/sbin/getenforce ] ; then echo exists ; fi') == 'exists':
        changed2 = run('STATUS=$(getenforce) ; if [ "$STATUS" == "Enforcing" ] ; then setenforce 0 ; echo perm ; fi') == 'perm'
    else:
        changed2 = False
    return changed1 or changed2


def systemctl_start(name):
    """systemctl start ``name``.
    """
    run('systemctl daemon-reload ; systemctl start ' + name + ' ; systemctl daemon-reload')


def systemctl_stop(name):
    """systemctl stop ``name``.
    """
    run('systemctl daemon-reload ; systemctl stop ' + name + ' ; systemctl daemon-reload')


def systemctl_reload(name):
    """systemctl reload ``name``.
    """
    run('systemctl daemon-reload ; systemctl reload ' + name + ' ; systemctl daemon-reload')


def systemctl_restart(name):
    """systemctl restart ``name``.
    """
    run('systemctl daemon-reload ; systemctl restart ' + name + ' ; systemctl daemon-reload')


def systemctl_enable(name):
    """systemctl enable ``name``.
    """
    run('systemctl daemon-reload ; systemctl enable ' + name + ' ; systemctl daemon-reload')


def systemctl_disable(name):
    """systemctl disable ``name``.
    """
    run('systemctl daemon-reload ; systemctl disable ' + name + ' ; systemctl daemon-reload')


def systemctl_mask(name):
    """systemctl mask ``name``.
    """
    run('systemctl daemon-reload ; systemctl mask ' + name + ' ; systemctl daemon-reload')


def systemctl_unmask(name):
    """systemctl unmask ``name``.
    """
    run('systemctl daemon-reload ; systemctl unmask ' + name + ' ; systemctl daemon-reload')


def systemctl_preset(name):
    """systemctl preset ``name``.
    """
    run('systemctl daemon-reload ; systemctl preset ' + name + ' ; systemctl daemon-reload')


def systemctl_edit(name, override):
    """systemctl edit ``name``.

    Works like command ``systemctl edit name``. Creates directory ``/etc/systemd/system/${name}.d``
    and creates file ``override.conf`` inside it with contents from string override.

    Args:
        name: Name of systemd service to edit.
        override: Which text place inside ``override.conf`` file.
            Leading and trailing whitespace chars are stripped from override.

    Returns:
        True if file ``override.conf`` for service ``name`` changed, False otherwise.
    """
    if override is None:
        override = ''
    if not isinstance(override, basestring):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('systemctl_edit: override must be string in file %s line %s' % (fname, nline))
    if '/' in name:
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('systemctl_edit: invalid unit name \'%s\' in file %s line %s' % (name, fname, nline))
    if not name.endswith('.service'):
        name = name + '.service'
    override_dir = '/etc/systemd/system/' + name + '.d'
    override_conf = os.path.join(override_dir, 'override.conf')
    override = strip_text(override)
    if override:
        changed1 = create_directory(override_dir)
        changed2 = write_file(override_conf, override)
    else:
        changed1 = remove_file(override_conf)
        changed2 = remove_directory(override_dir)
    return changed1 or changed2


def systemctl_get_default():
    """systemctl get-default.

    Returns:
        Output of command ``systemctl get-default``.
    """
    return run('systemctl daemon-reload ; systemctl get-default ; systemctl daemon-reload')


def systemctl_set_default(name):
    """systemctl set-default ``name``.

    For example, ``systemctl_set_default('multi-user.target')``

    """
    return run('systemctl daemon-reload ; systemctl set-default ' + name + ' ; systemctl daemon-reload')


def localectl_set_locale(locale):
    """localectl set-locale ``name``.

    For example, ``localectl_set_locale('LANG=en_US.UTF-8')``.

    """
    return run('localectl set-locale ' + locale)


def timedatectl_set_timezone(timezone):
    """timedatectl set-timezone ``timezone``.

    For example, ``timedatectl_set_timezone('Europe/Kiev')``.

    """
    return run('timedatectl set-timezone ' + timezone)


def get_virtualization_type():
    """Get virtualization type.

    Returns:
        None if no vitrualization detected, or vitrualization type as string, for example, "openvz" or "kvm" or something else.
    """
    stdout = run('hostnamectl status')
    virtualization_type = None
    virtualization_line_regexp = re.compile(r'^\s*Virtualization:\s(?P<virtualization_type>\w+)\s*$')
    for line in stdout.split('\n'):
        match = virtualization_line_regexp.match(line)
        if match:
            virtualization_type = match.group('virtualization_type')
            break
    return virtualization_type
