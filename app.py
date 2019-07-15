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
    
    if (present_skill == 'get_task' and task_list):
    
        return jsonify(
            status=200,
            replies=[{
            'type': 'text',
            'content': 'here is your first task \n'+ task_list[0] + '\n' + task_detail_dict[task_list[0]],
            #'content': 'The price of %s is %f BTC and %f USD' % (crypto_name, r.json()['BTC'], r.json()['USD'])
            }],
            conversation={ 
        'memory': { 'index': 1 } 
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

    # elif(present_skill == 'test'):
    #     #@app.route('/test', methods=['POST'])
    #     #r = request.get("https://p2001172697trial-trial.apim1.hanatrial.ondemand.com/p2001172697trial/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs(PurchaseOrder='4500000352')?$format=json", auth=HTTPBasicAuth('pritamsa', 'rupu@0801'))
    #     #body_test = r.json()
    #     #s = body_test["d"]["PurchaseOrder_Text"]
    #     return jsonify(
    #             status=200,
    #             replies=[{
    #             'type': 'text',
    #             'content': 'testing testing',
                
    #             }],
    #             conversation={ 
    #         'memory': {} 
    #         } 
    #         )
 
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
                'memory': {} 
                } 
                )
    

@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)



#app.run(port=port)

app.run(port=port, host="0.0.0.0")
