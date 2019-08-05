from flask import Flask, request, jsonify
import grequests
import json
import os
import sys

from requests.auth import HTTPBasicAuth

import requests


#sys.setrecursionlimit(20000)
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
    
    bot_nlp = data['nlp']['entities']
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(bot_nlp)
    bot_conversation = data['conversation']
    bot_memo = data['conversation']['memory']
    
    present_skill = data['conversation']['skill']
    print(bot_conversation)

    


    reply,index,instanceID,created_by_user,SupplierName,PurchaseOrderNetAmount,after_approval_reply,all_item_details,no_of_line_items,scrapped_po_no = query_get_task_with_details(data['conversation']['memory'],present_skill,bot_nlp)
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
    'no_of_line_items':no_of_line_items,
    'all_item_details':all_item_details,
    # 'item_details_ordinally':''
    'after_approval_reply':after_approval_reply,
    'present_reply': reply,
    'scrapped_po_no':scrapped_po_no
    } 
    } 
    )

    
    

   
   
def query_get_task_with_details(bot_memo,present_skill,bot_nlp):
    
    if ((bot_memo == {} or bot_memo['index']) and present_skill == 'get_task'):

        #requests can be used for synchronous requests
        # r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
        # body1 = r.json()

        #grequests is faster
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
            per_item_desc_dict = {}
            all_item_details = {}
            #po item detail
            no_of_line_items = len(body3["d"]["results"])
            for i in range(no_of_line_items):
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                netPriceItem = body3["d"]["results"][i]["NetPriceAmount"]
                documentCurrency = body3["d"]["results"][i]["DocumentCurrency"]
                price_present_item_with_currency = netPriceItem + documentCurrency

                item_no = '\nitem : ' + str(i + 1)
                # print(item_no)
                #item_no = dict(item_no)
                per_item_desc_dict = {item_no:{'Material':Material,'Plant':Plant,'OrderQuantity':OrderQuantity,'netPriceItem':price_present_item_with_currency}}
                all_item_details.update(per_item_desc_dict)
                
                #use this when sending the item details as string all in one reply
                # concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                #     + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                #     + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            #final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+  " say get item details to get all the item details in this purchase order. Or,say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."


            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no #return 1for memory index as no memo is present in the beggining

        else:
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,1,bot_memo,bot_memo,bot_memo, bot_memo,'','','',bot_memo

    
    elif ((bot_memo['index']) and (present_skill == 'get_next_task' or present_skill == 'ignore_task')):
        #requests can be used for synchronous requests
        # r = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
        # body1 = r.json()

        #grequests is faster
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
        no_of_tasks = len(body1["d"]["results"])
        if ((len(body1["d"]["results"])==1)):

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
            per_item_desc_dict = {}
            all_item_details = {}

            #po item detail
            no_of_line_items = len(body3["d"]["results"])
            for i in range(no_of_line_items):
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                netPriceItem = body3["d"]["results"][i]["NetPriceAmount"]
                documentCurrency = body3["d"]["results"][i]["DocumentCurrency"]
                price_present_item_with_currency = netPriceItem + documentCurrency

                item_no = 'item : ' + str(i + 1)
                # print(item_no)
                #item_no = dict(item_no)
                per_item_desc_dict = {item_no:{'Material':Material,'Plant':Plant,'OrderQuantity':OrderQuantity,'netPriceItem':price_present_item_with_currency}}
                all_item_details.update(per_item_desc_dict)
                
                #use this when sending the item details as string all in one reply
                # concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                #     + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                #     + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            # final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ " say get item details to get all the item details in this purchase order. Or,say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."

            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no #return 1for memory index as no memo is present in the beggining


       
        elif ((len(body1["d"]["results"])>1) and bot_memo['index'] < len(body1["d"]["results"])):
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
            per_item_desc_dict = {}
            all_item_details = {}

            #po item detail
            #only show one or two tasks
            no_of_line_items = len(body3["d"]["results"])
            for i in range(no_of_line_items):
                Material = body3["d"]["results"][i]["Material_Text"]
                Plant = body3["d"]["results"][i]["Plant"]
                OrderQuantity = body3["d"]["results"][i]["OrderQuantity"]
                netPriceItem = body3["d"]["results"][i]["NetPriceAmount"]
                documentCurrency = body3["d"]["results"][i]["DocumentCurrency"]
                price_present_item_with_currency = netPriceItem + documentCurrency

                item_no = 'item : ' + str(i + 1)
                # print(item_no)
                #item_no = dict(item_no)
                per_item_desc_dict = {item_no:{'Material':Material,'Plant':Plant,'OrderQuantity':OrderQuantity,'netPriceItem':price_present_item_with_currency}}
                all_item_details.update(per_item_desc_dict)
                
                #use this when sending the item details as string all in one reply
                # concat_string_for_multiple_lineitems = concat_string_for_multiple_lineitems \
                #     + 'Material: ' + Material + '.\n' + 'plant: ' + Plant + '.\n' \
                #     + 'OrderQuantity: ' + OrderQuantity + '.\n'
                    


            get_task_string = ''
            get_task_string_with_header_detail = ''

            get_task_string = task_title + '.' + '\n'

            get_task_string_with_header_detail = 'created by user: ' + created_by_user \
                + '.' + '\n' + 'SupplierName: ' + SupplierName \
                    + '.' + '\n' + 'PurchaseOrderNetAmount: ' + PurchaseOrderNetAmount + ' ' + DocumentCurrency + '.'+'\n'

            # final_reply_string = get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items in this P.O.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ " say get item details to get all the item details in this purchase order. Or,say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."

            #print(get_task_string)


            #print(final_reply_string)
            return final_reply_string,bot_memo['index'] + 1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no

        elif(len(body1["d"]["results"]) > 0)and(bot_memo['index'] >= len(body1["d"]["results"])):
            
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,bot_memo['index'] ,len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],'','','',bot_memo['scrapped_po_no']
   
        else:
            
            final_reply_string = 'I think there are no more pending approvals for you. Say, "get my tasks", to get your pending approvals.'
            return final_reply_string,bot_memo['index'],len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],'','','',bot_memo['scrapped_po_no']

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

        # response = session.head("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header)
        # if (response.status_code != 200):
        #     return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no']
        # elif (response.status_code == 200):
        #     cookie = session.cookies.get_dict()
        #     print(cookie)

        #     csrf = response.headers['x-csrf-token']
        #     #print(csrf)

        #     #post
        #     #approve
        #     header_2 = {'x-csrf-token':csrf}
        #     approve_po = session.post("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+present_task_instance_id +"'""&DecisionKey='0001'&Comments='test%20approve'",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'),headers=header_2,cookies=cookie)

        #     print('***************************************************************')
        #     print(approve_po.status_code)

        # approval request posted asynchronously
        url3 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
        head_res1 = (grequests.head(u,auth=('pritamsa','rupu@0801'),headers=header)for u in url3)
        #both imap and map can be used
        #reque = grequests.imap(rs,size=1)
        reque3 = grequests.map(head_res1,size=1)
        response_array3 = []
        for response3 in reque3:

            if (response3.status_code != 200):
                print("hey problem")
                return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no']
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
                        print("hey problem in approving the request. Please try again later.")
                        return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no']
                        
                    else:

                        return after_approval_reply,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],after_approval_reply,'','',bot_memo['scrapped_po_no'] #after this call the "next" task showing skill in bot

    
    # THIS LOGIC BELOW NEEDS TO BE RE_WRITTEN
    #************************************************************************************************************
    
    # elif((bot_nlp['ordinal'] and len(bot_nlp['ordinal']) <= bot_memo['no_of_line_items']) and present_skill == 'get_item_details'):
    elif (present_skill == 'get_item_details'):
        if (bot_nlp['ordinal'] and len(bot_nlp['ordinal']) <= bot_memo['no_of_line_items']):
            # filter_item_ordinally = 'item : '+ (bot_nlp['ordinal'][bot_nlp['ordinal']['index']]['rank'])
            # print(filter_item_ordinally)
            print('///////////////////////////////////////////////////')
            nlp_ordinal_filter_index = bot_nlp['ordinal'][0]['index']  #this is the first element's index of nlp entity ordinal array
            individual_item_filter_string = 'item : ' + str(nlp_ordinal_filter_index + 1)
            item_level_reply_ordinally = bot_memo['all_item_details'][individual_item_filter_string]
            print(item_level_reply_ordinally)

            return  str(item_level_reply_ordinally),bot_memo['index'],bot_memo['instanceID'],bot_memo['created_by'], bot_memo['SupplierName'],bot_memo['PurchaseOrderNetAmount'],bot_memo['after_approval_reply'],bot_memo['all_item_details'],bot_memo['no_of_line_items'],bot_memo['scrapped_po_no']


        elif(bot_nlp['ordinal']==False and bot_nlp['number'] and len(bot_nlp['number']) <= bot_memo['no_of_line_items']):
            # filter_item_ordinally = 'item : '+ (bot_nlp['ordinal'][bot_nlp['ordinal']['index']]['rank'])
            # print(filter_item_ordinally)
            print('///////////////////////////////////////////////////')
            nlp_number_filter_index = bot_nlp['number'][0]['scalar']  #this is the first element's index of nlp entity ordinal array
            individual_item_filter_string = 'item : ' + str(nlp_number_filter_index)
            item_level_reply_numerically = bot_memo['all_item_details'][individual_item_filter_string]
            print(item_level_reply_numerically)
            
            return  str(item_level_reply_numerically),bot_memo['index'],bot_memo['instanceID'],bot_memo['created_by'], bot_memo['SupplierName'],bot_memo['PurchaseOrderNetAmount'],bot_memo['after_approval_reply'],bot_memo['all_item_details'],bot_memo['no_of_line_items'],bot_memo['scrapped_po_no']

@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)



#app.run(port=port)

app.run(port=port, host="0.0.0.0")
