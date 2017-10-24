import os.path
from jinja2 import Environment, FileSystemLoader
from fabric.api import env, abort
from fabrix.config import conf, local_conf


def render_template(template_filename, **kwargs):
    templates_dir = os.path.join(os.path.dirname(env.real_fabfile), 'templates')
    if not os.path.isdir(templates_dir):
        abort('render_template: templates dir \'%s\' not exists' % templates_dir)
    template_abs_filename = os.path.join(templates_dir, template_filename)
    if not os.path.isfile(template_abs_filename):
        abort('render_template: template \'%s\' not exists' % template_abs_filename)
    environment = Environment(loader=FileSystemLoader(templates_dir))
    template = environment.get_template(template_filename)
    if env.host_string:
        context = conf.copy()
    else:
        context = local_conf.copy()
    context.update(**kwargs)
    return template.render(**context)
