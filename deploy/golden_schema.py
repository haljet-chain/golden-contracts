import json
from web3 import Web3
from utils import init, is_dev
from config import deployer_address

# Load initial data
with open('../contracts/GoldenSchemaPredicates.json') as f:
    initial_predicates = json.load(f)

with open('../contracts/GoldenSchemaEntityTypes.json') as f:
    initial_entity_types = json.load(f)

contract_name = 'GoldenSchema'

# Initialize network
network = init()

def deploy(w3: Web3):
    network_name = network.get('name')
    dev = is_dev(network_name)
    
    depl = deployer_address if not dev else w3.eth.default_account
    args = [initial_predicates, initial_entity_types] if dev else [[], []]
    
    # Load contract ABI and bytecode
    with open(f'../artifacts/{contract_name}.json') as f:
        contract_data = json.load(f)
        abi = contract_data['abi']
        bytecode = contract_data['bytecode']
    
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Deploy contract with OpenZeppelin Transparent Proxy pattern
    tx_hash = Contract.constructor().build_transaction({
        'from': depl,
        'gas': 5000000,
        'nonce': w3.eth.get_transaction_count(depl)
    })
    
    signed_txn = w3.eth.account.sign_transaction(tx_hash, private_key='YOUR_PRIVATE_KEY')
    tx_receipt = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_receipt)

    contract_address = tx_receipt.contractAddress
    print(f"{contract_name} deployed at: {contract_address}")
    
if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    deploy(w3)