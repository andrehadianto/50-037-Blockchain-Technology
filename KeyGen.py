import ecdsa
import binascii


def generateKeyPair():
    sender_sk = ecdsa.SigningKey.generate()
    sender_vk = sender_sk.get_verifying_key()
    return sender_sk, sender_vk


def generateSignature(message):
    sender_sk = ecdsa.SigningKey.generate()
    sender_vk = sender_sk.get_verifying_key()
    signature = sender_vk.sign(message.encode('utf-8'))
    return signature, sender_vk


def signWithPrivateKey(message, sender_vk):
    sender_sk = binascii.unhexlify(sender_vk.encode('ascii'))
    sender_sk = ecdsa.SigningKey.from_string(sender_sk)
    signature = sender_sk.sign(message.encode('utf-8'))
    return signature


def verifyingExisting(message, sender_vk, signature):
    sender_vk = binascii.unhexlify(sender_vk.encode('ascii'))
    sender_vk = ecdsa.VerifyingKey.from_string(sender_vk)
    return sender_vk.verify(signature, message.encode('utf-8'))


def generateVerifyingKeyPairs():
    message = "50037 Blockhain SUTD"
    signature, sender_vk = generateSignature(message)
    return verifyingExisting(message, sender_vk, signature)
