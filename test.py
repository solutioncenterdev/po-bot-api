from flask import Flask, request, jsonify
import json
import requests
import os

from requests.auth import HTTPBasicAuth

import aiohttp
import asyncio

# scrapped_po = '4500000431'

# async def fetch(session, url):
#     async with session.get(url) as response:
#         #data = await response.read()
        
#         return await response.json()
# async def hey():
#     urls = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"]
#     tasks = []
#     async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('pritamsa','rupu@0801')) as session:
#         for url in urls:
#             tasks.append(fetch(session,url))

#         body = await asyncio.gather(*tasks)

#         print(body[0]['d']['results'][0]["TaskTitle"])
#         print('**************************************************')
#         print(body[1]['d']['PurchasingOrganizationName'])

# loop = asyncio.get_event_loop()
# loop.run_until_complete(hey())









async def fetch(session, url):
    async with session.get(url) as response:
        #data = await response.read()
        
        return await response.json()
async def hey():

    r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
    body1 = r.json()
    no_of_tasks = len(body1["d"]["results"])
    if (body1["d"]["results"]):
        #task details
        instance_id = body1["d"]["results"][0]["InstanceID"] 
        task_title = body1["d"]["results"][0]["TaskTitle"]
        
        scrapped_po_no = task_title.split("order ",1)[1]

    # else:
    #     final_reply_string = 'no more tasks to approve in your inbox.'
    #     return final_reply_string,1,bot_memo,bot_memo,bot_memo, bot_memo,'','',''

    url1 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no +"'"")?sap-client=400&$format=json"
    url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json"
    urls = [url1,url2]

    # urls = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"]
    tasks = []
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('pritamsa','rupu@0801')) as session:
        for url in urls:
            tasks.append(fetch(session,url))

        body = await asyncio.gather(*tasks)

        return body[0], body[1], no_of_tasks, instance_id, task_title


loop = asyncio.get_event_loop()
loop.run_until_complete(hey())


