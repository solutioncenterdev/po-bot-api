from flask import Flask, request, jsonify
import json

import grequests

import aiohttp
import asyncio
import os
import requests


from requests.auth import HTTPBasicAuth



# scrapped_po = '4500000433'

# async def fetch(session, url):
#     async with session.get(url) as response:
#         #data = await response.read()
        
#         return await response.text()
# async def hey():
#     # urls = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"]
    
#     url1 = 'https://www.w3schools.com/'
#     # url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json"
#     urls = [url1]
#     tasks = []
#     async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('pritamsa','rupu@0801')) as session:
#         for url in urls:
#             tasks.append(fetch(session,url))

#         body = await asyncio.gather(*tasks)

#         # print(body[0]['d']['results'][0]["TaskTitle"])
#         # print('**************************************************')
#         # print(body[1]['d']['PurchasingOrganizationName'])

#         # print(body[0]['d']['PurchasingOrganizationName'])
#         # print(body[1]['d']['results'][0]['PurchaseOrderItemText'])

#         # print(body[0])

#         body2 = body[0]
#         # body3 = body[1]

#         print(body2)

        


    
    

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(hey())
        
        
# PurchaseOrderItemText

# loop = asyncio.get_event_loop()
# loop.run_until_complete(hey())

header = {'x-csrf-token':'Fetch'}
present_task_instance_id = '000000426165'

url3 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
head_res1 = (grequests.head(u,auth=('pritamsa','rupu@0801'),headers=header)for u in url3)
#both imap and map can be used
#reque = grequests.imap(rs,size=1)
reque3 = grequests.map(head_res1,size=1)
response_array3 = []
for response3 in reque3:

    if (response3.status_code != 200):
        print("hey problem")
    else:
        cookie = response3.cookies.get_dict()
        print(cookie)

        csrf = response3.headers['x-csrf-token']
        print(csrf)

        header_2 = {'x-csrf-token':csrf}

        url_post = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+present_task_instance_id +"'""&DecisionKey='0001'&Comments='test%20approve'"]
        post_res = (grequests.post(u_post,auth=('pritamsa','rupu@0801'),headers=header_2,cookies=cookie)for u_post in url_post)

        post_reque = grequests.map(post_res,size=1)
        response_array_post = []
        for response_post in post_reque:

            if (response_post.status_code != 200):
                print("hey problem in approval request")
            else:
                print('approved')   

# reque3 = grequests.map(head_res1,size=1)
# response_array3 = []
# for response3 in reque3:
#     print(response3)
#     x3 = response3.json()
#     response_array3.append(x3)
# body3 = response_array3[0]

# 000000426165










