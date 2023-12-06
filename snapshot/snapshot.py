from web3 import Web3
import requests
from datetime import datetime, timezone

w3 = Web3(Web3.HTTPProvider('blah blah'))

address = "WALLET_ADDRESS"

private_key = "PRIVATE_KEY"

snapshot_api_key = "SNAPSHOT_API_KEY"

project_name = "PROJECT_NAME"

#Construct the proposal
proposal_data = {
    "space": "space.eth",
    "type": "single-choice",
    "title": "test proposal using snapshot.py",
    "body": "This is the content of the proposal",
    "choices": ["Alice", "Bob", "Carol"],
    "start": #get current time,
    "end": #current time +48 hours,
    "snapshot": ,
    "network": "1",
    "plugins": "{}",
    "app": "project name"
}

#Sign the message with the private key

signature = w3.eth.account.sign_message(proposal_data, private_key=privatekey)

#Include the signature in the proposal data
proposal_data["sig"] = signature.signature.hex()

#Make a POST request to the Snapshot API
url = "https://hub.snapshot.org/api/message"
headers = {"Authorization": f"Bearer {snapshot_api_key}"}
response = requests.post(url, json=proposal_data, headers=headers)

print(response.json())