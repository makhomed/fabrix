import os.path
import inspect
from jinja2 import Environment, FileSystemLoader, BaseLoader
from jinja2.exceptions import UndefinedError
from fabric.api import env, abort
from fabrix.config import conf, local_conf
from fabrix.editor import strip_text


def _generate_context(*args, **kwargs):
    if env.host_string:
        context = conf.copy()
    else:
        context = local_conf.copy()
    variables = dict(*args, **kwargs)
    context.update(variables)
    return context


def _render_template(template, context):
    try:
        return template.render(context)
    except UndefinedError, ex:
        caller = str(inspect.stack()[1][3])
        fname = str(inspect.stack()[2][1])
        nline = str(inspect.stack()[2][2])
        abort('%s: %s in file %s line %s' % (caller, ex, fname, nline))


def render_template(template_filename, *args, **kwargs):
    templates_dir = os.path.join(os.path.dirname(env.real_fabfile), 'templates')
    if not os.path.isdir(templates_dir):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('render_template: templates dir \'%s\' not exists in file %s line %s' % (templates_dir, fname, nline))
    template_abs_filename = os.path.join(templates_dir, template_filename)
    if not os.path.isfile(template_abs_filename):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('render_template: template \'%s\' not exists in file %s line %s' % (template_abs_filename, fname, nline))
    environment = Environment(loader=FileSystemLoader(templates_dir), keep_trailing_newline=True)
    template = environment.get_template(template_filename)
    context = _generate_context(*args, **kwargs)
    return _render_template(template, context)


def render(template_string, *args, **kwargs):
    environment = Environment(loader=BaseLoader(), keep_trailing_newline=True)
    template = environment.from_string(template_string)
    context = _generate_context(*args, **kwargs)
    text = _render_template(template, context)
    return strip_text(text)
