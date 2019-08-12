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


def get_taskONEbyONE(bot_memo,present_skill,bot_nlp):

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

        suggestion_reply = ''

        if (eval(PurchaseOrderNetAmount) <= 7000):
            suggestion_reply = "I suggest you to approve or release this."
        else:
            suggestion_reply = "I dont have a suggestion for this approval now. you can get details before taking any action."

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

        #final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
        final_reply_string = 'you have, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items in this purchase order.\n'+ suggestion_reply


        return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no,'','' #return 1for memory index as no memo is present in the beggining

    else:
        final_reply_string = 'no more tasks to approve in your inbox.'
        return final_reply_string,1,bot_memo,bot_memo,bot_memo, bot_memo,'','','',bot_memo,'',''



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

    


    reply,index,instanceID,created_by_user,SupplierName,PurchaseOrderNetAmount,after_approval_reply,all_item_details,no_of_line_items,scrapped_po_no, final_batch_instance_amount_dict,final_batch_instance_id_list = query_get_task_with_details(data['conversation']['memory'],present_skill,bot_nlp)
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
    'scrapped_po_no':scrapped_po_no,
    'final_batch_instance_id_list':final_batch_instance_id_list,
    'final_batch_instance_amount_dict':final_batch_instance_amount_dict
    } 
    } 
    )

    
    

   
   
def query_get_task_with_details(bot_memo,present_skill,bot_nlp):

    if ((bot_memo == {} or bot_memo['index']) and present_skill == 'get_task_one_by_one'):

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

            suggestion_reply = ''

            if (eval(PurchaseOrderNetAmount) <= 7000):
                suggestion_reply = "I suggest you to approve or release this."
            else:
                suggestion_reply = "I dont have a suggestion for this approval now. you can get details before taking any action."

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

            #final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ concat_string_for_multiple_lineitems + " say approve to approve this task or say ignore to skip this task and move on to your next task, or say next to get your next task with details."
            final_reply_string = 'you have, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items in this purchase order.\n'+ suggestion_reply


            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no,'','' #return 1for memory index as no memo is present in the beggining

        else:
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,1,bot_memo,bot_memo,bot_memo, bot_memo,'','','',bot_memo,'',''

    #gets all the available tasks in my inbox and suggests user after validation of conditions for batch approvals
    if ((bot_memo == {} or bot_memo['index']) and present_skill == 'get_task'):
        final_reply_string = ''

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
            print("///////////////////////// hey     hey //////////")
            print(final_batch_instance_id_list)
            #if there are no tasks to safely approve
            if (len(final_batch_instance_id_list) <= 0):
                #call get tasks one by one function

                reply,index,instanceID,created_by_user,SupplierName,PurchaseOrderNetAmount,after_approval_reply,all_item_details,no_of_line_items,scrapped_po_no, final_batch_instance_amount_dict,final_batch_instance_id_list = get_taskONEbyONE(bot_memo,present_skill,bot_nlp)

                return  reply,1,instance_id,created_by_user,SupplierName, PurchaseOrderNetAmount,after_approval_reply,all_item_details,no_of_line_items,scrapped_po_no,'','' #return 1for memory index as no memo is present in the beggining

            else:
                print('*********************************************')
                print(final_batch_instance_amount_dict)

                final_reply_string = "you have," + str(no_of_tasks) + "pending approvals." + "You can safely approve," + str(len(final_batch_instance_id_list)) + "of them on the go. Say, yes, to approve all, and no to get your tasks one by one."

                return  final_reply_string,1,'','','', '','','','','',final_batch_instance_amount_dict,final_batch_instance_id_list
            
        else:
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,1,'','','', '','','','','',final_batch_instance_amount_dict,final_batch_instance_id_list

    
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

            
            suggestion_reply = ''

            if (eval(PurchaseOrderNetAmount) <= 7000):
                suggestion_reply = "I suggest you to approve or release this."
            else:
                suggestion_reply = "I dont have a suggestion for this approval now. you can get details before taking any action."

            
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
            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ suggestion_reply

            return  final_reply_string,1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no,'','' #return 1for memory index as no memo is present in the beggining


       
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

            
            suggestion_reply = ''

            if (eval(PurchaseOrderNetAmount) <= 7000):
                suggestion_reply = "I suggest you to approve or release this."
            else:
                suggestion_reply = "I dont have a suggestion for this approval now. you can get details before taking any action."

            
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
            final_reply_string = 'Now you have got, '+ str(no_of_tasks) + ' pending tasks to approve. ' + get_task_string + get_task_string_with_header_detail +'You have: ' + str(no_of_line_items) +' items.\n'+ suggestion_reply

            #print(get_task_string)


            #print(final_reply_string)
            return final_reply_string,bot_memo['index'] + 1,instance_id,created_by_user,SupplierName, (PurchaseOrderNetAmount + ' ' + DocumentCurrency),'',all_item_details,no_of_line_items,scrapped_po_no,'',''

        elif(len(body1["d"]["results"]) > 0)and(bot_memo['index'] >= len(body1["d"]["results"])):
            
            final_reply_string = 'no more tasks to approve in your inbox.'
            return final_reply_string,bot_memo['index'] ,len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],'','','',bot_memo['scrapped_po_no'],'',''
   
        else:
            
            final_reply_string = 'I think there are no more pending approvals for you. Say, "get my tasks", to get your pending approvals.'
            return final_reply_string,bot_memo['index'],len(body1["d"]["results"]),bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],'','','',bot_memo['scrapped_po_no'],'',''

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
                return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no'],'',''
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
                        return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no'],''
                        
                    else:

                        return after_approval_reply,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],after_approval_reply,'','',bot_memo['scrapped_po_no'],'','' #after this call the "next" task showing skill in bot

    
    
    elif((bot_memo['index']) and present_skill == 'reject'):
        after_rejection_reply = 'successfully rejected, please say,"get my tasks", to get your previous pending aapprovals from the beggining, or, say next to move on to your next task.'
        rejection_failure_reply = "there was an issue with the server, Please try again later to approve..."
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
        url4 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
        head_res4 = (grequests.head(u,auth=('pritamsa','rupu@0801'),headers=header)for u in url4)
        #both imap and map can be used
        #reque = grequests.imap(rs,size=1)
        reque4 = grequests.map(head_res4,size=1)
        response_array4 = []
        for response4 in reque4:

            if (response4.status_code != 200):
                print("hey problem")
                return rejection_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],rejection_failure_reply,'','',bot_memo['scrapped_po_no'],'',''
            else:
                cookie = response4.cookies.get_dict()
                print(cookie)

                csrf = response4.headers['x-csrf-token']
                print(csrf)

                header_2 = {'x-csrf-token':csrf}

                url_post = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+present_task_instance_id +"'""&DecisionKey='0002'&Comments='test%20reject'"]
                post_res = (grequests.post(u_post,auth=('pritamsa','rupu@0801'),headers=header_2,cookies=cookie)for u_post in url_post)

                post_reque = grequests.map(post_res,size=1)
                response_array_post = []
                for response_post in post_reque:

                    if (response_post.status_code != 200):
                        print("hey problem in rejecting P.O. . Please try again later.")
                        return rejection_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],rejection_failure_reply,'','',bot_memo['scrapped_po_no'],'',''
                        
                    else:

                        return after_rejection_reply,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],after_rejection_reply,'','',bot_memo['scrapped_po_no'],'','' #after this call the "next" task showing skill in bot

    
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

            return  str(item_level_reply_ordinally).strip('{}'),bot_memo['index'],bot_memo['instanceID'],bot_memo['created_by'], bot_memo['SupplierName'],bot_memo['PurchaseOrderNetAmount'],bot_memo['after_approval_reply'],bot_memo['all_item_details'],bot_memo['no_of_line_items'],bot_memo['scrapped_po_no'],'',''


        elif(bot_nlp['ordinal']==False and bot_nlp['number'] and len(bot_nlp['number']) <= bot_memo['no_of_line_items']):
            # filter_item_ordinally = 'item : '+ (bot_nlp['ordinal'][bot_nlp['ordinal']['index']]['rank'])
            # print(filter_item_ordinally)
            print('///////////////////////////////////////////////////')
            nlp_number_filter_index = bot_nlp['number'][0]['scalar']  #this is the first element's index of nlp entity ordinal array
            individual_item_filter_string = 'item : ' + str(nlp_number_filter_index)
            item_level_reply_numerically = bot_memo['all_item_details'][individual_item_filter_string]
            print(item_level_reply_numerically)
            
            return  str(item_level_reply_numerically),bot_memo['index'],bot_memo['instanceID'],bot_memo['created_by'], bot_memo['SupplierName'],bot_memo['PurchaseOrderNetAmount'],bot_memo['after_approval_reply'],bot_memo['all_item_details'],bot_memo['no_of_line_items'],bot_memo['scrapped_po_no'],'',''


    elif((bot_memo['final_batch_instance_amount_dict'] or bot_memo['final_batch_instance_id_list']) and present_skill == 'yes_approve_all'):
         

        after_approval_reply = 'successfully approved all tasks in batch.'
        approval_failure_reply = "there was an issue with the server, Please try again later to approve..."
       
        header = {'x-csrf-token':'Fetch'}


        url_maker_approve_array = []

        for inst in bot_memo['final_batch_instance_id_list']: 
            url_maker_approve = "https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/Decision?sap-client=400&SAP__Origin='S4HMYINBOCLNT200'&InstanceID="+ "'"+inst +"'""&DecisionKey='0001'&Comments='test%20approved_in_batch'"
            url_maker_approve_array.append(url_maker_approve)


        all_csrf = []

        url3 = ["https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/Workflow_approval/TaskCollection?sap-client=400&$filter=Status%20eq%20%27READY%27&$format=json"]
        head_res1 = (grequests.head(u,auth=('pritamsa','rupu@0801'),headers=header)for u in url3)
            
        reque3 = grequests.map(head_res1,size=len(url_maker_approve_array))

        print('********************')
        # print(reque3)




        if (reque3[0].status_code != 200):
            print("hey problem")
            return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no'],bot_memo['final_batch_instance_id_list'],bot_memo['final_batch_instance_amount_dict']
        else:
            cookie = reque3[0].cookies.get_dict()
                # print(cookie)

            csrf = reque3[0].headers['x-csrf-token'] #get one csrf to pass as header in post request
            # print(csrf)


                #post


            header_2 = {'x-csrf-token':csrf}


                
            # all_csrf.append(header_2)  #all csrf received at once which is of the length of suggested number of instances that can be approved
        
                
                
            post_res = (grequests.post(u_post,auth=('pritamsa','rupu@0801'),headers=header_2,cookies=cookie)for u_post in url_maker_approve_array)

            post_reque = grequests.map(post_res,size=10)
            response_array_post = []
            for response_post in post_reque:

                if (response_post.status_code != 200):
                    print("hey problem in approving the request. Please try again later.")
                    return approval_failure_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no'],bot_memo['final_batch_instance_id_list'],bot_memo['final_batch_instance_amount_dict']

                else:
                    print("approved suggested tasks in batch...")
                    return after_approval_reply ,bot_memo['index'],present_task_instance_id,bot_memo['created_by'],bot_memo['SupplierName'], bot_memo['PurchaseOrderNetAmount'],approval_failure_reply,'','',bot_memo['scrapped_po_no'],bot_memo['final_batch_instance_id_list'],bot_memo['final_batch_instance_amount_dict']


@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)



#app.run(port=port)

app.run(port=port, host="0.0.0.0")
