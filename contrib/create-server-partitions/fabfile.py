"""

create partitions on bare metal server for zfs storage

expected bare metal server with two *empty* HDDs /dev/sda and /dev/sdb in LiveCD mode

$ fab server_create_partitions

create partitions, /boot mdraid and LVM volumes on top of mdraid:

GPT:
/dev/sda1, /dev/sdb1 -    2014s - bios_grub partitions
/dev/sda2, /dev/sdb2 -    1 GiB - /dev/md0, /boot
/dev/sda3, /dev/sdb3 -   32 GiB - /dev/md1, LVM
/dev/sda4, /dev/sdb4 - all rest - for zfs zpool

LVM:
 opt - 8 GiB
root - 8 GiB
 tmp - 8 GiB
 var - 8 GiB

"""


import fabric.api
from fabric.api import task, abort, prompt, settings


__author__ = "Gena Makhomed"
__contact__ = "https://github.com/makhomed/fabrix"
__license__ = "GPLv3"
__version__ = "0.0.3"
__date__ = "2017-11-15"


def run(*args, **kwargs):
    with settings(fabric.api.hide('running', 'stdout', 'stderr')):
        return fabric.api.run(*args, shell=False, **kwargs)


def is_live_cd():
    out = run("mount")
    lines = out.split("\n")
    for line in lines:
        if line.startswith("overlay on / type overlay"):
            return True
    return False


class Parted(object):
    # blockdev --getsize64 /dev/sda returns size in bytes
    # blockdev --getsize /dev/sda returns size in sectors
    # blockdev --getss /dev/sdd - sectir size, 512
    # blockdev --getbsz /dev/sdd - block size, 4096
    # mdadm -E /dev/sdc2
    def __init__(self, *devices):
        self.devices = devices
        self.offset = 34
        self.part_index = 1
        self.partitions = list()
        self.label_created = False

    def _mdraid_metadata_size_in_sectors(self, data_size_in_sectors):  # pylint: disable=no-self-use
        """Return mdraid metadata size in sectors for data_size_in_sectors
           metadata size is at least 1Mib for alignment
           metadata size is 0.1% of data size, but no more than 128MiB.
        """
        assert data_size_in_sectors > 0
        headroom = 128 * 1024 * 2
        while (headroom << 10) > data_size_in_sectors:
            headroom >>= 1
        data_offset = 12 * 2 + headroom
        one_meg = 2 * 1024
        if data_offset < one_meg:
            data_offset = one_meg
        if data_offset > one_meg:
            data_offset = (data_offset / one_meg) * one_meg
        return data_offset

    def _lvm_metadata_size_in_sectors(self, data_size_in_sectors):  # pylint: disable=no-self-use
        assert data_size_in_sectors > 0
        return 2048

    def mkpart(self, description, data_size_in_sectors, mdraid, lvm):
        if data_size_in_sectors == -1:
            start = self.offset
            end = -34
            self.offset = 2**128 - 1
        else:
            if mdraid:
                data_size_in_sectors += self._mdraid_metadata_size_in_sectors(data_size_in_sectors)
            if lvm:
                data_size_in_sectors += self._lvm_metadata_size_in_sectors(data_size_in_sectors)
            start = self.offset
            end = self.offset + data_size_in_sectors - 1
            self.offset = self.offset + data_size_in_sectors
        part = (self.part_index, start, end, description)
        self.partitions.append(part)
        self.part_index = self.part_index + 1

    def check_alignment(self, align_in_sectors=2048):
        print
        print 'check partition align at %dKiB:' % (align_in_sectors / 2)
        print '----------------------------'
        for device in self.devices:
            for part_index, start, dummy_end, dummy_description in self.partitions:
                if start % align_in_sectors == 0:
                    print "    partition %s%d aligned" % (device, part_index)
                else:
                    print "    partition %s%d NOT aligned" % (device, part_index)

    def _commit(self, print_only):
        print
        for device in self.devices:
            if print_only:
                print "parted -s /dev/%s mklabel gpt" % device
            else:
                run("parted -s /dev/%s mklabel gpt" % device)
        print
        for device in self.devices:
            for dummy_part_index, start, end, dummy_description in self.partitions:
                if print_only:
                    print "parted -s /dev/%s -a min -- mkpart primary %ds %ds" % (device, start, end)
                else:
                    run("parted -s /dev/%s -a min -- mkpart primary %ds %ds" % (device, start, end))
            print

    def out(self):
        self._commit(print_only=True)

    def run(self):
        self._commit(print_only=False)


def is_disks_has_no_partitions():
    out = run("lsblk --noheadings --output NAME")
    devices = set()
    for device in out.split("\n"):
        devices.add(device.strip())
    return devices == set(['loop0', 'sda', 'sdb'])


def create_partitions():
    parted = Parted('sda', 'sdb')
    parted.mkpart('for bios_grub', 2014, mdraid=False, lvm=False)
    parted.mkpart('for  /dev/md0', 01 * 1024 * 1024 * 1024 / 512, mdraid=True, lvm=False)
    parted.mkpart('for  /dev/md1', 32 * 1024 * 1024 * 1024 / 512, mdraid=True, lvm=True)
    parted.mkpart('for zfs zpool', -1, mdraid=False, lvm=False)
    parted.run()

    run("parted -s /dev/sda -- set 1 bios_grub on")
    run("parted -s /dev/sdb -- set 1 bios_grub on")

    run("parted -s /dev/sda -- set 2 raid on")
    run("parted -s /dev/sdb -- set 2 raid on")

    run("parted -s /dev/sda -- set 3 raid on")
    run("parted -s /dev/sdb -- set 3 raid on")

    run("mdadm --create /dev/md0 --level=mirror --raid-devices=2 /dev/sda2 /dev/sdb2 --metadata=1.2")
    run("mdadm --create /dev/md1 --level=mirror --raid-devices=2 /dev/sda3 /dev/sdb3 --metadata=1.2")
    run("pvcreate /dev/md1")

    run("vgcreate lv /dev/md1")

    run("lvcreate -n  opt -L 8G lv")
    run("lvcreate -n root -L 8G lv")
    run("lvcreate -n  tmp -L 8G lv")
    run("lvcreate -n  var -L 8G lv")


@task
def server_remove_partitions():
    if not is_live_cd():
        abort("This server not in LiveCD mode, can't remove partitions")

    if is_disks_has_no_partitions():
        abort("Server disks already have NO partitions, nothing to do")

    print
    reply = prompt("\n\nDelete ALL partitions from ALL drives?\n\nEnter 'I AGREE' if you want this:")
    if reply != "I AGREE":
        print "Nothing to do"
        return

    for device in ['sda', 'sdb']:
        for part_index in [4, 3, 2, 1]:
            with settings(warn_only=True):
                run("parted -s /dev/%s -- rm %d" % (device, part_index))


@task
def server_create_partitions():
    if not is_live_cd():
        abort("This server not in LiveCD mode, can't create partitions")

    if not is_disks_has_no_partitions():
        abort("Server disks already have partitions")

    create_partitions()
