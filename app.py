from flask import Flask, request, jsonify
import grequests
import json
import os
import sys

from requests.auth import HTTPBasicAuth

import requests


sys.setrecursionlimit(20000)
app = Flask(__name__)
#port = 5000
port = int(os.environ.get("PORT", 5000))


def take_action_async(scrapped_po_no):
    scrapped_po = scrapped_po_no
    print('*******************************************************')
    print(scrapped_po)
    url1 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")?sap-client=400&$format=json"
    url2 = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json"
    urls = [url1,url2]
    rs = (grequests.get(u,auth=('pritamsa','rupu@0801'))for u in urls)
    #both imap and map can be used
    #reque = grequests.imap(rs,size=1)
    reque = grequests.map(rs,size=10)
    response_array = []
    for response in reque:
        print(response)
        x = response.json()
        response_array.append(x)
        # print(x)
    #print(response_array)
    body2 = response_array[0]  #1st url body
    body3 = response_array[1]

    return body2,body3



@app.route('/', methods=['POST'])
def index():
    data = json.loads(request.get_data())  # gets the data from chatbot that is json body of bot memory
    

    bot_conversation = data['conversation']
    bot_memo = data['conversation']['memory']
    
    present_skill = data['conversation']['skill']
    print(bot_conversation)

    


    reply,index,instanceID,created_by_user,SupplierName,PurchaseOrderNetAmount,after_approval_reply = query_get_task_with_details(data['conversation']['memory'],present_skill)
    return jsonify(
        status=200,
        replies=[{
        'type': 'text',
        'content': reply
        #'content': 'here is your first task \n'+ task_list[0] + '\n' + task_detail_dict[task_list[0]],

        }],
        conversation={ 
    'memory': {'index':index,
    'instanceID':instanceID,
    'created_by':created_by_user,
    'SupplierName':SupplierName,
    'PurchaseOrderNetAmount':PurchaseOrderNetAmount,
    'after_approval_reply':after_approval_reply,
    'present_reply': reply
    } 
    } 
    )

    
    

   
   
def query_get_task_with_details(bot_memo,present_skill):
    
    if ((bot_memo == {} or bot_memo['index']) and present_skill == 'get_task'):
        r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
        body1 = r.json()
        no_of_tasks = len(body1["d"]["results"])
        if (body1["d"]["results"]):
            #task details
            instance_id = body1["d"]["results"][0]["InstanceID"] 
            task_title = body1["d"]["results"][0]["TaskTitle"]
            
            scrapped_po_no = task_title.split("order ",1)[1]
            
            body2,body3 = take_action_async(scrapped_po_no)
            
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
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                netPriceItem = body3["d"]["results"][i]["NetPriceAmount"]
                documentCurrency = body3["d"]["results"][i]["DocumentCurrency"]
                item_dict = {'Material':Material}
                
                concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                    + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                    + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            

            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'' #return 1for memory index as no memo is present in the beggining

        else:
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,1,bot_memo,bot_memo,bot_memo, bot_memo,''

    
    elif ((bot_memo['index']) and (present_skill == 'get_next_task' or present_skill == 'ignore_task')):
        r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
        body1 = r.json()
        if ((len(body1["d"]["results"])==1):

            instance_id = body1["d"]["results"][0]["InstanceID"] 
            task_title = body1["d"]["results"][0]["TaskTitle"]
            
            scrapped_po_no = task_title.split("order ",1)[1]
            
            body2,body3 = take_action_async(scrapped_po_no)
            
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
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                netPriceItem = body3["d"]["results"][i]["NetPriceAmount"]
                documentCurrency = body3["d"]["results"][i]["DocumentCurrency"]
                item_dict = {'Material':Material}
                
                concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                    + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                    + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            

            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'' #return 1for memory index as no memo is present in the beggining


       
        elif ((len(body1["d"]["results"])>0) and bot_memo['index'] < len(body1["d"]["results"])):
            #task details
            instance_id = body1["d"]["results"][bot_memo['index']]["InstanceID"] 
            task_title = task_title = body1["d"]["results"][bot_memo['index']]["TaskTitle"]
            #print(task_title)
            scrapped_po_no = task_title.split("order ",1)[1]
            #print(scrapped_po_no)
           
            body2,body3 = take_action_async(scrapped_po_no)
            

            #po_header detail
            created_by_user = body2["d"]["CreatedByUser"]
            SupplierName = body2["d"]["SupplierName"]
            PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]
            DocumentCurrency = body2["d"]["DocumentCurrency"]
            PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]

            final_reply_string = ''
            concat_string_for_multiple_lineitems = ''

            #po item detail
            #only show one or two tasks
            no_of_line_items = len(body3["d"]["results"])
            for i in range(no_of_line_items):
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                
                concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                    + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                    + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            final_reply_string = get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items in this P.O.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            #print(get_task_string)


            #print(final_reply_string)
            return final_reply_string,bot_memo['index'] + 1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),''

        elif(len(body1["d"]["results"]) > 0)and(bot_memo['index'] >= len(body1["d"]["results"])):
            
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,bot_memo['index'] ,len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],''
   
        else:
            
            final_reply_string = 'I think there are no more pending approvals for you. Say, "get my tasks", to get your pending approvals.'
            return final_reply_string,bot_memo['index'],len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],''

    #repeat intent is handled via bot memory not via code

    # elif((bot_memo['index']) and present_skill == 'repeat'):

    #     r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
    #     body1 = r.json()
    #     if (body1["d"]["results"] and bot_memo['index'] <= len(body1["d"]["results"])):
    #         #task details
    #         instance_id = body1["d"]["results"][bot_memo['index']-1]["InstanceID"] 
    #         task_title = body1["d"]["results"][bot_memo['index']-1]["TaskTitle"]
            
    #         scrapped_po_no = task_title.split("order ",1)[1]
            
    #         body2,body3 = take_action_async(scrapped_po_no) 
            

    #         #po_header detail
    #         created_by_user = body2["d"]["CreatedByUser"]
    #         SupplierName = body2["d"]["SupplierName"]
    #         PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]
    #         DocumentCurrency = body2["d"]["DocumentCurrency"]
    #         PurchaseOrderNetAmount = body2["d"]["PurchaseOrderNetAmount"]

    #         final_reply_string = ''
    #         concat_string_for_multiple_lineitems = ''

    #         #po item detail
    #         #only show one or two tasks
    #         no_of_line_items = len(body3["d"]["results"])
    #         for i in range(no_of_line_items):
    #             Material = body3["d"]["results"][i]["Material_Text"]
    #             Plant = body3["d"]["results"][i]["Plant"]
    #             OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                
    #             concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
    #                 + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
    #                 + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


    #         get_task_string = ''
    #         get_task_string_with_header_detail = ''

    #         get_task_string = task_title + '\n'

    #         get_task_string_with_header_detail = 'created_by_user: ' + created_by_user \
    #             +'.' +'\n' + 'SupplierName: ' + SupplierName \
    #              +'.'   + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.' +'\n'

    #         final_reply_string = get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
    #         #print(get_task_string)


    #         #print(final_reply_string)
    #         return final_reply_string,bot_memo['index'],instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency)

    #     elif(body1["d"]["results"] and bot_memo['index'] >= len(body1["d"]["results"])):
    #         final_reply_string = 'no more tasks to approve...'
    #         return final_reply_string,bot_memo['index'],len(body1["d"]["results"]),created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency)
   
    #     else:
    #         final_reply_string = 'I am facing some issues now please try later'
    #         return final_reply_string,bot_memo['index'],len(body1["d"]["results"]),created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency)

    elif((bot_memo['index']) and present_skill == 'approve'):
        after_approval_reply = 'successfully approved, please say,"get my tasks", to get your previous pending aapprovals from the beggining, or, say next to move on to your next task.'
        approval_failure_reply = "there was an issue with the server, Please try again later to approve..."
        session = requests.Session()
        header = {'x-csrf-token':'Fetch'}
        present_task_instance_id = bot_memo['instanceID']

        response = session.head("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header)
        if (response.status_code != 200):
            return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply
        elif (response.status_code == 200):
            cookie = session.cookies.get_dict()
            print(cookie)

            csrf = response.headers['x-csrf-token']
            #print(csrf)

            #post
            #approve
            header_2 = {'x-csrf-token':csrf}
            approve_po = session.post("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+present_task_instance_id +"'""&DecisionKey='0001'&Comments='test%20approve'",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header_2,cookies=cookie)

            print('***************************************************************')
            print(approve_po.status_code)

            return after_approval_reply,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],after_approval_reply  #after this call the "next" task showing skill in bot


    

@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)



#app.run(port=port)

app.run(port=port, host="0.0.0.0")
