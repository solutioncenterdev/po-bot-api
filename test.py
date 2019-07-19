from flask import Flask, request, jsonify
import json
import requests
import os

from requests.auth import HTTPBasicAuth

import grequests

urls = ["http://python-requests.org"]

req = (grequests.get(u)for u in urls)
responses = grequests.imap(req,size=1)

json_body = [response for response in responses]
print(json_body)

