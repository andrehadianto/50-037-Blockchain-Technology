from flask import Flask, request, redirect
import requests
import json
import os
import time
import argparse
from Block import Block
from Blockchain import Blockchain
from Miner import Miner
from Transaction import Transaction
from KeyGen import generateKeyPair
import cbor

app = Flask(__name__)

FOUNDER = 'pawel'.encode('utf-8').hex()
PORT_LIST = [5004, 5005]

u1_priv, u1_pub = "111", "112"
u1_priv = u1_priv.encode('utf-8').hex()
u1_pub = u1_pub.encode('utf-8').hex()

u2_priv, u2_pub = "211", "212"
u2_priv = u2_priv.encode('utf-8').hex()
u2_pub = u2_pub.encode('utf-8').hex()

u3_priv, u3_pub = "311", "312"
u3_priv = u3_priv.encode('utf-8').hex()
u3_pub = u3_pub.encode('utf-8').hex()


sutdcoin = Blockchain()
t1 = Transaction(FOUNDER, u2_pub, 50, "T1")
t2 = Transaction(FOUNDER, u1_pub, 50, "T2")
t3 = Transaction(FOUNDER, u1_pub, 50, "T3")
t4 = Transaction(FOUNDER, u2_pub, 50, "T4")
t5 = Transaction(FOUNDER, u2_pub, 50, "T5")
t_list = [t1, t2, t3, t4, t5]

print('Genesis block generated')


@app.route('/listen', methods=["POST"])
def listen_to_broadcast():
    print('LISTENING')
    res = json.loads(request.get_json())
    ## create block ##
    transaction_list = []
    for trans in res["transactions"]:
        transaction_list.append(Transaction.deserialize(trans))
    block = Block(transaction_list, res['header']
                  ['prev_header'], res['miner_id'], res['header']['nonce'], res['header']['timestamp'])
    print("LISTEN API")
    print(block.get_header())
    myMiner.new_block_queue.append(block)
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

def announce(block):
    for port in PORT_LIST:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        try:
            data = {}
            data['header'] = block.get_header()
            transactions_to_send = []
            for trans in block.merkle_tree.past_transactions:
                transactions_to_send.append(trans.serialize())
            data['transactions'] = transactions_to_send
            data['miner_id'] = myMiner.miner_id

            form = json.dumps(data)
            print('sending now')
            r = requests.post(
                "http://localhost:{}/listen".format(port), json=form)
            print('done sending')
        except Exception as e:
            return {"Exception": str(e)}, 500
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400


@app.route('/start_mining')
def start_mining():
    myMiner.isMining = True
    time.sleep(2)
    while True:
        # try:
        res = myMiner.start_mining()
        if res == "receive new announcement block":
            continue
        elif res == "error":
            continue
            # announce res(new_block) to other miners
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce(res)
        print("==============BLOCKCHAIN===========")
        for k, v in sutdcoin.blockchain_graph.items():
            print("-----")
            print(k)
            print("height:", v['height'])
            print("block:", v['block'].get_header())
            print("balance map:", v['balance_map'])
            print("children:", v['children'])
            print("\n")
        print("==================================")

@app.route('/update')
def update():
    update_from_blockchain = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure miners")
    parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
    parser.add_argument('-n', '--name', type=str, required=True, help="NAME")
    args = parser.parse_args()

    myMiner = Miner(args.name.encode('utf-8').hex(), sutdcoin, t_list)
    PORT = args.port
    app.run("0.0.0.0", port=PORT, debug=True)
