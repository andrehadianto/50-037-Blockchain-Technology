import requests
import argparse
import json
from threading import Thread
import time


def mine_healthy_4():
    return requests.get("http://localhost:{}/start_mining".format(5004))

def mine_healthy_5():
    return requests.get("http://localhost:{}/start_mining".format(5005))


def create_trans(json_to_send):
    r = requests.post("http://localhost:{}/create_transaction".format(5004),json=json_to_send)


# mining and coin creationg
# fork resolution
def start_mining():
    # port_list = [5004,5005]
    # for port in port_list:
    #     thread = Thread(target = )
    #     thread.start()
    t1 = Thread(target = mine_healthy_4)
    t2 = Thread(target = mine_healthy_5)
    t1.start()
    t2.start()


# transaction resending protection
# payments between miners and SPV clients
def creating_transactions():
    json_to_send = {}
    json_to_send['amount'] = 20
    json_to_send['comment'] = 'This is a transaction'
    json_to_send['receiver'] = 'pawel'
    start_mining()
    time.sleep(5)
    print('need to wait for miners to mine empty blocks, for coin creation')
    t1 = Thread(target = create_trans,args=[json_to_send])
    t1.start()



# attacks from previous week : 51% attack
def attack_51():
    # PORT_LIST = [7337, 7338, 5005]
    # PORT_LIST_51 = [7337, 7338]
    # for port in PORT_LIST:
        # r = requests.get()
        # print("The 51% miner is http://localhost:{}/start_mining_51".format(7337))
        # r = requests.get("http://localhost:{}/start_mining_51".format(7338))
        # print("The 51% miner is http://localhost:{}/start_mining_51".format(7338))
        # r = requests.get("http://localhost:{}/start_mining".format(5005))
    # print("The honest miner is http://localhost:{}/start_mining".format(5005))
    t1 = Thread(target = requests.get,args=["http://localhost:{}/start_mining_51".format(7337)])
    t1.start()
    t2 = Thread(target = requests.get,args=["http://localhost:{}/start_mining_51".format(7338)])
    t2.start()
    t3 = Thread(target = requests.get,args=["http://localhost:{}/start_mining".format(5005)])
    t3.start()


# attacks from previous week : selfish mining
def selfish_mining():
    # r = requests.get("http://localhost:{}/start_mining".format(5004))
    # print("The honest miner is http://localhost:{}/start_mining".format(5004))
    # r = requests.get("http://localhost:{}/selfish_mining".format(5005))
    # print("The selfish miner is http://localhost:{}/start_selfish_mining".format(5005))
    t1 = Thread(target = requests.get,args=["http://localhost:{}/start_mining".format(5004)])
    t1.start()
    t2 = Thread(target = requests.get,args=["http://localhost:{}/start_selfish_mining".format(5005)])
    t2.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure miners")
    parser.add_argument('-m', '--mode', type=int, help="type of simulation" )
    args = parser.parse_args()
    if args.mode == 1:
        start_mining()
    elif args.mode == 2:
        creating_transactions()
    elif args.mode == 3:
        selfish_mining()
    else:
        attack_51()
         
