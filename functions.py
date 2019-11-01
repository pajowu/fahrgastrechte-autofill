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

import requests
from bs4 import BeautifulSoup
from fdfgen import forge_fdf

def get_args(parser=None):
	if not parser:
		parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input-pdf', action='store', default='fahrgastrechte.pdf',
		help="Filename of the input pdf. (default: fahrgastrechte.pdf)")
	parser.add_argument('--pdftk', action='store', default='pdftk',
		help="Name/Path of the pdftk binary (default: pdftk)")
	parser.add_argument('--output-fdf', action='store', default='data.fdf',
		help="Filename of the fdf file generated to fill the pdf-form (default: data.fdf)")
	parser.add_argument('-o', '--output-pdf', action='store', default=None,
		help="Filename to store the filled pdf (default: fahrgastrechte_{CURRENT UNIT TIMESTAMP}.pdf)")
	parser.add_argument('--output-json', action='store', default='fields.json',
		help="Filename to store the filled fields as a json file (default: fields.json)")
	parser.add_argument('-d', '--field-defaults', action='store', default='defaults.json',
		help="Filename to load the default value from (files from --output-json can be used) (default: default.json)")
	parser.add_argument('-a', '--auftragsnummer', action='store', default=None,
		help="Six character booking number")
	parser.add_argument('-n', '--nachname', action='store', default=None,
		help="Surname for the Booking")
	parser.add_argument('-p', '--portal', action='store_true',
		help="Get livedata from the iceportal")
	parser.add_argument('-u', '--portal-url', action='store', default="iceportal.de",
		help="Base-Url of the iceportal (default: iceportal.de)")
	parser.add_argument('-f', '--from-stop', action='store',
		help="Where to start the journey (data will be automatically filled)")
	parser.add_argument('-t', '--to-stop', action='store',
		help="Where to end the journey (data will be automatically filled)")

	args = parser.parse_args()

	if os.path.isfile(args.field_defaults):
		with open(args.field_defaults, "r") as f:
			defaults = json.load(f)
	else:
		defaults = {}

	if args.auftragsnummer and args.nachname:
		defaults.update(download_buchung(**vars(args)))

	if args.from_stop and args.to_stop:
		livedata = get_livedata(**vars(args))
		print(livedata)
		defaults.update({
			"S1F13": livedata["trip"]["trainType"],
			"S1F14": livedata["trip"]["vzn"],
			"S1F17": livedata["trip"]["trainType"],
			"S1F18": livedata["trip"]["vzn"],

		})

	if args.from_stop:
		stop = get_stop(livedata, args.from_stop)
		start_date = datetime.fromtimestamp(stop["timetable"]["scheduledDepartureTime"]/1000)
		defaults.update(departure_fields_from_name_date(stop["station"]["name"], start_date))

	if args.to_stop:
		stop = get_stop(livedata, args.to_stop)
		scheduled_end_date = datetime.fromtimestamp(stop["timetable"]["scheduledArrivalTime"] / 1000)
		actual_end_date = datetime.fromtimestamp(stop["timetable"]["actualArrivalTime"] / 1000)
		defaults.update(
			arrival_fields_from_name_dates(stop["station"]["name"], scheduled_end_date, actual_end_date))

	return args, defaults


def departure_fields_from_name_date(name, date):
	return {
		"S1F1": date.strftime("%d"),
		"S1F2": date.strftime("%m"),
		"S1F3": date.strftime("%y"),
		"S1F4": name,
		"S1F5": date.strftime("%H"),
		"S1F6": date.strftime("%M"),
		"S1F01": date.strftime("%d"),
		"S1F02": date.strftime("%m"),
		"S1F03": date.strftime("%y"),
		"S1F04": name,
		"S1F05": date.strftime("%H"),
		"S1F06": date.strftime("%M"),
		"S1F19": date.strftime("%H"),
		"S1F20": date.strftime("%M")
	}


def arrival_fields_from_name_dates(name, scheduled_date, actual_date):
	return {
		"S1F7": name,
		"S1F8": scheduled_date.strftime("%H"),
		"S1F9": scheduled_date.strftime("%M"),
		"S1F07": name,
		"S1F08": scheduled_date.strftime("%H"),
		"S1F09": scheduled_date.strftime("%M"),
		"S1F10": actual_date.strftime("%d"),
		"S1F11": actual_date.strftime("%m"),
		"S1F12": actual_date.strftime("%y"),
		"S1F15": actual_date.strftime("%H"),
		"S1F16": actual_date.strftime("%M"),
	}


def db_fieldname_sort(fieldname):
	match = re.match(r"S(\d+)F(\d+)", fieldname)
	if match:
		return "S{:02d}F{:02d}".format(int(match.group(1)), int(match.group(2)))

def get_form_fields(pdftk, input_pdf, *args, **kwrags):
	fields = {}
	fieldnames = []
	fields_ = subprocess.check_output([pdftk, input_pdf, "dump_data_fields"], stderr=open("/dev/null", "w")).decode().split("---\n")
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

	return fields, fieldnames


def generate_form(fields, input_pdf, output_pdf, output_fdf, output_json, pdftk, *args, **kwargs):

	with open(output_json, "w") as f:
		json.dump({x: y for x, y in fields}, f)

	fdf = forge_fdf("", fields, [], [], [])
	fdf_file = open(output_fdf, "wb")
	fdf_file.write(fdf)
	fdf_file.close()

	output_file = output_pdf if output_pdf else "fahrgastrechte_{}.pdf".format(int(time.time()))
	subprocess.run([pdftk, input_pdf, "fill_form", output_fdf, "output", output_file], stderr=open("/dev/null", "w"))

	return output_file

def request_xml(request_type, xml):
	url = 'https://fahrkarten.bahn.de/mobile/dbc/xs.go'
	tnr = random.getrandbits(64)
	print(tnr)
	ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	print(ts)
	request_body = '<{0} version="2.0"><rqheader tnr="{1}" ts="{2}" v="19100000" d="iPhone10,4" os="iOS_13.1.3" app="NAVIGATOR"/>{3}</{0}>'.format(request_type, tnr, ts, xml)
	print(request_body)
	return requests.post(url, data=request_body)

def parse_time_location(root, elem_id):
	arrival = root.iter(elem_id).__next__()
	bhf = arrival.find('ebhf_name').text
	date = datetime.strptime(arrival.get('dt'), '%Y-%m-%dT%H:%M:%S').date()
	time = datetime.strptime(arrival.get('t'), '%H:%M:%S').time()
	return bhf, date, time

def download_buchung(auftragsnummer, nachname, *args, **kwargs):
	request_body = '<rqorder on="{}"/><authname tln="{}"/>'.format(auftragsnummer, nachname)
	req = request_xml("rqorderdetails", request_body)
	root = ET.fromstring(req.text)

	arrival = parse_time_location(root, "arr")
	departure = parse_time_location(root, "dep")

	return {
		"S1F1": str(departure[1].day).zfill(2),
		"S1F2": str(departure[1].month).zfill(2),
		"S1F3": str(departure[1].year)[2:].zfill(2),
		"S1F4": str(departure[0]),
		"S1F5": str(departure[2].hour).zfill(2),
		"S1F6": str(departure[2].minute).zfill(2),
		"S1F7": str(arrival[0]),
		"S1F8": str(arrival[2].hour).zfill(2),
		"S1F9": str(arrival[2].minute).zfill(2),
		"S1F10": str(arrival[1].day).zfill(2),
		"S1F11": str(arrival[1].month).zfill(2),
		"S1F12": str(arrival[1].year)[2:].zfill(2),
	}

def get_livedata(portal_url, *args, **kwargs):
	trip_info = requests.get("http://{}/api1/rs/tripInfo/trip".format(portal_url))
	return trip_info.json()

def stops(livedata):
	return livedata["trip"]["stops"]

def get_stop(livedata, stop_name):
	for stop in stops(livedata):
		if stop["station"]["name"] == stop_name or stop["station"]["evaNr"] == stop_name:
			return stop
