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
    """Insert line editor.

    Inserts ``line_to_insert`` before or after specified line.
    One and only one keyword argument expected: ``before`` or ``after``

    Args:
        line_to_insert: Line to insert in text.
        before: Anchor pattern, before which text should be inserted.
        after: Anchor pattern, after which text should be inserted.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~insert_line` arguments.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
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
    """Prepend line editor.

    Prepends ``line_to_prepend`` before first line of text.
    If ``line_to_prepend`` already presend in text in any line position - do nothing.

    Args:
        line_to_prepend: Line to prepend before first line of text.
        insert_empty_line_after: If True add empty line after prepended line.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~prepend_line` arguments.
    """

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
    """Append line editor.

    Appends ``line_to_append`` after last line of text.
    If ``line_to_append`` already presend in text in any line position - do nothing.

    Args:
        line_to_append: Line to append after last line of text.
        insert_empty_line_before: If True add empty line before appended line.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~append_line` arguments.
    """

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
    """Delete line editor.

    Deletes all lines from text, which match ``pattern``.

    Args:
        pattern: Which lines whould be deleted.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~delete_line` arguments.
    """
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
    r"""Replace line editor.

    Replaces all **whole** lines in text, which match ``pattern`` with `repl`.
    In any case pattern wil start with r'^' and end with r'$' characters.

    .. seealso::
        :func:`~substitute_line`

    Args:
        pattern: Which lines should be replaced.
        repl: repl can be a string or a function; if it is a string, any backslash escapes in it are processed.
            That is, \\n is converted to a single newline character, \\r is converted to a carriage return,
            and so forth. Unknown escapes such as \\j are left alone. Backreferences, such as \\6,
            are replaced with the substring matched by group 6 in the pattern.
            For details see :meth:`re.RegexObject.sub`.
        flags: Any flags allowed in :func:`re.compile`.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~replace_line` arguments.
    """
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
    r"""Substitute line editor.

    Replaces part of lines in text, which match ``pattern`` with ``repl``.

    .. seealso::
        :func:`~replace_line`

    Args:
        pattern: Regular Expression, which part of lines should be substituted.
        repl: ``repl`` can be a string or a function; if it is a string, any backslash escapes in it are processed.
            That is, \\n is converted to a single newline character, \\r is converted to a carriage return,
            and so forth. Unknown escapes such as \\j are left alone. Backreferences, such as \\6,
            are replaced with the substring matched by group 6 in the pattern.
            For details see :meth:`re.RegexObject.sub`.
        flags: Any flags allowed in :func:`re.compile`.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~substitute_line` arguments.
    """

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
    """Strip line editor.

    Strip each line of text with :meth:`str.strip` called with argument chars.

    Args:
        chars: The chars argument is a string specifying the set of characters to be removed.
            If omitted or None, the chars argument defaults to removing whitespace.
            The chars argument is not a prefix or suffix;
            rather, all combinations of its values are stripped:

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~strip_line` arguments.

    """

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
    """Edit ini section text editor.

    Apply all editors from list ``editors`` to section named ``section_name_to_edit``.
    ``editors`` is any combination of **line** editors: :func:`~insert_line`, :func:`~delete_line`, :func:`~replace_line` and so on.

    Args:
        section_name_to_edit: Name of section to edit, must be in form '[section_name]'.
        editors: List of editors to apply for selected ini section.

    Returns:
        closure function, which acts as text editor, parameterized by :func:`~edit_ini_section` arguments.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
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
    """Edit local file text editor.

    Apply all editors from list ``editors`` to text of **local** file ``local_filename``.
    ``editors`` is any combination of editors: :func:`~insert_line`, :func:`~delete_line`, :func:`~replace_line` and so on.

    .. seealso::
            :func:`~edit_file`

    Args:
        local_filename: Name of **local** file to edit, must be absolute.
        editors: List of editors to apply for text of file ``local_filename``.

    Returns:
        True if file is changed, else False.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
    old_text = read_local_file(local_filename)
    changed, new_text = _apply_editors(old_text, *editors)
    if changed:
        _atomic_write_local_file(local_filename, new_text)
    return changed


def edit_file(remote_filename, *editors):
    """Edit remote file text editor.

    Apply all editors from list ``editors`` to text of **remote** file ``remote_filename``.
    ``editors`` is any combination of editors: :func:`~insert_line`, :func:`~delete_line`, :func:`~replace_line` and so on.

    .. seealso::
            :func:`~edit_local_file`

    Args:
        remote_filename: Name of **remote** file to edit, must be absolute.
        editors: List of editors to apply for text of file ``remote_filename``.

    Returns:
        True if file is changed, else False.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
    old_text = read_file(remote_filename)
    changed, new_text = _apply_editors(old_text, *editors)
    if changed:
        _atomic_write_file(remote_filename, new_text)
    return changed


def edit_text(text, *editors):
    """Edit text editor.

    Apply all editors from list ``editors`` to given text.
    ``editors`` is any combination of editors: :func:`~insert_line`, :func:`~delete_line`, :func:`~replace_line` and so on.

    Args:
        text: Text to edit, must be string.
        editors: List of editors to apply for text of file ``remote_filename``.

    Returns:
        Text after applying all editors.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
    changed, text = _apply_editors(text, *editors)
    return text


def strip_text(text):
    r"""Strip text helper function.

    Strip all empty lines from begin and end of text. Also strip all whitespace characters from begin and end of each line.
    Preserves '\\n' character at last line of text.

    Args:
        text: Text to strip, must be string or None.

    Returns:
        Text after strip. It is always string even if argument was None.

    Raises:
        :class:`~exceptions.SystemExit`: When error occurred.
    """
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
