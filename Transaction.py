import hashlib
import random
import time
import math
import json
import cbor
import base64
from ecdsa import SigningKey, VerifyingKey, NIST384p


class Transaction(object):

    def __init__(self, sender, receiver, amount, comment, timestamp=int(time.time())):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.comment = comment
        self.signature = None
        self.timestamp = timestamp

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
        return json.dumps(props)

    @classmethod
    def deserialize(cls, js_string):
        obj = json.loads(js_string)
        trans = Transaction(obj['sender'], obj['receiver'],
                            obj['amount'], obj['comment'], obj['timestamp'])
        # obj['sender'] = obj['sender'].encode('ascii')
        # obj['receiver'] = obj['receiver'].encode('ascii')
        # result = Transaction(VerifyingKey.from_string(base64.decodebytes(obj['sender']), curve=NIST384p), VerifyingKey.from_string(
        #     base64.decodebytes(obj['receiver']), curve=NIST384p), obj['amount'], obj['comment'])
        return trans

    def sign(self, priv_key):
        s = self.serialize().encode()
        sig = priv_key.sign(s)
        self.signature = sig
        return sig

    def validate_signature(self, pub_key):
        assert self.sender.verify(
            self.signature, self.serialize().encode()), "validation failed"
