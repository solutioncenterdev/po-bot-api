from flask import Flask, request, jsonify
import json

import aiohttp
import asyncio
import os
import requests


from requests.auth import HTTPBasicAuth



scrapped_po = '4500000431'

async def fetch(session, url):
    async with session.get(url) as response:
        #data = await response.read()
        
        return await response.json()
async def hey():
    urls = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"]
    tasks = []
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('pritamsa','rupu@0801')) as session:
        for url in urls:
            tasks.append(fetch(session,url))

        body = await asyncio.gather(*tasks)

        print(body[0]['d']['results'][0]["TaskTitle"])
        print('**************************************************')
        print(body[1]['d']['PurchasingOrganizationName'])

loop = asyncio.get_event_loop()
loop.run_until_complete(hey())











