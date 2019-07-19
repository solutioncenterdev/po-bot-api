from flask import Flask, request, jsonify
import json
import requests
import os
import aiohttp
import async_timeout
import asyncio
from requests.auth import HTTPBasicAuth





@asyncio.coroutine
def main():
    loop = asyncio.get_event_loop()
    future1 = loop.run_in_executor(None, requests.get, 'http://www.google.com')
    future2 = loop.run_in_executor(None, requests.get, 'http://www.google.co.uk')
    response1 = await.get_json(future1)
    #response2 = yield from future2
    print(response1)
    #print((response2.text))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())