from web3 import Web3
from typing import Any, Dict
import requests

class Snapshot:
    def __init__(self, hub_url: str):
        self.hub_url = hub_url

    def proposal(self, web3: Web3, account: str, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Construct the payload
        payload = {
            'address': account,
            'msg': proposal_data
        }

        # Print the payload for debugging
        print("Payload:", payload)

        # Make an HTTP POST request to the Snapshot API
        response = requests.post(f'{self.hub_url}', json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            receipt = response.json()
            return receipt
        else:
            # Handle the case when the request fails
            print(f'Failed to create proposal: {response.status_code} - {response.text}')
            return {'status': 'failed'}