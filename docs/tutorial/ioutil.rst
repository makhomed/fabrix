.. meta::
    :description: Fabrix input/output functions tutorial

.. _tutorial-ioutil:

Input/Output functions
----------------------

We able to check :func:`~fabrix.ioutil.is_file_exists`
and :func:`~fabrix.ioutil.is_directory_exists`.

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

Also Fabrix provides two helper functions :func:`~fabrix.ioutil.debug`
to print debug messages if debug mode is enabled and :func:`~fabrix.ioutil.hide_run`
for run commands on remote host with settings hide("everything").

.. seealso::
    :ref:`Input/Output functions Reference <reference-ioutil>`

