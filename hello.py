from __future__ import print_function

import grequests
from flask import Flask, request, jsonify
import json
import requests
import os
from requests.auth import HTTPBasicAuth


url = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"

url_count = 3

pending_requests = []
for i in range(url_count):
  pending_requests.append(grequests.get(url,auth=('pritamsa', 'rupu@0801')))

all_responses = grequests.imap(pending_requests,size=1)
# json_body = [response.content for response in all_responses]
# print(json_body[0])
for response in all_responses:
    x = response.json()
   
    
    break
print(x)