/**
 * This file contains the code for modifying the space settings on Snapshot.
 * It uses the ethers.js library to interact with the blockchain and the Snapshot.js library to update space settings.
 * The environment variables ETH_PRIVATE_KEY, PRIMARY_RPC, and SECONDARY_RPC must be set in a .env file.
 * The ETH_PRIVATE_KEY is the private key of the account that will modify the space settings.
 * The PRIMARY_RPC is the primary RPC URL used for submitting the space settings.
 * The SECONDARY_RPC is the secondary RPC URL used as a fallback if the primary RPC fails.
 */

const { ethers } = require('ethers');
const snapshot = require('@snapshot-labs/snapshot.js');

const ethPrivateKey = process.env.ETH_PRIVATE_KEY;
const primaryRpc = process.env.PRIMARY_RPC;
const secondaryRpc = process.env.SECONDARY_RPC;

const maxRetries = 3; // Number of retry attempts
const initialRetryDelay = 5000; // Initial delay between retries in milliseconds (e.g., 5000ms = 5s)

if (!ethPrivateKey) {
  throw new Error('Private key not provided in environment variables');
}

const quorumValue = parseInt(process.argv[2]);

async function submitSpaceSettings(providerRpc, quorumValue) {
  try {
    const provider = new ethers.providers.JsonRpcProvider(providerRpc);
    const wallet = new ethers.Wallet(ethPrivateKey, provider);

    const hub = 'https://hub.snapshot.org';
    const client = new snapshot.Client712(hub);

    const account = await wallet.getAddress();
    console.log('Using account:', account);

    const settings = {
      name: "Bloom Studio",
      about: "Bloom is a decentralized studio creating immersive, expressive games & other audiovisual experiences within a scalable, collective micro-economy",
      network: "42161",
      symbol: "govXP",
      private: false,
      admins: [],
      moderators: [],
      members: ["0xd80e4ef6169e5f737430be8a845237befb9a0adb"],
      categories: [],
      plugins: {},
      children: [],
      voting: {
        quorum: quorumValue,
        hideAbstain: false
      },
      strategies: [
        {
          name: "erc20-balance-of",
          network: "42161",
          params: {
            symbol: "uXP",
            address: "0x57d3a929fdc4faf1b35e7092d9dee7af097afb6a",
            decimals: 18
          }
        },
        {
          name: "erc20-balance-of",
          network: "42161",
          params: {
            symbol: "aXP",
            address: "0x206d247F61cb82B9711318381cDb7Bc5039d2A2c",
            decimals: 18
          }
        },
        {
          name: "erc20-balance-of",
          network: "42161",
          params: {
            symbol: "bXP",
            address: "0x4cd06ada7d8564830018000d784c69bd542b1e6a",
            decimals: 18
          }
        }
      ],
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

    const settingsString = JSON.stringify(settings);
    console.log('Settings JSON String:', settingsString);

    const receipt = await client.space(wallet, account, {
      space: "gov.bloomstudio.eth",
      settings: settingsString
    });

    console.log('Space settings updated', receipt);
    return true; // Indicate success
  } catch (error) {
    console.error(`Error updating space settings with RPC ${providerRpc}:`, error);
    return false; // Indicate failure
  }
}

// Delay function
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Attempt to submit the space settings with a retry mechanism
async function modifySpace() {
  let attempt = 0;
  let success = false;
  let retryDelay = initialRetryDelay;

  while (attempt < maxRetries && !success) {
    attempt++;
    console.log(`Attempt ${attempt} to update space settings...`);

    // Try using the primary RPC
    success = await submitSpaceSettings(primaryRpc, quorumValue);

    // If primary RPC fails, try using the secondary RPC
    if (!success) {
      console.log('Retrying with secondary RPC...');
      success = await submitSpaceSettings(secondaryRpc, quorumValue);
    }

    if (!success) {
      console.log(`Attempt ${attempt} failed.`);
      if (attempt < maxRetries) {
        console.log(`Waiting for ${retryDelay / 1000} seconds before retrying...`);
        await delay(retryDelay); // Wait before the next attempt
        retryDelay *= 2; // Exponential backoff
      }
    }
  }

  if (!success) {
    console.error('Failed to update space settings after multiple attempts with both RPC endpoints');
  }
}

// Call the function
modifySpace().catch(console.error);

