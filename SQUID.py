from web3 import Web3
from datetime import datetime

import json, requests
import time, pause, getpass
import os, sys, threading


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

snw_game_contract_address = '0xccc78df56470b70cb901fcc324a8fbbe8ab5304b'
snw_game_contract_abi_address = '0x721a650b65efeed95616f504395a4c63f6a785e9'

players_contract_address = '0xb00ED7E3671Af2675c551a1C26Ffdcc5b425359b'
players_contract_abi_address = '0xe9f688c064ae0f0668baf0558352075b83a1c4f1'

contract_version = 2 # Version 1 is ENDED!
# GLOBAL VARIABLES


# WINDOWS FUNCTIONS (CTRL+C to Exit)
def handler(a,b=None):
    sys.exit(1)

def install_handler():
    if sys.platform == "win32":
        import win32api
        win32api.SetConsoleCtrlHandler(handler, True)
# WINDOWS FUNCTIONS (CTRL+C to Exit)


# COMMON FUNCTIONS
def get_time():
	now = datetime.now()
	current_time = now.strftime('%H:%M:%S')
	return current_time


def clear_history():
    if(os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')


def get_abi(abi):
	api_bsc = 'https://api.bscscan.com/api'
	API_ENDPOINT = api_bsc + '?module=contract&action=getabi&address=' + str(abi)
	response = (requests.get(url = API_ENDPOINT)).json()

	abi_data = json.loads(response['result'])
	return abi_data


def get_abi_data():
	print('Receiving ABI Data of contracts, Please wait!')
	abi_player_data = get_abi(players_contract_abi_address)
	time.sleep(5)
	abi_game_data = get_abi(snw_game_contract_abi_address)

	return abi_game_data, abi_player_data


def get_run_time():
    time_string = input('Please, Enter Date to Buy (01-01-2000 00:00:00): ')
    if time_string == '0' or time_string == '':
        time_string = '01-01-2025 00:00:00'

    if time_string == '1':
        time_string = '01-01-2000 00:00:00' 

    date_time = datetime.strptime(time_string,"%d-%m-%Y %H:%M:%S")

    return date_time


def generate_wallets(amount, mnemonic):
    web3 = Web3()
    web3.eth.account.enable_unaudited_hdwallet_features()
    wallets = []
    
    for i in range(amount):
        account = web3.eth.account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{i}")
        address = account.address
        address_pk = Web3.toHex(account.key)

        wallet_object = wallet_data(address, address_pk)
        wallets.append(wallet_object)
    return wallets
# COMMON FUNCTIONS


# GAME FUNCTIONS
def get_game_id(se):
	se_int = int(se / 1000000000000000000000)
	if se_int > 7:
		se_int = 7
	return se_int - 1


def get_user_se(wallet_address, abi_data):
	web3 = Web3(Web3.HTTPProvider(bsc_network))
	contract_address = web3.toChecksumAddress(players_contract_address)
	wallet_address = web3.toChecksumAddress(wallet_address)
	contract = web3.eth.contract(address=contract_address, abi=abi_data)

	user_se = contract.functions.availableSEAmountV2(wallet_address).call()
	user_se_max = contract.functions.totalSEAmount(wallet_address).call()

	return user_se, user_se_max


def get_user_players(wallet_address, abi_data):
	user_players = []

	web3 = Web3(Web3.HTTPProvider(bsc_network))
	contract_address = web3.toChecksumAddress(players_contract_address)
	wallet_address = web3.toChecksumAddress(wallet_address)
	contract = web3.eth.contract(address=contract_address, abi=abi_data)

	contract_response = contract.functions.arrayUserPlayers(wallet_address).call()
	
	for player_info in contract_response:
		user_players.append(player_info[0])

	return user_players


def play_game(wallet_address, private_key, players_id, abi_data, game_index):
	print(wallet_address + ' - Creating Transaction! - ' + get_time())
	web3 = Web3(Web3.HTTPProvider(bsc_network))
	wallet_address = web3.toChecksumAddress(wallet_address)

	contract_address = web3.toChecksumAddress(snw_game_contract_address)
	contract = web3.eth.contract(address=contract_address, abi=abi_data)

	value = web3.toWei(0, 'ether')
	nonce = web3.eth.get_transaction_count(wallet_address)

	contracts_tx = contract.functions.playGame(game_index, players_id, contract_version).buildTransaction({
		'chainId': 56,
		'from': wallet_address,
		'value': value,
		'gas': 1000000,
		'gasPrice': web3.toWei('5','gwei'), 
		'nonce': nonce
    })

	sign_txn = web3.eth.account.sign_transaction(contracts_tx, private_key)
	print(wallet_address + ' - Sending Transaction! - ' + get_time())
	txn_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)

	web3.eth.wait_for_transaction_receipt(txn_hash)
	print(wallet_address + ' - Transaction is Done! - ' + get_time())


def run_game_cycle(wallets_array, abi_player_data, abi_game_data, sleep_time):
	for wallet_string in wallets_array:
		user_se, user_se_max = get_user_se(wallet_string.address, abi_player_data)
		if user_se != 0:
			if user_se == user_se_max:
				game_index = get_game_id(user_se_max)
				if game_index >= 0:
					print(wallet_string.address + ' - Game is Available! - ' + get_time())
					user_players = get_user_players(wallet_string.address, abi_player_data)
					play_game(wallet_string.address, wallet_string.address_pk, user_players, abi_game_data, game_index)
					print(wallet_string.address + ' - PlayGame is Done! - ' + get_time())
				else:
					print(wallet_string.address + ' - No Available any SE! - ' + get_time())
			else:
				print(wallet_string.address + ' - SE Recovering! - ' + get_time())
		else:
			print(wallet_string.address + ' - SE Recovering! - ' + get_time())
		time.sleep(sleep_time)
	run_game_cycle(wallets_array, abi_player_data, abi_game_data, sleep_time)
# GAME FUNCTIONS


# NEW CONTRACTS FUNCTION
def get_new_contracts(abi_data, wallet_address, private_key, players, date_time):
	web3 = Web3(Web3.HTTPProvider(bsc_network))

	contract_address = web3.toChecksumAddress(snw_game_contract_address)
	wallet_address = web3.toChecksumAddress(wallet_address)
	contract = web3.eth.contract(address=contract_address, abi=abi_data)

	value = web3.toWei(0, 'ether')
	nonce = web3.eth.get_transaction_count(wallet_address)

	contracts_tx = contract.functions.buyContractsV2(players, 1).buildTransaction({
		'chainId': 56,
		'from': wallet_address,
		'value': value,
		'gas': 1000000,
		'gasPrice': web3.toWei('10','gwei'), 
		'nonce': nonce
    })

	print(wallet_address + ' - To Buy tx is ready! - ' + get_time())
	print(wallet_address + ' - Awaiting time to Buy!')

	pause.until(date_time)

	sign_txn = web3.eth.account.sign_transaction(contracts_tx, private_key)
	txn_hash = web3.eth.send_raw_transaction(sign_txn.rawTransaction)
	print(wallet_address + ' - To Buy tx is sent! - ' + get_time())

	web3.eth.wait_for_transaction_receipt(txn_hash)
	print(wallet_address + ' - Buy is Done! - ' + get_time())
# NEW CONTRACTS FUNCTION


def main():
	install_handler()

	print('Please, Choose your Option (1-3): ')
	print('1. Buy new Contracts for Players!')
	print('2. Run Play Game cycle!')
	print('3. Exit from Application!')
	user_option = input()

	if user_option == '3':
		exit()
	clear_history()

	abi_game_data, abi_player_data = get_abi_data()

	mnemonic = getpass.getpass('Please, Enter your Mnemonic: ')

	if user_option == '2':
		sleep_time = int(input('Please, Enter checking delay for wallets (seconds): '))

	wallet_amounts = int(input('Please, Enter amount of wallets: '))
	wallets_array = generate_wallets(wallet_amounts, mnemonic)

	if user_option == '2':
		game_threads = threading.Thread(target=run_game_cycle, args=(wallets_array, abi_player_data, abi_game_data, sleep_time,))
		game_threads.start()
	elif user_option == '1':
		date_time = get_run_time()
		for wallet_info in wallets_array:
			user_players = get_user_players(wallet_info.address, abi_player_data)
			new_threads = threading.Thread(target=get_new_contracts, 
				args=(abi_game_data, wallet_info.address, wallet_info.address_pk, user_players, date_time,))
			new_threads.start()


if __name__ == '__main__':
	main()


