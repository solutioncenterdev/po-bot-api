from flask import Flask, request, jsonify
import json

import aiohttp
import asyncio
import os
import requests


from requests.auth import HTTPBasicAuth



# scrapped_po = '4500000433'

async def fetch(session, url):
    async with session.get(url) as response:
        #data = await response.read()
        
        return await response.json()
async def hey(scrapped_po):
    # urls = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"]
    
    url1 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"
    url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json"
    urls = [url1,url2]
    tasks = []
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('pritamsa','rupu@0801')) as session:
        for url in urls:
            tasks.append(fetch(session,url))

        body = await asyncio.gather(*tasks)

        # print(body[0]['d']['results'][0]["TaskTitle"])
        # print('**************************************************')
        # print(body[1]['d']['PurchasingOrganizationName'])

        # print(body[0]['d']['PurchasingOrganizationName'])
        # print(body[1]['d']['results'][0]['PurchaseOrderItemText'])

        # print(body[0])

        body2 = body[0]
        body3 = body[1]

        print(body2)


        
    

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(hey('4500000433'))

        
# PurchaseOrderItemText

# loop = asyncio.get_event_loop()
# loop.run_until_complete(hey())












