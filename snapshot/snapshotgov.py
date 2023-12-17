from web3 import Web3
from snapshot import Snapshot
import dotenv
import os
import time

# Get the current Unix time
current_time = int(time.time())
current_block_number = 0  # Placeholder for the current block number

dotenv.load_dotenv()

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth_goerli'))

# Ensure connection to Ethereum node is successful
if not web3.is_connected():
    print("Failed to connect to the Ethereum Goerli node")
    exit()

# Get the current block number from the Goerli testnet
current_block_number = web3.eth.block_number

# Specify your Ethereum address
account = os.getenv("ETH_ADDRESS")

# Define proposal parameters
proposal_data = {
    'space': 'testdao1.eth',
    'type': 'single-choice',
    'name': 'Test proposal using Snapshot.py',
    'discussion': 'Test',
    'body': 'This is the content of the proposal',
    'choices': ['Alice', 'Bob', 'Carol'],
    'start': current_time,  # Set the start time to the current time
    'end': current_time + (1 * 60 * 60),  # End time is 1 hour after the start time
    'snapshot': current_block_number,  # Use the current block number as the snapshot value
    'network': '1',
    'plugins': '{}',
    'app': 'my-apptest'
}

print(proposal_data)

# Create a proposal
if current_block_number:
    hub_url = 'https://testnet.hub.snapshot.org/api/msg'
    snapshot = Snapshot(hub_url)
    receipt = snapshot.proposal(web3, account, proposal_data)

    # Print the receipt or perform other actions as needed
    print(receipt)
else:
    print("Failed to get the current block number")