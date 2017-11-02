import re
import time
import inspect
import os.path
from fabric.state import connections
from fabric.api import run, settings, hide, quiet, env, abort
from fabrix.editor import edit_file, replace_line, strip_text
from fabrix.ioutil import remove_file, remove_directory, create_directory, write_file


def is_reboot_required():
    with quiet():
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
    # Shorter timeout for a more granular cycle than the default.
    timeout = 3
    # Use 'wait' as max total wait time
    attempts = int(round(float(wait) / float(timeout)))
    # Don't bleed settings, since this is supposed to be self-contained.
    # User adaptations will probably want to drop the "with settings()" and
    # just have globally set timeout/attempts values.
    with settings(
        hide('running'),
        timeout=timeout,
        connection_attempts=attempts
    ):
        print 'Rebooting %s...' % env.host_string
        with quiet():
            run(command)
        # Try to make sure we don't slip in before pre-reboot lockdown
        time.sleep(5)
        print 'Waiting for %s...' % env.host_string
        # This is actually an internal-ish API call, but users can simply drop
        # it in real fabfile use -- the next run/sudo/put/get/etc call will
        # automatically trigger a reconnect.
        # We use it here to force the reconnect while this function is still in
        # control and has the above timeout settings enabled.
        connections.connect(env.host_string)
    # At this point we should be reconnected to the newly rebooted server.


def disable_selinux():
    changed1 = False
    changed2 = False
    with settings(hide('everything')):
        if run('if [ -e /etc/selinux/config ] ; then echo exists ; fi') == 'exists':
            changed1 = edit_file('/etc/selinux/config', replace_line('\s*SELINUX\s*=\s*.*', 'SELINUX=disabled'))
        if run('if [ -e /usr/sbin/setenforce ] && [ -e /usr/sbin/getenforce ] ; then echo exists ; fi') == 'exists':
            changed2 = run('STATUS=$(getenforce) ; if [ "$STATUS" == "Enforcing" ] ; then setenforce 0 ; echo perm ; fi') == 'perm'
    return changed1 or changed2


def systemctl_start(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl start ' + name + ' ; systemctl daemon-reload')


def systemctl_stop(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl stop ' + name + ' ; systemctl daemon-reload')


def systemctl_reload(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl reload ' + name + ' ; systemctl daemon-reload')


def systemctl_restart(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl restart ' + name + ' ; systemctl daemon-reload')


def systemctl_enable(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl enable ' + name + ' ; systemctl daemon-reload')


def systemctl_disable(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl disable ' + name + ' ; systemctl daemon-reload')


def systemctl_mask(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl mask ' + name + ' ; systemctl daemon-reload')


def systemctl_unmask(name):
    with settings(hide('everything')):
        run('systemctl daemon-reload ; systemctl unmask ' + name + ' ; systemctl daemon-reload')


def systemctl_edit(name, override):
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
        return changed1 or changed2
    else:
        changed1 = remove_file(override_conf)
        changed2 = remove_directory(override_dir)
        return changed1 or changed2


def systemctl_get_default():
    with settings(hide('everything')):
        return run('systemctl daemon-reload ; systemctl get-default ; systemctl daemon-reload')


def systemctl_set_default(name):
    with settings(hide('everything')):
        return run('systemctl daemon-reload ; systemctl set-default ' + name + ' ; systemctl daemon-reload')


def localectl_set_locale(locale):
    with settings(hide('everything')):
        return run('localectl set-locale ' + locale)


def timedatectl_set_timezone(timezone):
    with settings(hide('everything')):
        return run('timedatectl set-timezone ' + timezone)


def get_virtualization_type():
    with settings(hide('everything')):
        stdout = run('hostnamectl status')
    virtualization_type = None
    virtualization_line_regexp = re.compile(r'^\s*Virtualization:\s(?P<virtualization_type>\w+)\s*$')
    for line in stdout.split('\n'):
        match = virtualization_line_regexp.match(line)
        if match:
            virtualization_type = match.group('virtualization_type')
            break
    return virtualization_type
