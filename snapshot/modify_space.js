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
const dotenv = require('dotenv');

dotenv.config();

const ethPrivateKey = process.env.ETH_PRIVATE_KEY;
const primaryRpc = process.env.PRIMARY_RPC_URL;
const secondaryRpc = process.env.SECONDARY_RPC_URL;

const hub = process.env.SNAPSHOT_HUB;
const snapshotSpace = process.env.SNAPSHOT_SPACE;
const networkId = process.env.NETWORK_ID;
const settingsName = process.env.SETTINGS_NAME;
const settingsAbout = process.env.SETTINGS_ABOUT;
const settingsAvatar = process.env.SETTINGS_AVATAR;
const settingsSymbol = process.env.SETTINGS_SYMBOL;
const settingsMembers = process.env.SETTINGS_MEMBERS ? process.env.SETTINGS_MEMBERS.split(',') : [];
const settingsAdmins = process.env.SETTINGS_ADMINS.split(',');
const settingsStrategies = JSON.parse(process.env.SETTINGS_STRATEGIES);

const maxRetries = 3;
const initialRetryDelay = 5000;

const quorumValue = parseInt(process.argv[2], 10);

async function submitSpaceSettings(providerRpc, quorumValue) {
  try {
    const provider = new ethers.providers.JsonRpcProvider(providerRpc);
    const wallet = new ethers.Wallet(ethPrivateKey, provider);
    const client = new snapshot.Client712(hub);

    const account = await wallet.getAddress();
    console.log('Using account:', account);

    const settings = {
      private: false,
      network: networkId,
      name: settingsName,
      about: settingsAbout,
      avatar: settingsAvatar,
      symbol: settingsSymbol,
      members: settingsMembers,
      admins: settingsAdmins,
      strategies: settingsStrategies,
      voting: {
        quorum: quorumValue,
        hideAbstain: false
      },
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
      space: snapshotSpace,
      settings: settingsString
    });

    console.log('Space settings updated', receipt);
    return true;
  } catch (error) {
    if (error.response && typeof error.response.text === 'function') {
      console.error(`Error response from server: ${await error.response.text()}`);
    } else if (error instanceof Error) {
      console.error(`Error: ${error.message}`);
    } else {
      console.error('Unexpected error:', error);
    }
    return false;
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function modifySpace() {
  let attempt = 0;
  let success = false;
  let retryDelay = initialRetryDelay;

  while (attempt < maxRetries && !success) {
    attempt++;
    console.log(`Attempt ${attempt} to update space settings...`);

    success = await submitSpaceSettings(primaryRpc, quorumValue);

    if (!success) {
      console.log('Retrying with secondary RPC...');
      success = await submitSpaceSettings(secondaryRpc, quorumValue);
    }

    if (!success) {
      console.log(`Attempt ${attempt} failed.`);
      if (attempt < maxRetries) {
        console.log(`Waiting for ${retryDelay / 1000} seconds before retrying...`);
        await delay(retryDelay);
        retryDelay *= 2;
      }
    }
  }

  if (!success) {
    console.error('Failed to update space settings after multiple attempts with both RPC endpoints');
  }
}

modifySpace().catch(console.error);
