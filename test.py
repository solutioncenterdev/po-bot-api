from flask import Flask, request, jsonify
import json
import requests
import os

from requests.auth import HTTPBasicAuth

import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        #data = await response.read()
        
        return await response.json(content_type=text/plane)
async def hey():
    urls = ['https://www.google.com/']
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session,url))

        body = await asyncio.gather(*tasks)

        print(body[0])

loop = asyncio.get_event_loop()
loop.run_until_complete(hey())


