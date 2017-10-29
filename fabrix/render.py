import os.path
import inspect
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import UndefinedError
from fabric.api import env, abort
from fabrix.config import conf, local_conf


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
    if env.host_string:
        context = conf.copy()
    else:
        context = local_conf.copy()
    variables = dict(*args, **kwargs)
    context.update(variables)
    print context
    try:
        return template.render(context)
    except UndefinedError, ex:
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('rendef_template: %s in file %s line %s' % (ex, fname, nline))
