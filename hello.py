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



# url1 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder='4500000365')?sap-client=400&$format=json"
# url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder='4500000365')/to_PurchaseOrderItem?sap-client=400&$format=json"
# urls = [url1,url2]

# rs = (grequests.get(u,auth=('pritamsa','rupu@0801'))for u in urls)
# reque = grequests.imap(rs,size=2)
# response_array = []
# for response in reque:
#     print(response)
#     x = response.json()
#     response_array.append(x)
#     # print(x)
# #print(response_array)
# body2 = response_array[0]
# body3 = response_array[1]
# print(body2["d"]["CreatedByUser"])
# # print(body3['d']['results'][0]['Material'])

import requests
session = requests.Session()

header = {'x-csrf-token':'Fetch'}


response = session.head("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header)
cookie = session.cookies.get_dict()
print(cookie)

csrf = response.headers['x-csrf-token']
print(csrf)

#post
#approve
header_2 = {'x-csrf-token':csrf}
approve_po = session.post("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID='000000420093'&DecisionKey='0001'&Comments='test%20approve'",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header_2,cookies=cookie)

print(approve_po.status_code)



#heads = response.cookies.get_dict()
# body = response.json()

# if 'x-csrf-token' in response.cookies:
#     # Django 1.6 and up
#     csrftoken = response.cookies['x-csrf-token']
# else:
#     # older versions
#     csrftoken = response.cookies['x-csrf-token']
# print(heads)
#print(response.headers['x-csrf-token'])

# print(csrftoken)

# print(body['d']['results'][1]['TaskTitle'])
#print(response.request.headers)
#print(response.headers)





#"https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID='000000420093'&DecisionKey='0001'&Comments='test%20approve'"




