from flask import Flask, request, jsonify, current_app
import json
import requests
from requests.auth import HTTPBasicAuth



# with app.app_context():
#     # within this block, current_app points to app.
#     print(current_app.name)
#     from flask import request, jsonify
r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
response_po_detail_header = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder='4500000352')?sap-client=400&$format=json",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
response_po_item_detail = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder='4500000352')/to_PurchaseOrderItem?sap-client=400&$format=json",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
body1 = r.json()
body2 = response_po_detail_header.json()
body3 = response_po_item_detail.json()
#print(r.json())
get_task_string = ''
get_task_string_with_header_detail = ''
# print(body1["d"]["results"][0]["InstanceID"])
# print(body1["d"]["results"][0]["TaskTitle"])

task_title = body1["d"]["results"][0]["TaskTitle"]
get_task_string = 'instance id : ' + body1["d"]["results"][0]["InstanceID"] + '\n' + body1["d"]["results"][0]["TaskTitle"] + '\n'
print(get_task_string)

# print()
# print()
print(body2["d"]["PurchaseOrder_Text"])
print(body3["d"]["results"][0]["Material"])

# r3 = request.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder='4500000352')?$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
# body_test = r3.json()
# s = body_test["d"]["PurchaseOrder_Text"]
# print()
# print()
# print(s)
#get_task_string_with_header_detail = 



# app = Flask(__name__)
# port = '5000'

# @app.route('/', methods=['POST'])
# def index():
#     #data = json.loads(request.get_data())

#     # FETCH THE CRYPTO NAME
#     #crypto_name = data['conversation']['memory']['crypto']['raw']

#     # FETCH BTC/USD/EUR PRICES
#     r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json")
#     print(r.json)
#     # return jsonify(
#     #     status=200,
#     #     replies=[{
#     #     'type': 'text',
#     #     'content': 'The price of %s is %f BTC and %f USD' % (crypto_name, r.json()['BTC'], r.json()['USD'])
#     #     }]
#     # )

# @app.route('/errors', methods=['POST'])
# def errors():
#   #print(json.loads(request.get_data()))
#   return jsonify(status=200)

# app.run(port=port)