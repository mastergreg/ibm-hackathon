"""
  Sample application to connect to an ObjectServer's HTTP interface
  and list the LastOccurrent, Summary and Tally fields of all Severity 2
  events.

  Licensed Materials - Property of IBM

  (C) Copyright IBM Corp. 2014. All Rights Reserved

  US Government Users Restricted Rights - Use, duplication
  or disclosure restricted by GSA ADP Schedule Contract
  with IBM Corp.

  This software is provided ``as is'' without express or
  implied warranty.

  Runs on Python v2 only.

"""

import urllib2
import urllib
import sys
import base64
import json
import datetime
import getopt

if __name__ == '__main__':
    # Sample application to connect to an ObjectServer's HTTP interface
    # and list the LastOccurrent, Summary and Tally fields of all Severity 2
    # events.
    # Runs on Python 2.7

    hostname='10.0.0.3'
    username="STUDENT1"
    password="STUDENT1"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:u:p:")

        for opt,arg in opts :
            if opt == '-h':
                hostname=arg
            if opt == '-p':
                password=arg
            if opt == '-u':
                username=arg

    except getopt.GetoptError:
        print("Usage: basicquery -h hostname -u userid -p password")
        sys.exit(-1)

    # URL of ObjectServer alerts.status table
    objserv_url=" http://%s:8080/objectserver/restapi/alerts/status" % (hostname)
    print (objserv_url)

    #Request the LastOccurrence and Summary columns for all entries with a Severity of 2
    my_url = objserv_url + "?"
    my_url=my_url+urllib.urlencode({'collist':'LastOccurrence,Summary,Tally','filter':'Severity=2'})
    request = urllib2.Request(my_url)
    response= None

    # Basic authentication is required.
    base64String = base64.encodestring("%s:%s" % (username,password))
    request.add_header("Authorization", "Basic %s" % (base64String))

    #print my_url
    #print request.headers

    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as err:
        print ("failed with HTTP status code %s" % (err.code))
        sys.exit(-1)
    except urllib2.URLError as err:
        print("failed with URL error %s" % (err.reason))
        sys.exit(-1)
    #print ('request successful')
    #print (response.info())

    # Get response and parse into JSON
    text_response = response.read()
    json_response = json.loads(text_response)

    #print (text_response)
    #print (json_response)

    # Output headings based off the SQL column names
    # and create a list of all the columns and their types we expect
    # to be returned
    coldesc = json_response['rowset']['coldesc']
    listofnames = list()
    for col in coldesc:
        sys.stdout.write( col['name'] +'\t\t')
        listofnames.append((col['name'],col['type']))
    print ('')

    for row in json_response['rowset']['rows']:
        # Loop through all the rows returned by the ObjectServer
        for name,coltype in listofnames:
            # Loop through all the columns we expect for each row and
            # format them according to type
            contents = row[name]
            if coltype =='string':
                #Truncate and pad the string to 60 characters
                sys.stdout.write("%-60s\t\t" % (contents[:60]))
            elif coltype =='utc':
                #Time in standard seconds from EPOC format. Can format
                #using python API
                mydate = datetime.datetime.fromtimestamp(int(contents))
                sys.stdout.write(mydate.strftime('%Y-%m-%d %H:%M:%S'))
            elif coltype =='integer':
                sys.stdout.write("%d\t\t" % (row[name]))
            sys.stdout.write('\t')
        print ('')
    print ('')

