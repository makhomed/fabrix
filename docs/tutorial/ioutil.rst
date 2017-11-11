.. meta::
    :description: Fabrix input/output functions tutorial

.. _tutorial-ioutil:

Input/Output functions
----------------------

We able to check :func:`~fabrix.ioutil.is_file_exists`
and :func:`~fabrix.ioutil.is_directory_exists`.

Also we can do reverse check :func:`~fabrix.ioutil.is_file_not_exists`
and :func:`~fabrix.ioutil.is_directory_not_exists`.

Also Fabrix provide functions :func:`~fabrix.ioutil.remove_file`
and :func:`~fabrix.ioutil.remove_directory` for deleting files and empty directories.

Also we can create empty files with function :func:`~fabrix.ioutil.create_file`
and empty directories with function :func:`~fabrix.ioutil.create_directory`.

Also we can change owner, group and mode of file or directory with functions
:func:`~fabrix.ioutil.chown` and :func:`~fabrix.ioutil.chmod`.

We can read and write local files with functions :func:`~fabrix.ioutil.read_local_file`
and :func:`~fabrix.ioutil.write_local_file`.

Also we can read and write remote files with functions
:func:`~fabrix.ioutil.read_file` and :func:`~fabrix.ioutil.write_file`.

We can copy files from local host to remote host with function
:func:`~fabrix.ioutil.copy_file`.

Or even recursively copy files and directories from local host
to remote host with function :func:`~fabrix.ioutil.rsync`.

With function :func:`~fabrix.ioutil.name` you can print pretty one-line description
about running action. For example, ``fabfile.py``:

.. code-block:: python

    from fabrix.api import name, systemctl_stop, yum_remove, remove_file
    from fabrix.api import yum_install, systemctl_enable, systemctl_start

    def install_server():
        name("install iptables")
        systemctl_stop("firewalld")
        yum_remove("firewalld")
        remove_file("/var/log/firewalld")
        yum_install("iptables-services")
        systemctl_enable("iptables")
        systemctl_start("iptables")

        name("install acpid")
        yum_install("acpid")
        systemctl_enable("acpid")
        systemctl_start("acpid")

Running this fabfile on host ``example.com`` will produce output:

.. code-block:: bash

    $ fab install_server
    [example.com] Executing task 'install_server'
    [example.com] * install iptables
    [example.com] * install acpid

Function :func:`~fabrix.ioutil.run` designed to use with function :func:`~fabrix.ioutil.name`.
Function :func:`~fabrix.ioutil.run` run commands on remote host with settings hide('running', 'stdout', 'stderr').

Also Fabrix provides helper function :func:`~fabrix.ioutil.debug_print`
to print debug messages if debug mode is enabled.

.. seealso::
    :ref:`Input/Output functions Reference <reference-ioutil>`

