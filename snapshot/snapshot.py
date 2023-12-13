from web3 import Web3
from snapshot import Snapshot
import dotenv
import os

dotenv.load_dotenv()

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider('https://ethereum-goerli.publicnode.com'))

# Ensure connection to Ethereum node is successful
if not web3.isConnected():
    print("Failed to connect to Ethereum goerli node")
    exit()

# Specify your Ethereum address
account = os.getenv("ETH_ADDRESS")

# Create a Snapshot instance
snapshot = Snapshot()

# Define proposal parameters
proposal_data = {
    'space': 'myENS.eth',
    'type': 'single-choice',
    'title': 'Test proposal using Snapshot.py',
    'body': 'This is the content of the proposal',
    'choices': ['Alice', 'Bob', 'Carol'],
    'start': 1636984800,
    'end': 1637244000,
    'snapshot': 13620822,
    'network': '1',
    'plugins': '{}',
    'app': 'my-app'
}

# Create a proposal
receipt = snapshot.proposal(web3, account, proposal_data)

# Print the receipt or perform other actions as needed
print(receipt)
