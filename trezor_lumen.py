#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 22:57:06 2017

@author: 1Hr1619SxTuTBC3qYZJ1rkfAxrvWnt7bt3
"""

#%%
from stellar_base.address import Address
from stellar_base.operation import ChangeTrust
from stellar_base.asset import Asset
from stellar_base.horizon import horizon_livenet
from stellar_base.horizon import Horizon
from stellar_base.transaction_envelope import TransactionEnvelope as Te
from stellar_base.transaction import Transaction
from stellar_base.keypair import Keypair
from stellar_base.operation import Payment
horizon = Horizon('https://cryptodealer.hk')

#%%
import os
import hashlib
import json
import binascii
import sys

#%%

from trezorlib.client import TrezorClient
from trezorlib.transport_hid import HidTransport

#%%Interacting with Local Trezor hardware

def Wait_for_devices():
    devices = HidTransport.enumerate()
    while not len(devices):
        print("Please connect TREZOR to computer and press Enter...")
        input()
        devices = HidTransport.enumerate()

    return devices

def Choose_device(devices):
    if not len(devices):
        raise Exception("No TREZOR connected!")

    if len(devices) == 1:
        try:
            return HidTransport(devices[0])
        except OSError:
            raise Exception("Device is currently in use, try reconnect the device")

    i = 0
    print("----------------------------\n")
    print("Available devices:\n")
    for d in devices:
        try:
            client = TrezorClient(d)
        except OSError:
            sys.stderr.write("[-] <device is currently in use>\n")
            continue

        if client.features.label:
            print("[%d] %s\n" % (i, client.features.label))
        else:
            print("[%d] <no label>\n" % i)
        client.close()
        i += 1
        

    print("----------------------------\n")

    try:
        device_id = int(input("Please choose device to use:"))
        return HidTransport(devices[device_id])
    except:
        raise Exception("Invalid choice, exiting...")
        

def Create_wallet_file():
    # create the clinet object
    devices = Wait_for_devices()
    transport = Choose_device(devices)
    client = TrezorClient(transport)
    
    
    # Label your wallet, something like 'lumen'.
    print('Please provide label for new drive: ')
    label = input()
    
    print('Computer asked TREZOR for new strong password.\n')
    print('Please confirm action on your device.\n')
    trezor_entropy = client.get_entropy(32)
    urandom_entropy = os.urandom(32)
    passw = hashlib.sha256(trezor_entropy + urandom_entropy).digest()
    
    if len(passw) != 32:
        raise Exception("32 bytes password expected")
        
    bip32_path = [10, 0]
    passw_encrypted = client.encrypt_keyvalue(bip32_path, label, passw, False, True)

    wallet_info = {'label': label,
            'bip32_path': bip32_path,
            'password_encrypted_hex': binascii.hexlify(passw_encrypted).decode(),
            'Address':Keypair.from_raw_seed(passw).address().decode()}
    
    #Store the wallet Information
    with open('Stellar_wallet.json', 'w') as fp:
        json.dump(wallet_info, fp)
        
    print('Please disconnect your Trezor hardware wallet.')
    
    
def Get_data():  
    '''Get the wallet information'''
    try: 
        return json.load(open('Stellar_wallet.json', 'r'))
    except:
        path = input('Enter the path of your wallet file')
        return json.load(open(path, 'r'))
    
    

def Trezor_Access():
    '''Asking access to the Trezor wallet and generate the stellar keypair.'''
    
    devices = Wait_for_devices()
    transport = Choose_device(devices)
    client = TrezorClient(transport)
    
    data = Get_data()
    
    print('Please confirm action on your device.\n')
    passw = client.decrypt_keyvalue(data['bip32_path'],
                                    data['label'],
                                    binascii.unhexlify(data['password_encrypted_hex'].encode()),
                                    False, True)
    
    kp = Keypair.from_raw_seed(passw)
    return kp

#%%   Interacting with Stellar Network

def asset_Identifier(assetName, assetAdd):
    '''Distinguish lumen between other created assets.'''
    if assetName=='XLM':
        asset = Asset('XLM')
    else:
        asset = Asset(assetName,assetAdd)
    return asset

def passed_or_not(response):
    '''Show if the transaction has been successfully submitted.'''
    if '_links' in response:
        print('Transaction passed')
    else:
        print('Transaction failed')
        
def Account_balance_check():
    '''Check the balance in your account, you do not have to connect your Trezor to execute this.'''
    data = Get_data()
    
    Add = data['Address']
    
    add_info = Address(address = Add,network = 'public')
    add_info.get()
    return add_info.balances
        
    
    
def sending_lumen(desAdd,amount):
    '''Using trezor to send lumen. The required parameters are
    desAdd:string, the address of the lumen receiver.
    amount:float, the amount of lumens you want to send.
    msg:string, optional, the message you want to attach to the transaction.'''
    
    data = Get_data()
        
    sourceAdd = data['Address']
    asset = Asset('XLM')
    sequence = horizon.account(sourceAdd).get('sequence')
    op = Payment({'asset':asset,'amount':str(amount),'destination':desAdd})
    tx = Transaction(source=sourceAdd,opts={'sequence':sequence,'operations':[op]})
    envelope_send = Te(tx = tx,opts = {"network_id":"PUBLIC"})
    
    try: envelope_send.sign(Trezor_Access())
    except: raise Exception("Device is currently in use, try reconnect the device")
    
    xdr = envelope_send.xdr()
    xdr = xdr.decode()
    response = horizon.submit(xdr)
    passed_or_not(response)
    return response

def sending_asset(Asset_symbol,Asset_Issuer,desAdd,amount):
    '''Similar to sending_lumen except this function sends created assets.
    Asset_symbol: string, symbol of the asset, eg. 'BTC'
    Asset_Issuer: string, Address of the asset Issuer.
    desAdd:string, the address of the lumen receiver.
    amount:float, the amount of lumens you want to send.
    msg:string, optional, the message you want to attach to the transaction.'''
    data = Get_data()
    
    sourceAdd = data['Address']
    asset = asset_Identifier(Asset_symbol,Asset_Issuer)
    
    sequence = horizon.account(sourceAdd).get('sequence')
    op = Payment({'asset':asset,'amount':str(amount),'destination':desAdd})
    tx = Transaction(source=sourceAdd,opts={'sequence':sequence,'operations':[op]})
    envelope_send = Te(tx = tx,opts = {"network_id":"PUBLIC"})
    
    try: envelope_send.sign(Trezor_Access())
    except: raise Exception("Device is currently in use, try reconnect the device")
    
    xdr = envelope_send.xdr()
    xdr = xdr.decode()
    response = horizon.submit(xdr)
    passed_or_not(response)
    return response


def Trusting_asset(assetName,issuerAdd,limit):
    data = Get_data()
    
    sourceAdd = data['Address']
    asset = asset_Identifier(assetName,issuerAdd)
    
    sequence2 = horizon.account(sourceAdd).get('sequence')
    op_ct = ChangeTrust({'asset':asset, 'limit':str(limit)})
    tx_ct = Transaction(source=sourceAdd, opts = {'sequence':sequence2, 'operations':[op_ct,]})
    envelope_ct = Te(tx=tx_ct, opts={"network_id": "PUBLIC"})
    kp = Keypair.from_seed(Trezor_Access())
    envelope_ct.sign(kp)                 #sign
    xdr2 = envelope_ct.xdr()
    response=horizon.submit(xdr2)           #submit
    passed_or_not(response)
    return response


    
    

            
