#!/usr/bin/env python
# -*- coding: utf-8
#
#* -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# File Name : config.py
# Creation Date : 02-04-2014
# Last Modified : Wed 02 Apr 2014 01:00:04 PM BST
# Created By : Greg Lyras <greglyras@gmail.com>
#_._._._._._._._._._._._._._._._._._._._._.*/

import base64

server = "http://10.0.0.6:8080"
username = "STUDENT11"
password = "STUDENT11"
authorization = base64.b64encode(username + ":" + password)
root_authorization = base64.b64encode("root:")

def main():
  pass

if __name__=="__main__":
    main()

