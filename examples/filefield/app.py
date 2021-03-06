# -*- coding: utf-8 -*-
from iktomi import web
from iktomi.web.filters import *
from iktomi.templates import jinja2, Template

import cfg
import handlers as h

static = static_files(cfg.STATIC)
media = static_files(cfg.MEDIA, '/media/')
template = Template(cfg.TEMPLATES, jinja2.TEMPLATE_DIR, engines={'html': jinja2.TemplateEngine})


@web.request_filter
def environment(env, data, next_handler):
    env.cfg = cfg

    env.url_for = url_for
    env.url_for_static = static.construct_reverse()
    env.template = template

    return next_handler(env, data)



app = environment | web.cases(
    static, media,
    match('/', 'files') | web.cases(
        # Playing REST ;)
        method('GET') | h.list_files,
        method('POST') | h.post_file,
        #method('DELETE') | h.delete_files,
    ),
)

url_for = web.Reverse(web.locations(app))
