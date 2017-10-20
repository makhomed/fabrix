from fabrix.config import conf, local_conf, read_config
from fabrix.editor import edit_remote_file, edit_local_file, edit_ini_section, edit_text
from fabrix.editor import insert_line, delete_line, prepend_line, append_line, replace_line, substitute_line, strip_line
from fabrix.ioutil import read_remote_file, read_local_file, write_remote_file, write_local_file, debug
from fabrix.render import render_template


assert conf
assert local_conf
assert read_config
assert edit_remote_file
assert edit_local_file
assert edit_ini_section
assert edit_text
assert insert_line
assert delete_line
assert prepend_line
assert append_line
assert replace_line
assert substitute_line
assert strip_line
assert read_remote_file
assert read_local_file
assert write_remote_file
assert write_local_file
assert debug
assert render_template
