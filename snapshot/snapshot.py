import os
import time
import json
import requests
from web3 import Web3
from eth_account.messages import encode_defunct

# Load environment variables
eth_address = os.getenv('ETH_ADDRESS')
eth_private_key = os.getenv('ETH_PRIVATE_KEY')

if not eth_address or not eth_private_key:
    raise ValueError('Ethereum address or private key not provided in environment variables')

# Initialize Web3
w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth_goerli'))  # Replace with your RPC endpoint

# Define proposal parameters
current_time = int(time.time())  # Current time in seconds
one_hour_in_seconds = 3600

proposal_params = {
    'space': 'testdao1.eth',
    'type': 'single-choice',  # define the voting system
    'title': 'Test proposal using Python',
    'body': 'This is the content of the proposal',
    'choices': ['Alice', 'Bob', 'Carol'],
    'start': current_time,
    'end': current_time + one_hour_in_seconds,  # End time is one hour later as an example
    'snapshot': w3.eth.block_number,  # Current block number as snapshot
    'network': '1',
    'plugins': json.dumps({}),
    'app': 'my-app'  # provide the name of your project using this Snapshot.js integration
}

# Sign the proposal
message = encode_defunct(text=json.dumps(proposal_params))
signed_message = w3.eth.account.sign_message(message, private_key=eth_private_key)

# Submit the proposal
url = 'https://testnet.hub.snapshot.org/api/message'
headers = {'Content-Type': 'application/json'}
data = {
    'address': eth_address,
    'msg': signed_message.messageHash.hex(),  # Use the hash of the original message
    'sig': signed_message.signature.hex(),
    'version': '2'
}
response = requests.post(url, headers=headers, data=json.dumps(data))

# Log the response details
if response.status_code == 200:
    print('Proposal submitted. Response:', response.json())
else:
    print('Error creating proposal:', response.text)