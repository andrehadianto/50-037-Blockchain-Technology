import hashlib
import random
import time
import math
import json
import cbor
import base64
from ecdsa import SigningKey, VerifyingKey, NIST384p
from KeyGen import generateKeyPair


class Transaction(object):

    def __init__(self, sender, receiver, amount, comment, timestamp=int(time.time()), signature=0):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.comment = comment
        self.timestamp = timestamp
        self.signature = signature

    def __eq__(self, transaction):
        return True if self.sender == transaction.sender and self.receiver == transaction.receiver and self.amount == transaction.amount else False

    @classmethod
    def new(cls, sender, receiver, amount, comment):
        t1 = Transaction(sender, receiver, amount, comment)
        return t1

    def serialize(self):
        props = {}
        props["receiver"] = self.receiver
        props["sender"] = self.sender
        props["amount"] = self.amount
        props["comment"] = self.comment
        props["timestamp"] = self.timestamp
        props["signature"] = self.signature
        return json.dumps(props)

    @classmethod
    def deserialize(cls, js_string):
        obj = json.loads(js_string)
        trans = Transaction(obj['sender'], obj['receiver'],
                            obj['amount'], obj['comment'], obj['timestamp'], obj['signature'])
        return trans

    def sign(self, priv_key):
        s = self.serialize().encode()
        sig = priv_key.sign(s)
        self.signature = sig.hex()

    def validate_signature(self):
        ser = {"receiver": self.receiver, "sender": self.sender, "amount": self.amount, "comment": self.comment, "timestamp": self.timestamp, "signature": 0}
        ser = json.dumps(ser).encode()
        return VerifyingKey.from_string(bytes.fromhex(self.sender)).verify(bytes.fromhex(self.signature), ser)