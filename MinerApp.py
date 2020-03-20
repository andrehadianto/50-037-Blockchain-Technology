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

app = Flask(__name__)

priv_key, pub_key = generateKeyPair()
priv_key = priv_key.to_string().hex()
pub_key = pub_key.to_string().hex()
sutdcoin = Blockchain()
print('Genesis block generated')
myMiner = Miner(pub_key, sutdcoin)

@app.route('/listen', methods=["POST"])
def listen_to_broadcast(): 
    print("I am receiving from: {}".format(request.remote_addr))
    try:
        json = json.loads(request.get_json())
        print(json)
        return 'success', 200
    except Exception as e:
        return {"Exception": str(e)}, 500


@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    try:
        params = request.get_json()
        # Transaction(params[])
    except Exception as e:
        return {"Exception": str(e)}, 500

@app.route('/announce/<port>')
def announce(port):
    print("I am announcing to: {}".format(port))
    try:
        block = Block()
        form = {"msg": "hello from {}".format(PORT)}
        form = json.dumps(form)
        r = requests.post("http://localhost:5005/", json=form)
    except Exception as e:
        return {"Exception": str(e)}, 500
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400

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
