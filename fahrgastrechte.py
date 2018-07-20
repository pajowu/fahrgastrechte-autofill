import argparse
import functools
import html
import json
import os
import random
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import npyscreen
import functions

def main(*args):
    args, defaults = functions.get_args()

    return npyscreen.wrapper_basic(functools.partial(run_menu, defaults, args))

def run_menu(defaults, args, *arg, **kwargs):
    field_fields = []
    fields, fieldnames = functions.get_form_fields(**vars(args))
    F = npyscreen.FormMultiPage()
    for n in sorted(fieldnames, key=functions.db_fieldname_sort):
        title = ""
        if 'FieldNameAlt' in fields[n]:
            title = fields[n]['FieldNameAlt']

        if n in defaults:
            value = defaults[n]
        else:
            value = None

        if 'FieldStateOption' in fields[n]:
            if value is not None:
                i = fields[n]['FieldStateOption'].index(value)
            else:
                i = fields[n]['FieldStateOption'].index('Off')
            if title:
                field_fields.append((n, F.add_widget_intelligent(
                    npyscreen.TitleMultiLine, values=fields[n]['FieldStateOption'], name=title, value=i)))
            else:
                field_fields.append((n, F.add_widget_intelligent(
                    npyscreen.MultiLine, values=fields[n]['FieldStateOption'], value=i)))
        else:
            field_fields.append((n, F.add_widget_intelligent(
                npyscreen.TitleText, name=title, value=value)))

    F.add_widget_intelligent(npyscreen.ButtonPress, name="Generate Form",
                             when_pressed_function=functools.partial(setattr, F, 'editing', False))
    F.switch_page(0)
    F.edit()

    fields = [(n, get_value(x)) for n, x in field_fields]

    return functions.generate_form(fields, **vars(args))

def get_value(w):
    if isinstance(w, npyscreen.MultiLine) or isinstance(w, npyscreen.TitleMultiLine):
        if w.value == None:
            return "Off"
        else:
            return w.values[w.value]
    else:
        return w.value

if __name__ == '__main__':
    print(main())
