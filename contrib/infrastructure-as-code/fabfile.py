"""

expected bare metal server with two empty partitions /dev/sda4 and /dev/sdb4
disks patitioning should be created with create-server-partitions/fabfile.py

roles
=====

hardware-node
-------------

- install CentOS 7.x KVM+ZFS hardware node
    with x1vnc gui on 127.0.0.1:5977 port
    using Xfce and Virtual Machine Manager
    use ssh port forwarding to access GUI

virtual-machine
---------------

- install CentOS 7.x virtual machines

virtual-machine-with-docker
---------------------------

- install CentOS 7.x virtual machines with docker

variables
=========

sshd_alternate_port
-------------------

- if set ssh will be lisen on port 22 and sshd_alternate_port

hostname
--------

- hostname will be set via hostnamectl set-hostname

timezone
--------

- server timezone

locale
------

- server locale

postfix_mail_root_alias
-----------------------

- root alias will be used in e/tc/aliases file

sshd_authorized_keys
--------------------

- add keys to /root/.ssh/authorized_keys

sshd_disable_password_authentication
------------------------------------

- disable sshd password authentication?

remove_selinux_policy
---------------------

- should be false if docker used

P.S.

after installation of hardware node and virtual machines
network settings and iptables settings should be tuned manually.

"""


from fabric.api import parallel, task, execute, roles, abort
from fabrix.api import run, yum_install, yum_update, yum_remove, is_reboot_required, reboot_and_wait, disable_selinux
from fabrix.api import copy_file, edit_file, replace_line, substitute_line, strip_line, is_file_not_exists
from fabrix.api import edit_ini_section, systemctl_stop, systemctl_enable, systemctl_start, systemctl_restart
from fabrix.api import append_line, chmod, insert_line, systemctl_preset, remove_file, conf, name, warn
from fabrix.api import read_local_file, create_directory, create_file, write_file, strip_text
from fabrix.api import systemctl_disable, get_virtualization_type, localectl_set_locale
from fabrix.api import timedatectl_set_timezone, systemctl_set_default, is_file_exists
from fabrix.api import remove_directory


__author__ = "Gena Makhomed"
__contact__ = "https://github.com/makhomed/fabrix"
__license__ = "GPLv3"
__version__ = "0.0.1"
__date__ = "2017-11-13"


def tune_sshd_service():
    name("tune sshd service")
    changed1 = edit_file("/etc/ssh/sshd_config",
        replace_line("#?UseDNS yes", "UseDNS no"),
        replace_line("X11Forwarding yes", "X11Forwarding no"),
        replace_line("#Port 22", "Port 22"),
        replace_line("#AddressFamily any", "AddressFamily inet")
    )
    sshd_alternate_port = conf.get('sshd_alternate_port')
    if sshd_alternate_port:
        name("add ssh alternate port %d" % sshd_alternate_port)
        port_line = "Port %d" % sshd_alternate_port
        changed2 = edit_file("/etc/ssh/sshd_config",
            insert_line(port_line, after="Port 22"),
        )
    else:
        changed2 = False
    sshd_authorized_keys = conf.get('sshd_authorized_keys')
    if sshd_authorized_keys:
        name("append public keys to /root/.ssh/authorized_keys")
        create_directory("/root/.ssh")
        chmod("/root/.ssh", 0700)
        create_file("/root/.ssh/authorized_keys")
        chmod("/root/.ssh/authorized_keys", 0600)
        keys = read_local_file(sshd_authorized_keys)
        for key in keys.split("\n"):
            key = key.strip()
            if key == "":
                continue
            edit_file("/root/.ssh/authorized_keys",
                append_line(key, insert_empty_line_before=True)
            )
    if conf.get("sshd_disable_password_authentication"):
        name("ssh disable password authentication")
        if not conf.get('sshd_authorized_keys'):
            abort("sshd_authorized_keys must be set first")
        changed3 = edit_file("/etc/ssh/sshd_config",
                replace_line("PasswordAuthentication yes", "PasswordAuthentication no")
        )
    else:
        changed3 = False
    if changed1 or changed2 or changed3:
        name("restart sshd service")
        systemctl_restart("sshd")


def tune_base_system():  # pylint: disable=too-many-branches,too-many-statements
    virtualization_type = get_virtualization_type()
    name("tune base system")
    disable_selinux()
    if virtualization_type == "kvm":
        name("kvm detected, remove microcode_ctl package")
        yum_remove("microcode_ctl")
        name("kvm detected, install qemu-guest-agent")
        yum_install("qemu-guest-agent")
    name("yum update")
    changed = yum_update()
    if changed and is_reboot_required():
        name("reboot")
        reboot_and_wait()
    locale = conf.get("locale")
    if locale:
        name("set locale")
        localectl_set_locale(locale)
    else:
        warn("locale not defined")
    timezone = conf.get("timezone")
    if timezone:
        name("set timezone")
        timedatectl_set_timezone(timezone)
    else:
        warn("timezone not defined")
    name("set multi-user.target as default target")
    systemctl_set_default("multi-user.target")
    name("install base packages")
    yum_install("mc vim screen net-tools mailx wget traceroute mtr chrony rsync")
    name("tune mc")
    copy_file("mc.ini", "/usr/share/mc/mc.ini")
    name("tune vim")
    copy_file("vimrc", "/etc/vimrc")
    copy_file("vim-default-editor.sh", "/etc/profile.d/vim-default-editor.sh")
    if conf.get('remove_selinux_policy'):
        name("remove selinux-policy")
        yum_remove(r"selinux-policy\*")
        run("rm -rf /etc/selinux/final")
        run("rm -rf /etc/selinux/targeted")
        run("rm -rf /etc/selinux/tmp")
    name("tune /etc/default/grub")
    changed = edit_file("/etc/default/grub",
        replace_line(r"GRUB_TIMEOUT=.*", r"GRUB_TIMEOUT=1"),
        replace_line(r"(GRUB_CMDLINE_LINUX=.*)\brhgb\b(.*)", r"\1selinux=0\2"),
        replace_line(r"(GRUB_CMDLINE_LINUX=.*)\bquiet\b(.*)", r"\1panic=1\2"),
        substitute_line(r"\s+", r" "),
        strip_line(),
    )
    if changed:
        name("grub2-mkconfig -o /boot/grub2/grub.cfg")
        run("grub2-mkconfig -o /boot/grub2/grub.cfg")

    if is_file_not_exists("/usr/bin/htop"):
        name("install htop")
        yum_install("epel-release")
        yum_install("htop")

    name("make chronyd listed only on ipv4 socket")
    changed = edit_file("/etc/sysconfig/chronyd",
        replace_line('OPTIONS=""', 'OPTIONS="-4"')
    )
    if changed:
        systemctl_restart("chronyd.service")
    if is_file_exists("/usr/bin/firewall-cmd"):
        name("remove firewalld service")
        systemctl_stop("firewalld")
        yum_remove("firewalld")
        remove_file("/var/log/firewalld")
    if is_file_not_exists("/usr/lib/systemd/system/iptables.service"):
        name("install iptables services")
        yum_install("iptables-services")
        systemctl_enable("iptables")
        systemctl_start("iptables")
    if is_file_not_exists("/usr/sbin/acpid"):
        name("install acpid")
        yum_install("acpid")
        systemctl_enable("acpid")
        systemctl_start("acpid")

    name("disable useless services")
    systemctl_disable("rpcbind.socket rpcbind.service")
    name("remove useless packages")
    yum_remove("btrfs-progs teamd wpa_supplicant")
    remove_directory("/var/log/rhsm")

    hostname = conf.get("hostname")
    if hostname:
        name("set hostname to %s" % hostname)
        run("hostnamectl set-hostname %s" % hostname)
    else:
        warn("hostname not defined")

    postfix_mail_root_alias = conf.get("postfix_mail_root_alias")
    if postfix_mail_root_alias:
        name("postfix set root alias %s" % postfix_mail_root_alias)
        changed = edit_file("/etc/aliases",
            replace_line(r"#root:\s+marc", "root:\t\t%s" % postfix_mail_root_alias)
        )
        if changed:
            run("newaliases")
    else:
        warn("postfix_mail_root_alias not defined")
    name("tune postfix")
    changed = edit_file("/etc/postfix/main.cf",
        replace_line(r"\s*inet_protocols\s*=\s*all\s*", "inet_protocols = ipv4")
    )
    if changed:
        name("restart postfix")
        systemctl_restart("postfix")
    name("apply workaround for bug https://bugzilla.redhat.com/show_bug.cgi?id=1499367")
    changed = edit_file("/usr/lib/systemd/system/ip6tables.service",
        replace_line("After=syslog.target,iptables.service", "After=syslog.target iptables.service")
    )
    if changed:
        run("systemctl daemon-reload")
    name("tune /etc/fstab")
    if virtualization_type == "kvm":
        edit_file("/etc/fstab",
            substitute_line(r"defaults(\s)", r"defaults,discard,noatime\1")
        )
        name("enable fstrim cron")
        write_file("/etc/cron.d/fstrim", strip_text("""
            #
            # this file automatically generated by fabrix, do not edit manually
            #

            55 23 * * * root /sbin/fstrim /
        """))
    if virtualization_type is None:
        edit_file("/etc/fstab",
            substitute_line(r"defaults(\s)", r"defaults,noatime\1")
        )
        name("install smartmontools")
        yum_install("smartmontools")
        systemctl_enable("smartd")
        systemctl_start("smartd")


def hardware_node_install_zfs():
    name("install zfs")

    def get_zfs_partitions_id():
        out = run("cd /dev/disk/by-id/ ; for i in * ; do echo $i $(readlink $i) ; done")
        sda_part = None
        sdb_part = None
        for line in out.split("\n"):
            line = line.strip()
            part, link = line.split()
            if part.startswith("wwn-"):
                continue
            if link == "../../sda4":
                sda_part = part
            if link == "../../sdb4":
                sdb_part = part
        return sda_part, sdb_part

    # https://github.com/zfsonlinux/zfs/wiki/RHEL-and-CentOS#kabi-tracking-kmod
    name("enable zfs-kmod repo")
    if is_file_not_exists("/etc/yum.repos.d/zfs.repo"):
        yum_install("http://download.zfsonlinux.org/epel/zfs-release.el7_4.noarch.rpm")
    edit_file("/etc/yum.repos.d/zfs.repo",
        edit_ini_section("[zfs]",
            replace_line("enabled=1", "enabled=0")
        ),
        edit_ini_section("[zfs-kmod]",
            replace_line("enabled=0", "enabled=1")
        ),
    )
    name("install zfs packages")
    yum_install("zfs")
    run("/sbin/modprobe zfs")
    name("apply workaround for bug https://github.com/zfsonlinux/zfs/issues/6838")
    systemctl_preset("zfs-import-cache.service zfs-import-scan.service zfs-mount.service zfs-share.service zfs-zed.service zfs.target")
    if run("zpool list") == "no pools available":
        sda_part, sdb_part = get_zfs_partitions_id()
        name("create zpool on %s and %s" % (sda_part, sdb_part))
        run("zpool create -o ashift=12 -O compression=lz4 -O atime=off -O xattr=sa -O acltype=posixacl tank mirror %s %s" % (sda_part, sdb_part))
    name("set disk scheduler to noop")
    changed = edit_file("/etc/rc.d/rc.local",
        append_line("echo noop > /sys/block/sda/queue/scheduler", insert_empty_line_before=True),
        append_line("echo noop > /sys/block/sdb/queue/scheduler"),
    )
    chmod("/etc/rc.d/rc.local", "+x")
    if changed:
        run("/etc/rc.d/rc.local")
    name("disable lvm scan zvols")
    edit_file("/etc/lvm/lvm.conf",
        insert_line("\t" + r'global_filter = ["r|/dev/zd.*|", "a|.*|"]', after=r'\s*# global_filter = \[ "a\|\.\*/\|" \]')
    )


def hardware_node_install_kvm():
    name("install kvm")
    run("tuned-adm profile virtual-host")
    yum_install("centos-release-qemu-ev")
    yum_install("qemu-kvm-ev qemu-kvm-tools-ev virt-top perf")
    name("install libvirt and virt-manager")
    yum_install("virt-manager libvirt")
    systemctl_start("libvirtd")
    name("install virtual X server and x11vnc")
    yum_install("xorg-x11-server-Xvfb x11vnc psmisc")
    name("install Xfce")
    yum_install("""
        xfce4-session
        xfwm4
        xfdesktop
        xfce4-settings
        xfce4-appfinder
        tumbler
        abattis-cantarell-fonts
        liberation-sans-fonts
        liberation-fonts-common
        xfce4-terminal
    """)
    name("enable x11vnc service")
    write_file("/etc/systemd/system/x11vnc.service", strip_text("""
        [Unit]
        Description=x11vnc service

        [Service]
        User=root
        PrivateTmp=true
        ProtectSystem=full
        Environment=FD_SESS=xfce X11VNC_CREATE_GEOM=1270x920x24 X11VNC_CREATE_STARTING_DISPLAY_NUMBER=77
        ExecStart=/usr/bin/x11vnc -noipv6 -rfbportv6 5977 -no6 -q -localhost -rfbport 5977 -nopw -create -ping 60 -gone 'killall Xvfb'
        Restart=always

        [Install]
        WantedBy=multi-user.target
    """))
    run("systemctl daemon-reload")
    systemctl_enable("x11vnc")
    systemctl_start("x11vnc")
    # https://fedoraproject.org/wiki/Windows_Virtio_Drivers
    if is_file_not_exists("/etc/yum.repos.d/virtio-win.repo"):
        name("enable virtio-win repo")
        run("curl --silent --output /etc/yum.repos.d/virtio-win.repo --remote-time https://fedorapeople.org/groups/virt/virtio-win/virtio-win.repo")
    name("install virtio-win")
    yum_install("virtio-win")
    if "default" in run("virsh net-list"):
        name("disable libvirtd default network")
        run("virsh net-destroy default")
        run("virsh net-undefine default")
    if "default" in run("virsh pool-list"):
        name("disable libvirtd default pool")
        run("virsh pool-destroy default")
        run("virsh pool-undefine default")
    name("disable dnsmasq service")
    systemctl_stop("dnsmasq")
    systemctl_disable("dnsmasq")
    name("enable libvirt-guests service")
    edit_file("/etc/sysconfig/libvirt-guests",
        replace_line("#ON_BOOT=start", "ON_BOOT=start"),
        replace_line("#START_DELAY=0", "START_DELAY=0"),
        replace_line("#ON_SHUTDOWN=suspend", "ON_SHUTDOWN=shutdown"),
        replace_line("#PARALLEL_SHUTDOWN=0", "PARALLEL_SHUTDOWN=777"),
        replace_line("#SHUTDOWN_TIMEOUT=300", "SHUTDOWN_TIMEOUT=300"),
    )
    systemctl_enable("libvirt-guests")
    systemctl_start("libvirt-guests")
    changed = write_file("/etc/sysctl.d/kvm.conf", strip_text("""
        # enable IPv4 forwarding
        net.ipv4.ip_forward = 1
    """))
    if changed:
        name("enable IPv4 forwarding")
        run("sysctl -p /etc/sysctl.d/kvm.conf")


def install_docker():
    name("install docker")
    create_directory("/etc/docker")
    if is_file_not_exists("/etc/docker/daemon.json"):
        name("create /etc/docker/daemon.json config")
        write_file("/etc/docker/daemon.json", strip_text("""
            {
                "bip": "172.29.0.1/16",
                "log-driver": "syslog",
                "storage-driver": "devicemapper",
                "storage-opts": [ "dm.directlvm_device=/dev/sdb" ]
            }
        """))
    # https://docs.docker.com/engine/installation/linux/docker-ce/centos/
    if is_file_not_exists("/etc/yum.repos.d/docker-ce.repo"):
        name("enable docker-ce repo")
        run("curl --silent --output /etc/yum.repos.d/docker-ce.repo --remote-time https://download.docker.com/linux/centos/docker-ce.repo")
    name("install docker dependencies")
    yum_install("device-mapper-persistent-data lvm2")
    name("install docker package")
    yum_install("docker-ce")
    name("start docker service")
    systemctl_enable("docker")
    systemctl_start("docker")


@task
@parallel
@roles("hardware-node")
def install_hardware_nodes():
    tune_sshd_service()
    tune_base_system()
    hardware_node_install_zfs()
    hardware_node_install_kvm()


@task
@parallel
@roles("virtual-machine")
def install_vms():
    tune_sshd_service()
    tune_base_system()


@task
@parallel
@roles("virtual-machine-with-docker")
def install_vms_with_docker():
    tune_sshd_service()
    tune_base_system()
    install_docker()


@task(default=True)
@parallel
def install_all():
    execute(install_hardware_nodes)
    execute(install_vms)
    execute(install_vms_with_docker)
