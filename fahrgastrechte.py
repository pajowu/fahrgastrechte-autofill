import functools
import html
import json
import os
import shlex
import subprocess
import sys
import time

import npyscreen
from fdfgen import forge_fdf


def stop_form(F):
    F.editing = False


def form(*args):
    F = npyscreen.FormMultiPage()
    if os.path.isfile("defaults.json"):
        with open("defaults.json", "r") as f:
            defaults = json.load(f)
    else:
        defaults = {}

    fields = {}
    fieldnames = []
    field_fields = []
    fields_ = subprocess.check_output(shlex.split(
        "pdftk fahrgastrechte.pdf dump_data_fields"), stderr=open("/dev/null", "w")).decode().split("---\n")
    for raw_field in fields_:
        f = {}
        for line in raw_field.splitlines():
            r = line.split(": ")
            r[1] = html.unescape(r[1])
            if r[0] in f:
                if not isinstance(f[r[0]], list):
                    f[r[0]] = [f[r[0]]]
                f[r[0]].append(r[1])
            else:
                f[r[0]] = r[1]
        if 'FieldName' in f:
            fields[f['FieldName']] = f
            fieldnames.append(f['FieldName'])

    for n in fieldnames:
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
                             when_pressed_function=functools.partial(stop_form, F))
    F.switch_page(0)
    F.edit()

    fields = [(n, get_value(x)) for n, x in field_fields]

    with open("fields.json", "w") as f:
        json.dump({x: y for x, y in fields}, f)

    fdf = forge_fdf("", fields, [], [], [])
    fdf_file = open("data.fdf", "wb")
    fdf_file.write(fdf)
    fdf_file.close()

    fields_ = subprocess.check_output(shlex.split(
        "pdftk fahrgastrechte.pdf fill_form data.fdf output fahrgastrechte_{}.pdf".format(int(time.time()))), stderr=open("/dev/null", "w")).decode().split("---\n")


def get_value(w):
    if isinstance(w, npyscreen.MultiLine) or isinstance(w, npyscreen.TitleMultiLine):
        if w.value == None:
            return "Off"
        else:
            return w.values[w.value]
    else:
        return w.value

if __name__ == '__main__':
    npyscreen.wrapper_basic(form)
