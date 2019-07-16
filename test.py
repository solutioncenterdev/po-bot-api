from flask import Flask, request, jsonify, current_app
import json
import requests
from requests.auth import HTTPBasicAuth



# with app.app_context():
#     # within this block, current_app points to app.
#     print(current_app.name)
#     from flask import request, jsonify
r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
body1 = r.json()
if (body1["d"]["results"]):
    #task details
    instance_id = body1["d"]["results"][0]["InstanceID"] 
    task_title = body1["d"]["results"][0]["TaskTitle"]
    #print(task_title)
    scrapped_po_no = task_title.split("order ",1)[1]
    #print(scrapped_po_no)
    response_po_detail_header = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no +"'"")?sap-client=400&$format=json",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
    body2 = response_po_detail_header.json()
    
    response_po_item_detail = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))

    
    body3 = response_po_item_detail.json()
    #print(r.json())

    #task details
    instance_id = body1["d"]["results"][0]["InstanceID"] 
     

    #po_header detail
    created_by_user = body2["d"]["CreatedByUser"]
    SupplierName = body2["d"]["SupplierName"]
    PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]
    DocumentCurrency = body2["d"]["DocumentCurrency"]
    PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]

    final_reply_string = ''
    concat_string_for_multiple_lineitems = ''

    #po item detail
    no_of_line_items = len(body3["d"]["results"])
    for i in range(no_of_line_items):
        Material = body3["d"]["results"][i]["Material"]
        Plant = body3["d"]["results"][i]["Plant"]
        OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
        
        concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
            + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
               + 'OrderQuantity: ' + OrderQuantity + '.\n'
            


    get_task_string = ''
    get_task_string_with_header_detail = ''

    get_task_string = task_title + '\n' + 'instance id : ' + instance_id + '\n'

    get_task_string_with_header_detail = 'created_by_user: ' + created_by_user \
        + '\n' + 'SupplierName: ' + SupplierName \
            + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '\n'

    final_reply_string = get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items\n'+ concat_string_for_multiple_lineitems
    #print(get_task_string)


    print(final_reply_string)

else:
    final_reply_string = 'no tasks to approve...'
    

