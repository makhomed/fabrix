import re
import inspect
from fabric.api import abort
from fabrix.ioutil import read_local_file, read_file, _atomic_write_local_file, _atomic_write_file, debug


def _full_line(pattern):
    if pattern[0] != '^':
        pattern = '^' + pattern
    if pattern[-1] != '$':
        pattern = pattern + '$'
    return pattern


def insert_line(line_to_insert, **kwargs):
    insert_type = None
    anchor_pattern = None
    for name in sorted(kwargs):
        if insert_type is None:
            if name == 'before' or name == 'after':
                insert_type = name
                anchor_pattern = _full_line(kwargs[name])
            else:
                fname = str(inspect.stack()[1][1])
                nline = str(inspect.stack()[1][2])
                abort('insert_line: unknown insert_type \'%s\' in file %s line %s' % (name, fname, nline))
        else:
            fname = str(inspect.stack()[1][1])
            nline = str(inspect.stack()[1][2])
            abort('insert_line: already defined insert_type \'%s\', unexpected \'%s\' in file %s line %s' % (insert_type, name, fname, nline))
    if insert_type is None:
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('insert_line: must be defined \'before\' or \'after\' argument in file %s line %s' % (fname, nline))

    def insert_line_editor(text):
        regex = re.compile(anchor_pattern)
        text_lines = text.split('\n')
        line_already_inserted = False
        anchor_lines = 0
        for line in text_lines:
            match = regex.match(line)
            if match:
                anchor_lines += 1
            if line == line_to_insert:
                line_already_inserted = True
        if anchor_lines == 0:
            fname = str(inspect.stack()[3][1])
            nline = str(inspect.stack()[3][2])
            abort('insert_line: anchor pattern \'%s\' not found in file %s line %s' % (anchor_pattern, fname, nline))
        elif anchor_lines > 1:
            fname = str(inspect.stack()[3][1])
            nline = str(inspect.stack()[3][2])
            abort('insert_line: anchor pattern \'%s\' found %d times, must be only one in file %s line %s' % (anchor_pattern, anchor_lines, fname, nline))
        out = list()
        for line in text_lines:
            match = regex.match(line)
            if match and not line_already_inserted:
                if insert_type == 'before':
                    out.append(line_to_insert)
                    out.append(line)
                    continue
                else:  # insert_type == 'after':
                    out.append(line)
                    out.append(line_to_insert)
                    continue
            else:
                out.append(line)
        return '\n'.join(out)
    return insert_line_editor


def prepend_line(line_to_prepend, insert_empty_line_after=False):

    def prepend_line_editor(text):
        text_lines = text.split('\n')
        if line_to_prepend in text_lines:
            return text
        if insert_empty_line_after:
            text_lines.insert(0, '')
        text_lines.insert(0, line_to_prepend)
        return '\n'.join(text_lines)
    return prepend_line_editor


def append_line(line_to_append, insert_empty_line_before=False):

    def append_line_editor(text):
        text_lines = text.split('\n')
        if line_to_append in text_lines:
            return text
        if text_lines[-1] == '':
            if insert_empty_line_before:
                text_lines.append(line_to_append)
            else:
                text_lines[-1] = line_to_append
        else:
            if insert_empty_line_before:
                text_lines.append('')
            text_lines.append(line_to_append)
        text_lines.append('')
        return '\n'.join(text_lines)
    return append_line_editor


def delete_line(pattern):
    pattern = _full_line(pattern)

    def delete_line_editor(text):
        regex = re.compile(pattern)
        out = list()
        for line in text.split('\n'):
            match = regex.match(line)
            if match:
                continue
            out.append(line)
        return '\n'.join(out)
    return delete_line_editor


def replace_line(pattern, repl, flags=0):
    pattern = _full_line(pattern)

    def replace_line_editor(text):
        regex = re.compile(pattern, flags)
        out = list()
        for line in text.split('\n'):
            match = regex.match(line)
            if match:
                line = regex.sub(repl, line)
            out.append(line)
        return '\n'.join(out)
    return replace_line_editor


def substitute_line(pattern, repl, flags=0):

    def substitute_editor(text):
        regex = re.compile(pattern, flags)
        out = list()
        for line in text.split('\n'):
            found = regex.search(line)
            if found:
                line = regex.sub(repl, line)
            out.append(line)
        return '\n'.join(out)
    return substitute_editor


def strip_line(chars=None):

    def strip_editor(text):
        out = list()
        for line in text.split('\n'):
            line = line.strip(chars)
            out.append(line)
        return '\n'.join(out)
    return strip_editor


def _apply_editors(old_text, *editors):
    if not editors:
        fname = str(inspect.stack()[2][1])
        nline = str(inspect.stack()[2][2])
        abort('editors can\'t be empty in file %s line %s' % (fname, nline))
    text = old_text
    for editor in editors:
        text = editor(text)
    text_after_first_pass = text
    for editor in editors:
        text = editor(text)
    text_after_second_pass = text
    if text_after_first_pass != text_after_second_pass:
        fname = str(inspect.stack()[2][1])
        nline = str(inspect.stack()[2][2])
        abort('editors is not idempotent in file %s line %s' % (fname, nline))
    new_text = text_after_second_pass
    changed = new_text != old_text
    debug('_apply_editors():', 'old_text:', old_text, 'new_next:', new_text, 'changed:', changed)
    return changed, new_text


def edit_ini_section(section_name_to_edit, *editors):
    if section_name_to_edit is not None:
        if section_name_to_edit[0] != '[' or section_name_to_edit[-1] != ']':
            fname = str(inspect.stack()[1][1])
            nline = str(inspect.stack()[1][2])
            abort('edit_ini_section: section name must be in form [section_name] in file %s line %s' % (fname, nline))
        section_name_to_edit = section_name_to_edit[1:-1]

    def ini_section_editor(text):
        pattern = r'^\s*\[(.*)\]\s*$'
        regex = re.compile(pattern)
        current_section_name = None
        current_section_text = list()
        section_content = dict()
        section_order = list()
        for line in text.split('\n'):
            match = regex.match(line)
            if match:
                new_section_name = match.group(1)
                if new_section_name in section_content or new_section_name == current_section_name:
                    fname = str(inspect.stack()[3][1])
                    nline = str(inspect.stack()[3][2])
                    abort('edit_ini_section: bad ini file, section \'[%s]\' duplicated in file %s line %s' % (new_section_name, fname, nline))
                section_content[current_section_name] = current_section_text
                section_order.append(current_section_name)
                current_section_name = new_section_name
                current_section_text = list()
            else:
                current_section_text.append(line)
        section_content[current_section_name] = current_section_text
        section_order.append(current_section_name)
        if section_name_to_edit in section_content:
            old_text = '\n'.join(section_content[section_name_to_edit])
            changed, new_text = _apply_editors(old_text, *editors)
            if changed:
                section_content[section_name_to_edit] = new_text.split('\n')
        else:
            fname = str(inspect.stack()[3][1])
            nline = str(inspect.stack()[3][2])
            abort('edit_ini_section: section \'[%s]\' not found in file %s line %s' % (section_name_to_edit, fname, nline))
        out = list()
        for section_name in section_order:
            if section_name is not None:
                out.append('[' + section_name + ']')
            section_text = section_content[section_name]
            out.extend(section_text)
        return '\n'.join(out)
    return ini_section_editor


def edit_local_file(local_filename, *editors):
    old_text = read_local_file(local_filename)
    changed, new_text = _apply_editors(old_text, *editors)
    if changed:
        _atomic_write_local_file(local_filename, new_text)
    return changed


def edit_file(filename, *editors):
    old_text = read_file(filename)
    changed, new_text = _apply_editors(old_text, *editors)
    if changed:
        _atomic_write_file(filename, new_text)
    return changed


def edit_text(old_text, *editors):
    changed, new_text = _apply_editors(old_text, *editors)
    return new_text


def strip_text(text):
    if text is None:
        text = ''
    if not isinstance(text, basestring):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('strip_text: string expected in file %s line %s' % (fname, nline))
    if not text:
        return text
    lines = list()
    text = text.strip() + '\n'
    for line in text.split('\n'):
        line = line.strip()
        lines.append(line)
    text = '\n'.join(lines)
    return text
