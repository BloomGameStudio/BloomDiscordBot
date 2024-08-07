import snapshot from '@snapshot-labs/snapshot.js';
import { ethers } from 'ethers';

// Private Key
const privateKey = '0x4d9be11f';

// Set up ethers provider
const provider = new ethers.JsonRpcProvider('https://rpc2.sepolia.org');

// Create a wallet instance
const wallet = new ethers.Wallet(privateKey, provider);

// Override the signTypedData method for compatibility with Snapshot.js
wallet._signTypedData = async (domain, types, value) => {
  return wallet.signTypedData(domain, types, value);
};

// Initialize Snapshot client
const hub = 'https://testnet.hub.snapshot.org'; // or a different hub if needed
const client = new snapshot.Client712(hub);

// Function to modify space settings
async function modifySpace() {
  try {
    const account = await wallet.getAddress();
    console.log('Using account:', account); // Log the account being used

    // Construct settings object based on the provided schema and example
    const settings = {
      name: "Testnet",
      about: "test",
      network: "11155111",
      symbol: "LINK",
      private: false,
      admins: [],
      moderators: [],
      members: ["0x5b3eadc33df96e51ba69907112f32ea863870fd4"],
      categories: [],
      plugins: {},
      children: [],
      voting: {
        quorum: 5000,
        hideAbstain: false
      },
      strategies: [{
        name: "erc20-balance-of",
        network: "11155111",
        params: {
          symbol: "GLD",
          address: "0x84219229E96bB404c932f55833044dc2785B7c0c",
          decimals: 18
        }
      }],
      validation: {
        name: "any",
        params: {}
      },
      voteValidation: {
        name: "any",
        params: {}
      },
      filters: {
        minScore: 0,
        onlyMembers: true
      },
      treasuries: [],
      boost: {
        enabled: true,
        bribeEnabled: false
      }
    };

    // Stringify the settings object
    const settingsString = JSON.stringify(settings);

    // Log the exact settings string being sent
    console.log('Settings JSON String:', settingsString);

    // Correctly pass settings as a JSON string
    const receipt = await client.space(wallet, account, {
      space: "testnet-1.eth",
      settings: settingsString
    });

    console.log('Space settings updated', receipt);
  } catch (error) {
    console.error('Error updating space settings:', error);
    if (error.message) {
      console.error('Error message:', error.message);
    }
    if (error.stack) {
      console.error('Error stack:', error.stack);
    }
    if (error.response) {
      console.error('Response error:', error.response.data);
    }
  }
}

// Call the function
modifySpace().catch(console.error);
