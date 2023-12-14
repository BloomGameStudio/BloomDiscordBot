from web3 import Web3
from snapshot import Snapshot
import dotenv
import os

dotenv.load_dotenv()

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider('https://ethereum-goerli.publicnode.com'))

# Ensure connection to Ethereum node is successful
if not web3.is_connected():
    print("Failed to connect to Ethereum goerli node")
    exit()

# Specify the hub URL for the testnet
hub_url = 'https://testnet.hub.snapshot.org/api/msg'
snapshot = Snapshot(hub_url)

# Specify your Ethereum address
account = os.getenv("ETH_ADDRESS")

# Define proposal parameters
proposal_data = {
    'space': 'testdao1.eth',
    'type': 'single-choice',
    'title': 'Test proposal using Snapshot.py',
    'body': 'This is the content of the proposal',
    'choices': ['Alice', 'Bob', 'Carol'],
    'start': 1636984800,
    'end': 1637244000,
    'snapshot': 13620822,
    'network': '1',
    'plugins': '{}',
    'app': 'my-apptest'
}

# Create a proposal
receipt = snapshot.proposal(web3, account, proposal_data)

# Print the receipt or perform other actions as needed
print(receipt)
