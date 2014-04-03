#!/usr/bin/env python
# -*- coding: utf-8
#
#* -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# File Name : index.py
# Creation Date : 02-04-2014
# Last Modified : Wed 02 Apr 2014 03:32:00 PM BST
# Created By : Greg Lyras <greglyras@gmail.com>
#_._._._._._._._._._._._._._._._._._._._._.*/

from config import server
from config import authorization
from config import root_authorization


from flask import Flask
from flask import render_template

import simplejson as json

import requests

app = Flask(__name__)

@app.route('/')
def index():
  navigation = [{'href' : 'some_href', 'caption' : 'some_caption'}]
  return render_template("index.html", navigation=navigation)

auth_headers = {
  "Accept": "application/json",
  "Authorization": "Basic " + authorization,
  "Connection": "keep-alive"
  }

root_auth_headers = {
  "Accept": "application/json",
  "Authorization": "Basic " + root_authorization,
  "Connection": "keep-alive"
  }
limits = {'collist': 'Identifier,Location,Severity,Flash,Acknowledged', 'filter': "Scenario='eventpump' AND Severity > 0"}

@app.route('/test')
def test():
  r = requests.get(server+"/objectserver/restapi/alerts/status", params=limits, headers=auth_headers)
  return render_template("test.html", responce=r, jsonstuff=r.text)


def aggregate_location_flash(r):
  aggregated_data = {}
  for row in r.json()['rowset']['rows']:
    city = row['Location']
    if city in aggregated_data.keys():
      aggregated_data[city]['Flash'] += row['Flash']
      if row['Flash'] == 0:
        aggregated_data[city]['NotFlash'] += 1
    else:
      aggregated_data[city] = {}
      aggregated_data[city]['Flash'] = row['Flash']
      if row['Flash'] == 0:
        aggregated_data[city]['NotFlash'] = 1
      else:
        aggregated_data[city]['NotFlash'] = 0

  geo = [['City', 'Flash Ratio']]
  for key in aggregated_data.keys():
    nrow = [key]
    (a,b) = aggregated_data[key].values()
    nrow.append(float(a)/float(b))
    geo.append(nrow)
  geo = json.dumps(geo)
  return geo

def aggregate_location_severity_flash(r):
  aggregated_data = {}
  for row in r.json()['rowset']['rows']:
    city = row['Location']
    if city in aggregated_data.keys():
      aggregated_data[city]['Severity'] = max(aggregated_data[city]['Severity'], row['Severity'])
    else:
      aggregated_data[city] = {}
      aggregated_data[city]['Severity'] = row['Severity']

  geo = [['City', 'Severity']]
  for key in aggregated_data.keys():
    nrow = [key]
    nrow.extend(aggregated_data[key].values())
    geo.append(nrow)
  geo = json.dumps(geo)
  return geo

def aggregate_performance_data(r):
  perf_buf= r.json()['rowset']['rows']
  perf = []
  for row in perf_buf:
    perf.append([row['Minute'], row['TriggerPercent']*10,
      row['ClientPercent']*10, row['EventRate']])
  perf = sorted(perf, key = lambda x: x[0])
  perf = [['Minute', 'TriggerPercent', 'ClientPercent','EventRate']] + perf
  return json.dumps(perf)

@app.route('/challenge_a')
def challenge_a():
  r = requests.get(server+"/objectserver/restapi/alerts/status", params=limits, headers=auth_headers)
  geodata = aggregate_location_flash(r)
  geosevdata = aggregate_location_severity_flash(r)
  jsontable = sorted(r.json()['rowset']['rows'], key=lambda x: x['Severity'], reverse=True)
  r = requests.get(server+"/objectserver/restapi/master/perf_per_minute", headers=root_auth_headers)
  perfdata = aggregate_performance_data(r)

  return render_template("challenge_a.html", **locals())

@app.route('/_update_performance')
def update_performance():
  r = requests.get(server+"/objectserver/restapi/master/perf_per_minute", headers=root_auth_headers)
  return aggregate_performance_data(r)


if __name__ == '__main__':
  app.debug = True
  app.run()
