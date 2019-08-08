from flask import Flask, request, jsonify
import json

import grequests

import aiohttp
import asyncio
import os
import requests


from requests.auth import HTTPBasicAuth


# header = {'x-csrf-token':'Fetch'}
# present_task_instance_id = '000000431084'

# url3 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
# head_res1 = (grequests.head(u,auth=('pritamsa','rupu@0801'),headers=header)for u in url3)
# #both imap and map can be used
# #reque = grequests.imap(rs,size=1)
# reque3 = grequests.map(head_res1,size=1)
# response_array3 = []
# for response3 in reque3:

#     if (response3.status_code != 200):
#         print("hey problem")
#     else:
#         cookie = response3.cookies.get_dict()
#         print(cookie)

#         csrf = response3.headers['x-csrf-token']
#         print(csrf)

#         header_2 = {'x-csrf-token':csrf}

#         url_post = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+present_task_instance_id +"'""&DecisionKey='0002'&Comments='test%20reject'"]
#         post_res = (grequests.post(u_post,auth=('pritamsa','rupu@0801'),headers=header_2,cookies=cookie)for u_post in url_post)

#         post_reque = grequests.map(post_res,size=1)
#         response_array_post = []
#         for response_post in post_reque:

#             if (response_post.status_code != 200):
#                 print("hey problem in rejection request")
#             else:
#                 print('rejected')   

url1 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
rs1 = (grequests.get(u,auth=('pritamsa','rupu@0801'))for u in url1)
#both imap and map can be used
#reque = grequests.imap(rs,size=1)
reque1 = grequests.map(rs1,size=1)
response_array1 = []
for response1 in reque1:
    print(response1)
    x1 = response1.json()
    response_array1.append(x1)
body1 = response_array1[0]

all_instance_id_array = []
scrapped_po_no_list = []

scrapped_po_dict_instance_id = {}
instance_id_corresponding_scrapped_net_amt_dict = {}

no_of_tasks = len(body1["d"]["results"])
if (body1["d"]["results"]):
    for i in range(no_of_tasks):
        instance_id = body1["d"]["results"][i]["InstanceID"]
        task_title = body1["d"]["results"][i]["TaskTitle"]
            
        scrapped_po_no = task_title.split("order ",1)[1]
        all_instance_id_array.append(instance_id)
        scrapped_po_no_list.append(scrapped_po_no)
print(all_instance_id_array)
print(scrapped_po_no_list)

scrapped_po_dict_instance_id = dict(zip(scrapped_po_no_list,all_instance_id_array))
print(scrapped_po_dict_instance_id)

make_url_array_for_sending_all_po_and_getting_net_amt_as_response = []
for i in range(len(scrapped_po_no_list)):
    make_url = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no_list[i] +"'"")?sap-client=400&$format=json"
    make_url_array_for_sending_all_po_and_getting_net_amt_as_response.append(make_url)

print()
print(make_url_array_for_sending_all_po_and_getting_net_amt_as_response)


#make async request to get net amount for each po and corresponding instance ids

# url_all_with_ = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
rs5 = (grequests.get(u,auth=('pritamsa','rupu@0801'))for u in make_url_array_for_sending_all_po_and_getting_net_amt_as_response)
#both imap and map can be used
#reque = grequests.imap(rs,size=1)
request_to_get_all_PO = grequests.map(rs5,size=10)
response_array5 = []
for response in request_to_get_all_PO:
    print(response)   # response statuses of each requests
    y = response.json()
    response_array5.append(y)
# body1 = response_array5[1]  #print only one of the requested bodies

length_of_response_array = len(response_array5)

scrap_all_net_amounts_serially_for_all_PO_list = []
for j in range(length_of_response_array):
    scrapped_net_amounts = response_array5[j]["d"]["PurchaseOrderNetAmount"]
    scrap_all_net_amounts_serially_for_all_PO_list.append(scrapped_net_amounts)    
print(scrap_all_net_amounts_serially_for_all_PO_list)

instance_id_corresponding_scrapped_net_amt_dict = dict(zip(all_instance_id_array,scrap_all_net_amounts_serially_for_all_PO_list))

print(instance_id_corresponding_scrapped_net_amt_dict)

final_batch_instance_id_list = []
final_batch_amount_list = []
final_batch_instance_amount_dict = {}
for key in instance_id_corresponding_scrapped_net_amt_dict.keys():
    if (eval(instance_id_corresponding_scrapped_net_amt_dict[key]) < (7000)):
        final_batch_instance_id_list.append(key)  #appends the instance ids which whose Po amounts satisfies the condition
        final_batch_amount_list.append(instance_id_corresponding_scrapped_net_amt_dict[key])
final_batch_instance_amount_dict = dict(zip(final_batch_instance_id_list,final_batch_amount_list))

print('*********************************************')
print(final_batch_instance_amount_dict)



#approval code
#batch approval code








