from flask import Flask, request, jsonify
import json
import requests
import os
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
#port = 5000
port = int(os.environ.get("PORT", 5000))

@app.route('/', methods=['POST'])
def index():
    data = json.loads(request.get_data())  # gets the data from chatbot that is json body of bot memory
    
    
    print(data)
    print()
    print()
    # FETCH THE CRYPTO NAME
    bot_conversation = data['conversation']
    bot_memo = data['conversation']['memory']
    #bot_memo_index_prsent_value = data['conversation']['memory']['index']
    present_skill = data['conversation']['skill']
    print(bot_conversation)

    # FETCH BTC/USD/EUR PRICES
    #here the back end odata api must be called
    #r = requests.get("https://min-api.cryptocompare.com/data/price?fsym="+crypto_name+"&tsyms=BTC,USD,EUR")
    

    #test task list
    #these data will be fetched from oddata api later on
    #call the backend odata api here to get the current task id and the po header and item details
    task_list = ['task1', 'task2', 'task3']
    #task_list = []
    po_header_item_detail = ['po_no: 1 \ncustomer: a', 'po_no: 2 \ncustomer: b', 'po_no: 3 \ncustomer: c']
    task_detail_dict = dict(zip(task_list,po_header_item_detail))

    #handling logic
    
    if (present_skill == 'get_task'):
        #bot_memo_index_prsent_value = data['conversation']['memory']['index']
        reply = query_get_task_with_details(data['conversation']['memory'])
        return jsonify(
            status=200,
            replies=[{
            'type': 'text',
            'content': reply
            #'content': 'here is your first task \n'+ task_list[0] + '\n' + task_detail_dict[task_list[0]],
        
            }],
            conversation={ 
        'memory': {} 
        } 
        )

    

    elif (present_skill == 'get_next_task' and task_list and data['conversation']['memory']['index'] < len(task_list)):

    
        return jsonify(
            status=200,
            replies=[{
            'type': 'text',
            'content': 'your next task \n'+ task_list[data['conversation']['memory']['index']] + '\n' + task_detail_dict[task_list[data['conversation']['memory']['index']]],
            #'content': 'The price of %s is %f BTC and %f USD' % (crypto_name, r.json()['BTC'], r.json()['USD'])
            }],
            conversation={ 
        'memory': { 'index': data['conversation']['memory']['index'] + 1} 
        } 
        )


    elif (present_skill == 'repeat'):
        return jsonify(
            status=200,
            replies=[{
            'type': 'text',
            'content': 'your next task \n'+ task_list[data['conversation']['memory']['index']-1] + '\n' + task_detail_dict[task_list[data['conversation']['memory']['index']-1]],
            #'content': 'The price of %s is %f BTC and %f USD' % (crypto_name, r.json()['BTC'], r.json()['USD'])
            }],
            conversation={ 
        'memory': { 'index': data['conversation']['memory']['index']} 
        } 
        )

   
    else:

        return jsonify(
            status=200,
            replies=[{
            'type': 'text',
            'content': 'no more tasks to approve in your inbox',
            #'content': 'The price of %s is %f BTC and %f USD' % (crypto_name, r.json()['BTC'], r.json()['USD'])
            }],
            conversation={ 
        'memory': {'index':data['conversation']['memory']['index']} 
        } 
        )

def query_get_task_with_details(bot_memo):
    if (bot_memo == {} or bot_memo[['index']]):
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
            
            
            response_po_item_detail = requests.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/ALEXA_ALL/C_PURCHASEORDER_FS_SRV;o=sid(M17.400)/C_PurchaseOrderFs(PurchaseOrder="+ "'"+scrapped_po_no +"'"")/to_PurchaseOrderItem?sap-client=400&$format=json",auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))

            body2 = response_po_detail_header.json()
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


            #print(final_reply_string)
            return final_reply_string

        else:
            final_reply_string = 'no tasks to approve...'
            return final_reply_string

    
   

    





@app.route('/test', methods=['POST'])
def test():
    data = json.loads(request.get_data())
    present_skill = data['conversation']['skill']
    if(present_skill == 'test'):
        return jsonify(
                    status=200,
                    replies=[{
                    'type': 'text',
                    'content': 'testing testing',
                    
                    }],
                    conversation={ 
                'memory': {'index':15} 
                } 
                )
    

@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)



#app.run(port=port)

app.run(port=port, host="0.0.0.0")
