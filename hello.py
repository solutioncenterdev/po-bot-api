from __future__ import print_function

import grequests
from flask import Flask, request, jsonify
import json
import requests
import os
from requests.auth import HTTPBasicAuth


# url = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"

# url_count = 3

# pending_requests = []
# for i in range(url_count):
#   pending_requests.append(grequests.get(url,auth=('pritamsa', 'rupu@0801')))

# all_responses = grequests.imap(pending_requests,size=1)
# # json_body = [response.content for response in all_responses]
# # print(json_body[0])
# for response in all_responses:
#     x = response.json()
   
    
#     break
# print(x)



url1 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder='4500000365')?sap-client=400&$format=json"
url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder='4500000365')/to_PurchaseOrderItem?sap-client=400&$format=json"
urls = [url1,url2]

rs = (grequests.get(u,auth=('pritamsa','rupu@0801'))for u in urls)
reque = grequests.imap(rs,size=2)
response_array = []
for response in reque:
    print(response)
    x = response.json()
    response_array.append(x)
    # print(x)
#print(response_array)
body2 = response_array[0]
body3 = response_array[1]
print(body2["d"]["CreatedByUser"])
# print(body3['d']['results'][0]['Material'])





