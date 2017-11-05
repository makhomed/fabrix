
Version 0.2
-----------

Released: 07 Nov 2017

- fixed bug in detection of invalid yaml files in read_config
- fixed bug in detection of duplicated sections in ini_section_editor
- fixed bug in detection of empty string in hosts list in read_config
- fixed bug in detection of empty string in roles role name in read_config
- fixed bug in detection of empty string in roles hosts list in read_config
- fixed bug in detection of empty string in host_vars host name in read_config
- fixed bug in detection of empty string in role_vars role name in read_config
- fixed bug in append_line if last line of text does not end with newline char
- fixed bug in render_template, now last newline char not stripped by jinja2
- fixed bugs in mv / stat / ... calls for file names started with '-' symbol
- all writes to local/remote files preserve extended attributes of these files
- conf now provides all correct methods to work like Python built-in dict type
- render_template now use conf/local_conf variables as context default values
- add fabfile file name and fabfile line number to error messages if possible
- rename functions {edit,read,write}_remote_file to {edit,read,write}_file
- added new functions copy_file(), rsync(), chown(), chmod()
- added new functions yum_install(), yum_remove(), yum_update()
- added new functions is_reboot_required(), reboot_and_wait()
- added new functions disable_selinux(), hide_run(), systemctl_edit()
- added new functions systemctl_enable(), systemctl_disable()
- added new functions systemctl_mask(), systemctl_unmask()
- added new functions systemctl_start(), systemctl_stop()
- added new functions systemctl_reload(), systemctl_restart()
- added new functions create_file(), create_directory()
- added new functions remove_file(), remove_directory()
- added new functions systemctl_get_default(), systemctl_set_default()
- added new functions localectl_set_locale(), timedatectl_set_timezone()
- added new functions get_virtualization_type(), strip_text(), render()
- status changed to "beta", added documentation https://fabrix.readthedocs.io/


Version 0.1
-----------

Released: 20 Oct 2017

- first public release
