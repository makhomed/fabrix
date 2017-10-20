import os.path
from fabric.api import env, abort
from jinja2 import Environment, FileSystemLoader


def render_template(template_filename, **context):
    templates_dir = os.path.join(os.path.dirname(env.real_fabfile), 'templates')
    if not os.path.isdir(templates_dir):
        abort('render_template: templates dir \'%s\' not exists' % templates_dir)
    template_abs_filename = os.path.join(templates_dir, template_filename)
    if not os.path.isfile(template_abs_filename):
        abort('render_template: template \'%s\' not exists' % template_abs_filename)
    environment = Environment(loader=FileSystemLoader(templates_dir))
    template = environment.get_template(template_filename)
    return template.render(context)
