from flask import Flask, request, redirect
import requests
import json
import os
import argparse
from Block import Block
from Blockchain import Blockchain
from Miner import Miner
from Transaction import Transaction
from KeyGen import generateKeyPair
import cbor


# BLOCKCHAIN_IP = 'http://localhost'
# BLOCKCHAIN_PORT = '5001'
# BLOCKCHAIN_APP = BLOCKCHAIN_IP+':'+BLOCKCHAIN_PORT

transaction_pool = []
send_priv,send_pub = generateKeyPair()
rec_priv,rec_pub = generateKeyPair()
t1= Transaction(send_pub.to_string().hex(),rec_pub.to_string().hex(),100,'asdasd')
transaction_pool.append(t1)
app = Flask(__name__)

# priv_key, pub_key = generateKeyPair()
# priv_key = priv_key.to_string().hex()
# pub_key = pub_key.to_string().hex()
# sutdcoin = Blockchain()
# print('Genesis block generated')
# myMiner = Miner(pub_key, sutdcoin)

@app.route('/listen', methods=["POST"])
def listen_to_broadcast(): 
    print('hello')
    # try:
    print(request.get_json())
    print(type(request.get_json()))
    jsonn = json.loads(request.get_json())
    print(type(json.loads(jsonn['transactions'][0])['comment']))
    print(json.loads(jsonn['transactions'][0])['comment'])
    # print(jsonn['transactions'][0]['comment'])
    # print(json[transactions][comment])
    return 'success', 200
    # except Exception as e:
    #     return {"Exception": str(e)}, 500
#     params = request.get_json()


# @app.route('/create_transaction', methods=['POST'])
# def create_transaction():
#     try:
#         params = request.get_json()
#         # Transaction(params[])
#     except Exception as e:
#         return {"Exception": str(e)}, 500

@app.route('/announce/<port>')
def announce(port):
    print("I am announcing to: {}".format(port))
    try:
        block = Block(transaction_pool,'i am genesis',rec_priv.to_string().hex())
        print('created block')
        dict_to_send = {}
        dict_to_send['header'] = block.header
        print('block serialized')
        transactions_to_send = []
        for t in transaction_pool:
            transactions_to_send.append(t.serialize())
        print('transactions added')
        dict_to_send['transactions'] = transactions_to_send
        dict_to_send['miner_id'] = rec_priv.to_string().hex()
        print('done serializing')
  
        form = json.dumps(dict_to_send)
        print(dict_to_send['transactions'])
        print('sending now')
        print(port)
        r = requests.post("http://localhost:{}/listen".format(port), json=form)
        print('done sending')
        if r.ok:
            return 'success', 200
        else:

            return 'not ok', 400
    except Exception as e:
        return {"Exception": str(e)}, 500
  

@app.route('/start_mining')
def start_mining():
    myMiner.isMining = True
    while True:
        # try:
        res = myMiner.start_mining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
            # announce res(new_block) to other miners
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        # print(sutdcoin.blockchain_graph)

@app.route('/update')
def update():
    update_from_blockchain = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure miners")
    parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
    args = parser.parse_args()
    PORT = args.port
    app.run("0.0.0.0", port=PORT, debug=True)




# @app.route('/register_miner', methods=["POST"])
# def create_miner():
#   if request.method == "POST":
#     try:
#       blockchain = request.form["blockchain"]
#       user_id = request.form["user_id"]
#     except:
#       return "missing parameters", 400
#     miner = Miner(user_id, blockchain)
#     return ("miner " + user_id + " has been created", 200)

# @app.route('/start_mining')
# def start_mining():
#   while True:
#     blockchain = requests.get(BLOCKCHAIN_APP+'/get_blockchain')

#   return (user_id + ' starts mining')

# @app.route('/add_user', methods=["POST"])
# def add_user():
#   if request.method == "POST":
#     try:
#       pub_key = request.form['pub_key']
#       priv_key = request.form['priv_key']
#       balance = request.form['balance']
#     except:
#       return "missing parameters", 400
#     user_db[pub_key] = {"priv_key": priv_key, "balance": balance}
#     return "user successfully added", 200
