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
import hashlib

app = Flask(__name__)


FOUNDER = 'pawel'.encode('utf-8').hex()

# SET OWN MINER KEYPAIR
priv_key, pub_key = generateKeyPair()
priv_key = priv_key.to_string().hex()
pub_key = pub_key.to_string().hex()
print(pub_key)


sutdcoin = Blockchain()
print('===Genesis block generated===')
print("My ID:", pub_key)



parser = argparse.ArgumentParser(description="Configure miners")
parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
parser.add_argument('-s', '--simulation', type=str, required=False, help="type of simulation: normal, 51, selfish")
args = parser.parse_args()
print(args)
if args.simulation == "normal" or args.simulation == "selfish":
    PORT_LIST = [5004, 5005]
    PORT_LIST_51 = []
elif args.simulation == "51":
    PORT_LIST = [7337, 7338, 5005]
    PORT_LIST_51 = [7337, 7338]
SPVAPP_PORT = 8080

stopEvil = False

@app.route('/show_graph')
def showGraph():
    longest_block = sutdcoin.blockchain_graph[sutdcoin.longest_header]["block"]
    block_list = sutdcoin.createChainToParentBlock(longest_block)
    block_list.insert(0, longest_block)
    block_list.reverse()

    longest_graph = [block.hash_header()[-6:] for block in block_list]
    print("=============BLOCKCHAIN=============")
    string = " -> ".join(longest_graph)
    print(string)
    print("==================================")
    for k, v in sutdcoin.blockchain_graph.items():
        print("-----")
        print(k[-6:])
        print("owner:", v["block"].miner_id)
        print("height:", v['height'])
        # print("block:", v['block'].get_header())
        # print("balance map:", ["{} : {}".format(key[-6:],val) for key,val in v['balance_map'].items()])
        print("children:", [child[-6:] for child in v['children']])
    print("==================================")
    return "200"


    # print("==============BLOCKCHAIN===========")
    # for k, v in sutdcoin.blockchain_graph.items():
    #     print("-----")
    #     print(k[-6:])
    #     print("owner:", v["block"].miner_id)
    #     print("height:", v['height'])
    #     # print("block:", v['block'].get_header())
    #     print("balance map:", ["{} : {}".format(key[-6:],val) for key,val in v['balance_map'].items()])
    #     print("children:", [child[-6:] for child in v['children']])
    # print("==================================")
    # return "200"

@app.route('/create_transaction', methods=["POST"])
def prepare_transaction_to_send():
    res = request.get_json()
    amount = res["amount"]
    comment = res["comment"]
    receiver = res["receiver"]

    data = {}
    data["pub_key"] = pub_key
    data["priv_key"] = priv_key
    data["receiver"] = receiver.encode('utf-8').hex()
    data["amount"] = amount
    data["comment"] = comment
    data = json.dumps(data)
    r = requests.post("http://localhost:{}/broadcast_transactions".format(SPVAPP_PORT), json=data)
    return "200" if r.ok else "500"


@app.route('/new_transactions', methods=["POST"])
def update_transaction_pool():
    res = json.loads(request.get_json())

    sender = res["sender"]
    receiver = res["receiver"]
    amount = res["amount"]
    comment = res["comment"]
    timestamp = res["timestamp"]
    signature = res["signature"]

    trans = Transaction(sender, receiver, amount,
                        comment, timestamp, signature)
    if trans.validate_signature():
        myMiner.trans_pool.append(trans)
    else:
        return "500"
    return "200"

@app.route('/broadcast_listener', methods=["POST"])
def listenToBroadcast():
    print("===LISTENING===")
    res = json.loads(request.get_json())

    for data in res.values():
        difficulty = data["difficulty"]
        evil = data["evil"]
        transaction_list = []
        for trans in data["transactions"]:
            transaction_list.append(Transaction.deserialize(trans))
        block = Block(transaction_list, data['header']
                    ['prev_header'], data['miner_id'], data['header']['nonce'], data['header']['timestamp'])
        myMiner.new_block_queue.append([block, difficulty, evil])
    print("---------")
    return 'success', 200
    # except Exception as e:
    #     return {"Exception": str(e)}, 500
#     params = request.get_json()

@app.route('/stop_being_bad')
def stopBeingBad():
    print("=19*&$*7981&^)$=")
    global stopEvil
    stopEvil = True
    print("=cleansing successful=")
    return "success", 200

def announce(blocks, isEvil=False):
    print("===Announcing===")
    PORTS = PORT_LIST_51 if isEvil else PORT_LIST
    for port in PORTS:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        data = {}
        for i in range(len(blocks)):
            try:
                print("transmitting.., block_header =", blocks[i].hash_header()[-6:])
                data[i] = {}
                data[i]['header'] = blocks[i].get_header()
                data[i]['difficulty'] = sutdcoin.old_target
                data[i]["evil"] = "evil" if isEvil else "good"
                transactions_to_send = []
                for trans in blocks[i].merkle_tree.past_transactions:
                    transactions_to_send.append(trans.serialize())
                data[i]['transactions'] = transactions_to_send
                data[i]['miner_id'] = myMiner.miner_id
            except Exception as e:
                return {"Exception": str(e)}, 500
        form = json.dumps(data)
        r = requests.post(
            "http://localhost:{}/broadcast_listener".format(port), json=form)

    latest_block = sutdcoin.blockchain_graph[sutdcoin.longest_header]["block"]
    latest_chain = sutdcoin.createChainToParentBlock(latest_block)
    chain_of_headers = []
    for i in latest_chain:
        head = i.get_header()
        chain_of_headers.append(head)
    d1 = {}
    d1['list_headers'] = chain_of_headers
    d1['miner_port'] = args.port
    d1 = json.dumps(d1)
    r = requests.post("http://localhost:{}/headers".format(8080),json=d1)
    print("-----------------")
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400

def stop51Attack():
    print("===AnnouncingEVIL===")
    for port in PORT_LIST_51:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        r = requests.get("http://localhost:{}/stop_being_bad".format(port))
    print("-----------------")
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400


@app.route('/start_mining')
def start_mining():
    myMiner.isMining = True
    counter = 1
    while True:
        if counter % 5 == 0:
            r = showGraph()
        counter += 1
        try:
            res = myMiner.startMining()
            if res == "receive new block":
                continue
            elif res == "error":
                continue
        except Exception as e:
            return {"Exception": str(e)}, 500
        announce([res])
        
@app.route('/start_mining_51')
def start51Mining():
    myMiner.isMining = True
    good_length = 0
    
    while good_length < 3:
        #counter += 1
        # try:
        res = myMiner.startMining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
        good_length = len(sutdcoin.createChainToParentBlock(sutdcoin.blockchain_graph[sutdcoin.longest_header]["block"])) + 1
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce([res])

    print("COMMENCING EVIL DEEDS")
    evil_length = 0
    evil_head = sutdcoin.blockchain_graph["4a18a58e969d9281c65ff9fdc9443f23ce2484c532329a99c14f58b5eaef5120"]["children"][0]
    while evil_length <= good_length + 2 and not stopEvil:
        print('good chain length:', good_length)
        print('evil chain length:', evil_length)
        res = myMiner.start51Mining(evil_head)
        if res == "receive new block":
            print('received a good block')
            good_length += 1
            continue
        elif res == "receive evil block":
            evil_length += 1
            continue
        elif res == "error":
            continue
        if stopEvil:
            res = ""
            print("leaving evil deeds...")
            break
        print("EVIL FOUND NEW BLOCK ", res.hash_header()[-6:])
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        evil_head = res.hash_header() 
        evil_length = len(sutdcoin.createChainToParentBlock(res)) + 1
        announce([res], isEvil=True)
        if evil_length > good_length+2:
            stop51Attack()

    if type(res) is not str:
        evil_block_list = sutdcoin.createChainToParentBlock(res)
        evil_block_list.insert(0, res)
        if not stopEvil:
            evil_block_list.reverse()
            announce(evil_block_list)
    print("EVIL DEED IS DONE")
    r = showGraph()
    while True:
        res = myMiner.startMining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce([res])

@app.route('/start_selfish_mining')
def start_selfish_mining():
    myMiner.isMining = True
    list_of_priv_blocks = [] ## the lead, and not announced chain branch
    while True: 
        list_of_priv_blocks = []
        # show that selfish miner has worse computational power
        time.sleep(2)
        res = myMiner.startMining()
        if res == "receive new block" or myMiner.new_block_queue:
            # continue mining on public blockchain
            print('selfish recieve new block')
            continue
        else:
            while(not myMiner.new_block_queue):
                list_of_priv_blocks.append(res)
                res = myMiner.startMining()
                if type(res) is not str:
                    list_of_priv_blocks.append(res)
                    if len(list_of_priv_blocks)>=2:
                        announce(list_of_priv_blocks)
                        list_of_priv_blocks = []
                        print("SELFISH MINING SUCCESS")
                        r = showGraph()

@app.route('/start_mining_sequential')
def start_mining_sequential():
    myMiner.isMining = True
    # try:
    res = myMiner.startMining()
    if res == "receive new block":
        return "new", 200
    elif res == "error":
        return "error", 500
    # except Exception as e:
    #     return {"Exception": str(e)}, 500
    announce(res)
    print("==============BLOCKCHAIN===========")
    for k, v in sutdcoin.blockchain_graph.items():
        print("-----")
        print(k)
        print("owner:", v["block"].miner_id)
        print("height:", v['height'])
        # print("block:", v['block'].get_header())
        # print("balance map:", v['balance_map'])
        print("children:", v['children'])
    print("==================================")
    return "success", 200

@app.route('/update')
def update():
    update_from_blockchain = True


# @app.route('/my_transactions'):
# def verify_my_transaction:
#     r = requests.get("http://localhost:{}/list_transactions/{}".format(CLIENT_PORT,pub_key))
#     if r.ok:
#         return 200
#     else:
#         return 400

@app.route('/get_transactions', methods=['POST'])
def listening_to_my_transactions():
    user_pub_key = request.get_json()['pub']
    print(user_pub_key)
    # need to serialize transaction and then make on other side
    transactions_list = []
    data = {}
    # print(sutdcoin.blockchain_graph)
    last_block = sutdcoin.blockchain_graph[sutdcoin.longest_header]["block"]
    longest_chain = sutdcoin.createChainToParentBlock(last_block)
    longest_chain.insert(0,last_block)
    #blockchain_graph_items = sutdcoin.blockchain_graph.items()
    for block in longest_chain:
        for trans in block.merkle_tree.past_transactions:
            if trans.sender == user_pub_key or trans.receiver == user_pub_key:
                nodes, neighbour, index = block.merkle_tree.get_min_nodes(
                    trans)
                transactions_list.append(
                    [trans.serialize(), nodes, neighbour, index])

    data['transaction_list'] = transactions_list
    print("THE TRANSACTION LIST IS:", data)
    data = json.dumps(data)
    return data, 200


if __name__ == '__main__':
    myMiner = Miner(pub_key, sutdcoin)
    app.run(host="0.0.0.0", port=args.port, debug=True)
