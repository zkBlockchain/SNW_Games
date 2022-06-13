from web3 import Web3
from datetime import datetime
from crypto import HDPrivateKey, HDKey

import requests, json, getpass
import os, subprocess, threading, pause

# WALLET DATA OBJECT
class wallet_data:
    address = ''
    address_pk = ''
    def __init__(self, address, address_pk): 
        self.address = address
        self.address_pk = address_pk
# WALLET DATA OBJECT

# GLOBAL
bsc_network = 'https://bsc-dataseed1.binance.org'
biswap_token_address = '0x965F527D9159dCe6288a2219DB51fc6Eef120dD1'

biswap_hp_contract_address = '0xa4b20183039b2F9881621C3A03732fBF0bfdff10'
biswap_hp_abi_address = '0xa4b20183039b2F9881621C3A03732fBF0bfdff10'

snw_contract_address = '0xF28743d962AD110d1f4C4266e5E48E94FbD85285'
snw_abi_address = '0x98d9798511d60103834a8b117dd7f51b8f8cd0d6'

summary_info = 0
summary_claim = 0

line = '------------------------------------------------------------'
# GLOBAL

# COMMON FUNCTIONS
def get_abi(abi_address):
    api_bsc = 'https://api.bscscan.com/api'
    API_ENDPOINT = api_bsc + '?module=contract&action=getabi&address=' + str(abi_address)
    response = (requests.get(url = API_ENDPOINT)).json()

    abi_data = json.loads(response['result'])
    return abi_data

def get_time():
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    return current_time

def clear_history():
    if(os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')

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
# COMMON FUNCTIONS

# STATISTIC FUNCTIONS
def statistic_option(abi_data, wallets_array, is_details):
    index, total_available, total_claimable = 1, 0, 0
    if is_details:
        print(line)

    for wallet_string in wallets_array:
        available, claimable = workers_statistic(index, wallet_string.address, snw_contract_address, abi_data, wallet_string.address_pk, is_details)
        total_available += available
        total_claimable += claimable
        index += 1

    print('\nSummary Available: ' + str(total_available))
    print('Summary Claimable: ' + str(total_claimable) + '\n')

def check_player(players_array):
    if players_array[0] == 0 and players_array[1] == 0:
        return True
    else:
        return False

def get_worker_details(worker_info):
    total_time = (worker_info[1] - worker_info[0]) / 60 / 60 / 24
    year_apr = worker_info[3]
    period_roi = worker_info[4]
    current_earn = round(worker_info[5] / 1000000000000000000, 2)
    total_earn = (25 / 100 * period_roi)
    remaining_days = round((1 - (current_earn / total_earn)) * total_time, 2)


    results_days = 'Remaining Days: ' + str(remaining_days) + '\n'
    results_ROI = 'ROI: ' + str(period_roi) + '% per ' + str(total_time) + ' Days' + '\n'
    results_earns = 'Earnings: ' + str(current_earn) + '/' + str(total_earn) + ' BSW' + '\n'
    results_APR = 'APR: ' + str(year_apr) + '%' + '\n'
    
    results = results_days + results_ROI + results_earns + results_APR

    return results

def get_detailed_stats(index, wallet_address, users_array):
    available, claimable = 0, 0

    if len(users_array) == 2:
        print(str(index) + '. ' + wallet_address + ' - Statistics!\n')
        for i in range(2):
            if check_player(users_array[i]):
                claimable += 1
            worker_info = users_array[i]
            print('Player ' + str(i + 1) + ' Info: ')
            print(get_worker_details(worker_info))
        print('To Buy: 0 & To Claim: ' + str(claimable))
        print(line)
    elif len(users_array) == 1:
        print(str(index) + '. ' + wallet_address + ' - Statistics!\n')
        worker_info = users_array[0]
        print('Player 1 Info: ')
        print(get_worker_details(worker_info))
        if check_player(users_array[0]):
            print('To Buy: 1 & To Claim: 1')
            claimable, available = 1, 1
        else:
            print('To Buy: 1 & To Claim: 0')
            available = 1
        print(line)
    elif len(users_array) == 0:
        print(str(index) + '. ' + wallet_address + ' - Statistics!\n')
        print('To Buy: 2 & To Claim: 0')
        available = 2
        print(line)
    else:
        print(str(index) + '. ' + ' - Something was wrong!')
        print(line)
    return available, claimable

def get_custom_stats(index, wallet_address, users_array):
    available, claimable = 0, 0

    if len(users_array) == 2:
        for i in range(2):
            if check_player(users_array[i]):
                claimable += 1
        print(str(index) + '. ' + wallet_address + ' - To Buy: 0 & To Claim: ' + str(claimable))
    elif len(users_array) == 1:
        if check_player(users_array[0]):
            print(str(index) + '. ' + wallet_address + ' - To Buy: 1 & To Claim: 1')
            claimable, available = 1, 1
        else:
            print(str(index) + '. ' + wallet_address + ' - To Buy: 1 & To Claim: 0')
            available = 1
    elif len(users_array) == 0:
        print(str(index) + '. ' + wallet_address + ' - To Buy: 2 & To Claim: 0')
        available = 2
    else:
        print(str(index) + '. ' + ' - Something was wrong!')

    return available, claimable

def workers_statistic(index, wallet_address, contract_address, abi_data, private_key, is_details):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    available, claimable = 0, 0

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)

    contracts_response = contract.functions.getUserInfo(wallet_address).call()
    users_array = contracts_response[0][9]
    players_count = len(users_array)

    if is_details:
        available, claimable = get_detailed_stats(index, wallet_address, users_array)
    else:
        available, claimable = get_custom_stats(index, wallet_address, users_array)

    return available, claimable
# STATISTIC FUNCTIONS

# CLAIM FUNCTIONS
def is_claim_worker(players_array):
    if players_array[0] == 0 and players_array[1] == 0:
        return True
    else:
        return False

def claims_queue(wallet_address, contract_address, abi_data, players, private_key, claim_player_id):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    wallet_address = web3.toChecksumAddress(wallet_address)
    nonce = web3.eth.get_transaction_count(wallet_address)

    for i in range(players + 1):
        if players == 1:
            tx_claim_workers(wallet_address, contract_address, abi_data, i, private_key, nonce)
        elif players == 0:
            tx_claim_workers(wallet_address, contract_address, abi_data, claim_player_id, private_key, nonce)
        nonce += 1

def tx_claim_workers(wallet_address, contract_address, abi_data, player_id, private_key, nonce):
    print(wallet_address + ' - Claiming Player (' + str(player_id) + ')!')

    web3 = Web3(Web3.HTTPProvider(bsc_network))
    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)

    value = web3.toWei(0, 'ether')

    contracts_response = contract.functions.claimWorker(player_id).buildTransaction({
        'chainId': 56,
        'from': wallet_address,
        'value': value,
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })

    print(wallet_address + ' - Claiming tx is ready! - ' + get_time())
    sign_txn = web3.eth.account.sign_transaction(contracts_response, private_key)
    txn_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)
    print(wallet_address + ' - Claiming tx is sent! - ' + get_time())

    web3.eth.wait_for_transaction_receipt(txn_hash)
    print(wallet_address + ' - Claiming is Done! - ' + get_time())
# CLAIM FUNCTIONS

# HIRE FUNCTIONS
def get_run_time(option):
    if option == False:
        time_string = input('Please, Enter Date to Run Hiring (01-01-2000 00:00:00): ')
        if time_string == '0' or time_string == '':
            time_string = '01-01-2025 00:00:00'

        if time_string == '1':
            time_string = '01-01-2000 00:00:00' 

        date_time = datetime.strptime(time_string,"%d-%m-%Y %H:%M:%S")

        return date_time

def workers_queue(wallet_address, contract_address, abi_data, private_key, date_time, workers):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    wallet_address = web3.toChecksumAddress(wallet_address)
    nonce = web3.eth.get_transaction_count(wallet_address)

    for i in range(workers):
        tx_new_worker(wallet_address, contract_address, abi_data, private_key, date_time, nonce)
        nonce += 1

def tx_new_worker(wallet_address, contract_address, abi_data, private_key, date_time, nonce):
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)

    value = web3.toWei(0, 'ether')

    contracts_response = contract.functions.hireWorker().buildTransaction({
        'chainId': 56,
        'from': wallet_address,
        'value': value,
        'gas': 1000000,
        'gasPrice': web3.toWei('5','gwei'), 
        'nonce': nonce
    })

    print(wallet_address + ' - Hiring tx is ready! - ' + get_time())
    print(wallet_address + ' - Hiring - Awaiting Time!')

    pause.until(date_time)

    sign_txn = web3.eth.account.sign_transaction(contracts_response, private_key)
    txn_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)
    print(wallet_address + ' - Hiring tx is sent! - ' + get_time())

    web3.eth.wait_for_transaction_receipt(txn_hash)
    print(wallet_address + ' - Hiring is Done! - ' + get_time())

def new_worker_threads(wallet_address, contract_address, abi_data, private_key, date_time, workers):
    new_threads = threading.Thread(target=workers_queue, args=(wallet_address, contract_address, abi_data, private_key, date_time, workers,))
    new_threads.start()
# HIRE FUNCTIONS

# MAIN COMMON FUNCTIONS
def run_workers_queue(wallet_address, contract_address, abi_data, private_key, date_time, option):
    global summary_info
    global summary_claim
    web3 = Web3(Web3.HTTPProvider(bsc_network))
    #print(wallet_address + ' - Checking Connection: ' + str(web3.isConnected()))

    contract_address = web3.toChecksumAddress(contract_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    contract = web3.eth.contract(address=contract_address, abi=abi_data)
    contracts_response = contract.functions.getUserInfo(wallet_address).call()
    workers_count = len(contracts_response[0][9])
    workers = 0

    if workers_count == 2:
        if option:
            print(wallet_address + ' - 2 Players! Checking Claims!')
            claim_counter = -1
            claim_player_id = 0
            for i in range(2):
                if is_claim_worker(contracts_response[0][9][i]):
                    claim_counter += 1
                    summary_claim += 1
                    claim_player_id = i

            if claim_counter > -1:
                claims_queue(wallet_address, contract_address, abi_data, claim_counter, private_key, claim_player_id)
            else:
                print(wallet_address + ' - Nothing to Claim (0)!')
                print(wallet_address + ' - Nothing to Claim (1)!')
        else:
            print(wallet_address + ' - 2 Players! Nothing to Buy!')
    elif workers_count == 1:
        if option:
            print(wallet_address + ' - 1 Player! Checking 1!')
            if is_claim_worker(contracts_response[0][9][0]):
                claims_queue(wallet_address, contract_address, abi_data, 0, private_key)
                summary_claim += 1
            else:
                print(wallet_address + ' - Nothing to Claim (0)!')
        else:
            summary_info += 1
            workers += 1
            print(wallet_address + ' - 1 Player! Buy 1!') # Check 1 player => buy 1 or 2 contracts!
            new_worker_threads(wallet_address, contract_address, abi_data, private_key, date_time, workers)
    elif workers_count == 0:
        if option:
            print(wallet_address + ' - 0 Players! Nothing to Claim!')
        else:  
            print(wallet_address + ' - 0 Players! Buy 2 Players!')
            workers += 2
            summary_info += 2

            new_worker_threads(wallet_address, contract_address, abi_data, private_key, date_time, workers)
    else:
        print('Something Wrong!')

def main_menu(abi_data, wallets):
    print('Please, Choose your Option (1-4): ')
    print('1. Checking workers Statistic!')
    print('2. Claiming Available Workers!')
    print('3. Hiring New Players!')
    print('4. Exit from Application!')
    user_option = input()
    clear_history()

    # Option 1
    if user_option == '1':
        print('Please, Choose statistic Option (1-3): ')
        print('1. Statistic with Details!')
        print('2. Statistic without Details!')
        print('3. Go to Main Menu!')
        user_stat_option = input()
        clear_history()
        if user_stat_option == '1':
            statistic_option(abi_data, wallets, True)
        elif user_stat_option == '2':
            statistic_option(abi_data, wallets, False)
        main_menu(abi_data, wallets)
        return
    # Option 1

    # Option 2
    option = True # False - Hair, True - Claim
    # Option 2

    # Option 3
    if user_option == '3':
        option = False
    date_time = get_run_time(option)
    # Option 3

    # Option 4
    if user_option == '4':
        exit()
    # Option 4

    # Back if wrong option!
    if user_option != '2' and option == True:
        main_menu(abi_data, wallets)
        return
    # Back if wrong option!

    # Run Claim/Hire option
    for wallet_string in wallets:
        run_workers_queue(wallet_string.address, snw_contract_address, abi_data, wallet_string.address_pk, date_time, option)
    # Run Claim/Hire option

    # Results
    if option:
        print('\nClaiming Statistic: ' + str(summary_claim) + '\n')
        main_menu(abi_data, wallets)
    else:
        print('\nSummary to Buy: ' + str(summary_info) + '\n')
# MAIN COMMON FUNCTIONS

def main():
    global summary_info
    global summary_claim
    summary_info = 0
    summary_claim = 0

    abi_data = get_abi(snw_abi_address)

    mnemonic = getpass.getpass('Please, Enter your Mnemonic: ')
    wallet_amounts = int(input('Please, Enter count of Wallets: '))
    wallets = generate_wallets(wallet_amounts, mnemonic)

    main_menu(abi_data, wallets)

if __name__ == '__main__':
    main()


