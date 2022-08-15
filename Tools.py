from web3 import Web3
from datetime import datetime
from crypto import HDPrivateKey, HDKey

import requests, json, getpass, time
import os, subprocess, threading, pause


# WALLET DATA OBJECT
class wallet_data:
    address = ''
    address_pk = ''
    def __init__(self, address, address_pk): 
        self.address = address
        self.address_pk = address_pk
# WALLET DATA OBJECT


# GLOBAL VARIABLES
bsc_network = 'https://bsc-dataseed1.binance.org'
biswap_token_address = '0x965F527D9159dCe6288a2219DB51fc6Eef120dD1'

biswap_hp_contract_address = '0xa4b20183039b2F9881621C3A03732fBF0bfdff10'
biswap_hp_abi_address = '0xa4b20183039b2F9881621C3A03732fBF0bfdff10'

snw_contract_address = '0xF28743d962AD110d1f4C4266e5E48E94FbD85285'
snw_abi_address = '0x98d9798511d60103834a8b117dd7f51b8f8cd0d6'
# GLOBAL VARIABLES


# MAIN FUNCTIONS
def clear_history():
    if(os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')


def get_abi(abi_address):
    api_bsc = 'https://api.bscscan.com/api'
    API_ENDPOINT = api_bsc + '?module=contract&action=getabi&address=' + str(abi_address)
    response = (requests.get(url = API_ENDPOINT)).json()

    abi_data = json.loads(response['result'])
    return abi_data


def get_wallets():
    mnemonic = getpass.getpass('Please, Enter your Mnemonic: ')
    wallet_amounts = int(input('Please, Enter count of Wallets: '))
    wallets_array = generate_wallets(wallet_amounts, mnemonic)

    return wallets_array


def get_time():
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    return current_time


def generate_wallets(amount, mnemonic):
    master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)
    root_keys = HDKey.from_path(master_key,"m/44'/60'/0'")
    acct_priv_key = root_keys[-1]
    wallets = []

    for i in range(amount):
        keys = HDKey.from_path(acct_priv_key,'{change}/{index}'.format(change=0, index=i))
        private_key = keys[-1]

        address = private_key.public_key.address()
        address_pk = '0x' + private_key._key.to_hex()

        wallet_object = wallet_data(address, address_pk)
        wallets.append(wallet_object)
    return wallets


def get_balance(contract_address, wallet_address, private_key, abi_data):
    web3 = Web3(Web3.HTTPProvider(bsc_network))

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)
    contracts_response = contract.functions.balanceOf(wallet_address).call()

    return contracts_response


def approve(token, contract_address, wallet_address, private_key, abi_data):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    print(wallet_address + ' - Connection: ' + str(web3.isConnected()))

    token = web3.toChecksumAddress(token)
    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=token, abi=abi_data)

    max_amount = web3.toWei(2**64-1, 'ether')
    nonce = web3.eth.getTransactionCount(wallet_address)

    approve_tx = contract.functions.approve(contract_address, max_amount).buildTransaction({
        'chainId': 56,
        'from': wallet_address, 
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })
    
    sign_tx = web3.eth.account.signTransaction(approve_tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
    print(wallet_address + ' - Approve tx is sent! Awaiting Response!')

    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(wallet_address + ' - Approve tx Done!')


def deposit_HP(contract_address, deposit_size, wallet_address, private_key, abi_data):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    print(wallet_address + ' - Connection: ' + str(web3.isConnected()))

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)

    value = web3.toWei(0, 'ether')
    nonce = web3.eth.get_transaction_count(wallet_address)
    deposit_uint256 = web3.toWei(str(deposit_size),'ether')
    
    contracts_tx = contract.functions.deposit(deposit_uint256).buildTransaction({
        'chainId': 56,
        'from': wallet_address,
        'value': value,
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })

    print(wallet_address + ' - Deposit tx is ready! - ' + get_time())
    print(wallet_address + ' - Awaiting time!')

    sign_tx = web3.eth.account.sign_transaction(contracts_tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(sign_tx.rawTransaction)
    print(wallet_address + ' - Deposit tx sent! - ' + get_time())

    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(wallet_address + ' - Deposit tx Done! - ' + get_time())


def withdraw_from_HP(contract_address, wallet_address, private_key, abi_data):
    web3 = Web3(Web3.HTTPProvider(bsc_network))

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    nonce = web3.eth.getTransactionCount(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)
    
    approve_tx = contract.functions.withdrawAll().buildTransaction({
        'chainId': 56,
        'from': wallet_address, 
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })

    sign_tx = web3.eth.account.signTransaction(approve_tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
    print(wallet_address + ' - Withdraw tx is sent! Awaiting!')

    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(wallet_address + ' - Withdraw tx is Done!')


def collect_tokens(contract_address, wallet_address, private_key, recipient_wallet, abi_data):
    web3 = Web3(Web3.HTTPProvider(bsc_network))

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    recipient_wallet = web3.toChecksumAddress(recipient_wallet)
    nonce = web3.eth.getTransactionCount(wallet_address)

    contract = web3.eth.contract(address=contract_address, abi=abi_data)
    available_tokens = contract.functions.balanceOf(wallet_address).call()
    
    approve_tx = contract.functions.transfer(recipient_wallet, available_tokens).buildTransaction({
        'chainId': 56,
        'from': wallet_address, 
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })

    sign_tx = web3.eth.account.signTransaction(approve_tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
    print(wallet_address + ' - Token tx is sent! Awaiting!')

    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(wallet_address + ' - Token tx is Done!')
# MAIN FUNCTIONS


# MAIN MENU
def approve_HP_option(wallets_array):
    abi_data_bsw = get_abi(biswap_token_address)
    for wallet_string in wallets_array:
        approve(biswap_token_address, biswap_hp_contract_address, wallet_string.address, wallet_string.address_pk, abi_data_bsw)
    print('Everything is Done!\n')


def approve_SNW_option(wallets_array):
    abi_data_bsw = get_abi(biswap_token_address)
    for wallet_string in wallets_array:
        approve(biswap_token_address, snw_contract_address, wallet_string.address, wallet_string.address_pk, abi_data_bsw)
    print('Everything is Done!\n')


def deposit_to_HP_option(wallets_array):
    abi_data_hp = get_abi(biswap_hp_abi_address)
    deposit_size = input('Please, Enter Deposit Size (10): ')
    if deposit_size == '':
        deposit_size = '10'
    for wallet_string in wallets_array:
        deposit_HP(biswap_hp_contract_address, deposit_size, wallet_string.address, wallet_string.address_pk, abi_data_hp)
    print('Everything is Done!\n')


def withdraw_from_HP_option(wallets_array):
    abi_data_hp = get_abi(biswap_hp_abi_address)
    for wallet_string in wallets_array:
        withdraw_from_HP(biswap_hp_contract_address, wallet_string.address, wallet_string.address_pk, abi_data_hp)
    print('Everything is Done!\n')


def show_balances_option(wallets_array):
    abi_data_bsw = get_abi(biswap_token_address)
    wallet_count = 0
    for wallet_string in wallets_array:
        wallet_count += 1
        response = get_balance(biswap_token_address, wallet_string.address, wallet_string.address_pk, abi_data_bsw)
        print(str(wallet_count) + '. ' + wallet_string.address + ' - ' + str(response))
    print('Everything is Done!\n')


def collecting_tokens_option(wallets_array):
    recipient_wallet = input('Please, Enter your Main Wallet to Receive tokens: \n')
    print('This is your Main Wallet: ' + recipient_wallet)
    user_option = input('Do you want to Continue with this wallet? (y/n): ')
    if user_option != 'y':
        return

    abi_data_bsw = get_abi(biswap_token_address)
    for wallet_string in wallets_array:
        collect_tokens(biswap_token_address, wallet_string.address, wallet_string.address_pk, recipient_wallet, abi_data_bsw)
    print('Everything is Done!\n')


def main_menu(wallets_array):
    if wallets_array == []:
        wallets_array = get_wallets()

    print('Enter number of your Option:')
    print('1. Approve HP!')
    print('2. Approve SNW!')
    print('3. Deposit to HP!')
    print('4. Withdraw from HP!')
    print('5. Show wallets Balances!')
    print('6. Collecting BSW Tokens!')
    print('7. Use Another Mnemonic!')
    print('8. Exit from Application!')
    user_option = input()
    clear_history()

    if user_option == '1':
        approve_HP_option(wallets_array)

    if user_option == '2':
        approve_SNW_option(wallets_array)

    if user_option == '3':
        deposit_to_HP_option(wallets_array)

    if user_option == '4':
        withdraw_from_HP_option(wallets_array)
    
    if user_option == '5':
        show_balances_option(wallets_array)

    if user_option == '6':
        collecting_tokens_option(wallets_array)

    if user_option == '7':
        wallets_array = get_wallets()

    if user_option == '8':
        exit()

    main_menu(wallets_array)
    return
# MAIN MENU


def main():
    main_menu([])


if __name__ == '__main__':
    main()



