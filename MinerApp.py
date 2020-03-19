from flask import Flask, request, redirect
import requests
from Miner import Miner
import json
import os
import argparse

PORT = 5000

BLOCKCHAIN_IP = 'http://localhost'
BLOCKCHAIN_PORT = '5001'
BLOCKCHAIN_APP = BLOCKCHAIN_IP+':'+BLOCKCHAIN_PORT

app = Flask(__name__)

blockchain = ""
user_id = ""

@app.route('/', methods=["POST"])
def root():
  print("my port is: {}".format(PORT))
  jsonn = request.get_json()
  print(json.loads(jsonn)["msg"])
  return "success", 200
  
@app.route('/announce')
def announce():
  print('announcing')
  form = {"msg": "hello from {}".format(PORT)}
  form = json.dumps(form)
  r = requests.post("http://localhost:5005/", json=form)
  if r.ok:
    return 'success', 200
  else:
    return 'not ok', 400


@app.route('/update')
def update():
  update_from_blockchain = True

@app.route('/register_miner', methods=["POST"])
def create_miner():
  if request.method == "POST":
    try:
      blockchain = request.form["blockchain"]
      user_id = request.form["user_id"]
    except:
      return "missing parameters", 400
    miner = Miner(user_id, blockchain)
    return ("miner " + user_id + " has been created", 200)

@app.route('/start_mining')
def start_mining():
  while True:
    blockchain = requests.get(BLOCKCHAIN_APP+'/get_blockchain')
    
  return (user_id + ' starts mining')

@app.route('/add_user', methods=["POST"])
def add_user():
  if request.method == "POST":
    try:
      pub_key = request.form['pub_key']
      priv_key = request.form['priv_key']
      balance = request.form['balance']
    except:
      return "missing parameters", 400
    user_db[pub_key] = {"priv_key": priv_key, "balance": balance}
    return "user successfully added", 200

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Configure miners")
  parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
  args = parser.parse_args()
  PORT = args.port

  app.run("0.0.0.0", port=PORT, debug=True)


