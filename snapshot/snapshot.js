/**
 * This file contains the code for creating a proposal on Snapshot.
 * It uses the ethers.js library to interact with the blockchain.
 * The proposal is created using the Snapshot.js library.
 * The environment variables ETH_ADDRESS, ETH_PRIVATE_KEY, PRIMARY_RPC, and SECONDARY_RPC must be set in a .env file.
 * The ETH_ADDRESS is the address of the account that will create the proposal.
 * The ETH_PRIVATE_KEY is the private key of the ETH_ADDRESS account.
 * The PRIMARY_RPC is the primary RPC URL you wish to use for submitting proposals.
 * The SECONDARY_RPC is the secondary RPC URL you wish to use for submitting proposals.
 * wrapper.js is responsible for calling this function with the correct arguments.
 */
const { ethers } = require('ethers');
const snapshot = require('@snapshot-labs/snapshot.js');
const dotenv = require('dotenv');

dotenv.config();

/**
 *
 * @param {string} title - The title of the proposal
 * @param {*} abstract  - The abstract of the proposal
 * @param {*} background - The background of the proposal
 * @param {*} choices - The choices for the proposal
 */
async function createProposal(title, abstract, background, additional, choices) {
  const ethAddress = process.env.ETH_ADDRESS;
  const ethPrivateKey = process.env.ETH_PRIVATE_KEY;
  const primaryRpc = process.env.PRIMARY_RPC;
  const secondaryRpc = process.env.SECONDARY_RPC;
  const hub = process.env.SNAPSHOT_HUB;
  const snapshotSpace = process.env.SNAPSHOT_SPACE;
  const network = process.env.NETWORK;

  const maxRetries = 3;
  const initialRetryDelay = 5000;

  if (!ethAddress || !ethPrivateKey) {
    throw new Error('Ethereum address or private key not provided in environment variables');
  }

  async function submitProposal(providerRpc) {
    try {
      const provider = new ethers.providers.JsonRpcProvider(providerRpc);
      const wallet = new ethers.Wallet(ethPrivateKey, provider);

      const client = new snapshot.Client712(hub);

      const currentTime = Math.floor(new Date().getTime() / 1000);
      const seventyTwoHoursInSeconds = 72 * 3600;

      const proposalParams = {
        space: snapshotSpace,
        type: 'weighted',
        title: title,
        body: `\n ${abstract}\n\n \n ${background}\n\n \n ${additional}`,
        choices: choices,
        start: currentTime,
        end: currentTime + seventyTwoHoursInSeconds,
        snapshot: await provider.getBlockNumber(),
        network: network,
        plugins: JSON.stringify({}),
        app: 'Gov'
      };

      const receipt = await client.proposal(wallet, ethAddress, proposalParams);

      console.log('Proposal submitted. Receipt:', receipt);
      return true;
    } catch (error) {
      console.error(`Error creating proposal with RPC ${providerRpc}:`, error);
      return false;
    }
  }

  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  let attempt = 0;
  let success = false;
  let retryDelay = initialRetryDelay;

  while (attempt < maxRetries && !success) {
    attempt++;
    console.log(`Attempt ${attempt} to submit proposal...`);

    success = await submitProposal(primaryRpc);

    if (!success) {
      console.log('Retrying with secondary RPC...');
      success = await submitProposal(secondaryRpc);
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
    console.error('Failed to submit proposal after multiple attempts with both RPC endpoints');
  }
}

module.exports = createProposal;
