.. meta::
    :description: Fabrix API Documentation

API Documentation
=================

.. toctree::
    :maxdepth: 2
    :hidden:

    api-documentation/config
    api-documentation/editor
    api-documentation/ioutil
    api-documentation/render
    api-documentation/rpmyum
    api-documentation/system

----------------------------------------

**Configuration**
  - :obj:`~fabrix.config.conf`
  - :obj:`~fabrix.config.local_conf`
  - :func:`~fabrix.config.read_config`

----------------------------------------

**Editor functions**
  - :func:`~fabrix.editor.append_line`
  - :func:`~fabrix.editor.delete_line`
  - :func:`~fabrix.editor.edit_file`
  - :func:`~fabrix.editor.edit_ini_section`
  - :func:`~fabrix.editor.edit_local_file`
  - :func:`~fabrix.editor.edit_text`
  - :func:`~fabrix.editor.insert_line`
  - :func:`~fabrix.editor.prepend_line`
  - :func:`~fabrix.editor.replace_line`
  - :func:`~fabrix.editor.strip_line`
  - :func:`~fabrix.editor.strip_text`
  - :func:`~fabrix.editor.substitute_line`

----------------------------------------

**Input/Output functions**
  - :func:`~fabrix.ioutil.chmod`
  - :func:`~fabrix.ioutil.chown`
  - :func:`~fabrix.ioutil.copy_file`
  - :func:`~fabrix.ioutil.create_directory`
  - :func:`~fabrix.ioutil.debug`
  - :func:`~fabrix.ioutil.hide_run`
  - :func:`~fabrix.ioutil.read_file`
  - :func:`~fabrix.ioutil.read_local_file`
  - :func:`~fabrix.ioutil.remove_directory`
  - :func:`~fabrix.ioutil.remove_file`
  - :func:`~fabrix.ioutil.rsync`
  - :func:`~fabrix.ioutil.write_file`
  - :func:`~fabrix.ioutil.write_local_file`

----------------------------------------

**Template rendering**
  - :func:`~fabrix.render.render`
  - :func:`~fabrix.render.render_template`

----------------------------------------

**Package management**
  - :func:`~fabrix.rpmyum.yum_install`
  - :func:`~fabrix.rpmyum.yum_remove`
  - :func:`~fabrix.rpmyum.yum_update`

----------------------------------------

**System management**
  - :func:`~fabrix.system.disable_selinux`
  - :func:`~fabrix.system.get_virtualization_type`
  - :func:`~fabrix.system.is_reboot_required`
  - :func:`~fabrix.system.localectl_set_locale`
  - :func:`~fabrix.system.reboot_and_wait`
  - :func:`~fabrix.system.systemctl_disable`
  - :func:`~fabrix.system.systemctl_edit`
  - :func:`~fabrix.system.systemctl_enable`
  - :func:`~fabrix.system.systemctl_get_default`
  - :func:`~fabrix.system.systemctl_mask`
  - :func:`~fabrix.system.systemctl_reload`
  - :func:`~fabrix.system.systemctl_restart`
  - :func:`~fabrix.system.systemctl_set_default`
  - :func:`~fabrix.system.systemctl_start`
  - :func:`~fabrix.system.systemctl_stop`
  - :func:`~fabrix.system.systemctl_unmask`
  - :func:`~fabrix.system.timedatectl_set_timezone`

----------------------------------------

