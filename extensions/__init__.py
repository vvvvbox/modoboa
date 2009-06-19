# -*- coding: utf-8 -*-
import os
import re

def loadextensions():
    from django.conf import settings

    expr = re.compile("mailng\.extensions\.(.+)")
    for app in settings.INSTALLED_APPS:
        m = expr.match(app)
        if not m:
            continue
        module = __import__(m.group(1), globals(), locals(), ['main'])
        module.main.init()
