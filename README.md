# Trezor-Stellar-Integration
This repository contain codes that help Trezor user to encrypt and sign Stellar operations.

## Introduction

Most current Stellar wallet providers require user to enter their private key or to submit a key file before signing transctions. This requires the user to store their private key somewhere on their computing device in order to use the wallet easily. Leaving important data on your own device can be risky and the best practice is to store you key information on an offline device such as hardware wallets or paper wallets.

In Bitcoin eco-system and there are many manufacturers providing bitcoin hardware wallet service. Since Ethereum and many other popular cryptocurrencies share the same private key format as bitcoin, wallet such as Ledger and Trezor also support storing of Litecoin, Ether, ERC20 tokens etc.

However, currently these wallet users cannot use their wallet to store lumen and another asset on Stellar Network. By using python scripts included in this repository, the user is able to turn his or her Trezor into a secure Stellar hardware wallet too.

## Ideology

We use trezor to encrypt a urandom(32) bytes and use that to generate a Stellar keypair. With the generated Stellar keypair the user will be able to sign all kinds of transaction.

## Usage
Preparation: This is NOT a stand alone repository and few libraries need to implemented.
```
pip install Trezor
pip install Stellar-base
```
Step1: Run the script `Trezor_lumen.py`. This script currently connect to the public network. If the user wants to test things out in testnet please change the variable `horizon` to `horizon = 'https://horizon-testnet.stellar.org'`.   
Step2: Execute `Create_wallet_file()` function to create a wallet information file where the label, Bip32 info, encrypted password and account address are saved.   
Step3: Fund the address with at least 20 XLM.     
Step4: Disconnect and reconnect your trezor and this time you can execute `sending_lumen(desAdd,amount,msg)` to make a transaction.   

## Future plan
This is not the final version of this project. In coming days I will add all the operations here. Wallet providers are welcome to integrate this into your backend so that you can support Trezor as well. Feedbacks are more than welcome. Thanks.
