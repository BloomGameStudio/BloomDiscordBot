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
const { ethers, logger } = require('ethers');
const snapshot = require('@snapshot-labs/snapshot.js');
const dotenv = require('dotenv');

dotenv.config();

/**
 *
 * @param {string} title - The title of the proposal
 * @param {*} body - The body of the proposal
 * @param {*} choices - The choices for the proposal
 */
async function createProposal(title, body, choices) {
  const ethAddress = process.env.ETH_ADDRESS;
  const ethPrivateKey = process.env.ETH_PRIVATE_KEY;
  const primaryRpc = process.env.PRIMARY_RPC_URL;
  const secondaryRpc = process.env.SECONDARY_RPC_URL;
  const hub = process.env.SNAPSHOT_HUB;
  const snapshotSpace = process.env.SNAPSHOT_SPACE;
  const networkId = process.env.NETWORK_ID;

  const maxRetries = 3;
  const initialRetryDelay = 5000;

  if (!ethAddress || !ethPrivateKey) {
    throw new Error('Ethereum address or private key not provided in environment variables');
  }

  /**
   * Submits a proposal to Snapshot using the provided RPC endpoint
   * @param {string} providerRpc - RPC endpoint URL
   * @returns {Object} Object containing receipt and error
   */
  async function submitProposal(providerRpc) {
    const provider = new ethers.providers.JsonRpcProvider(providerRpc);
    const wallet = new ethers.Wallet(ethPrivateKey, provider);
    const client = new snapshot.Client712(hub);
    const currentTime = Math.floor(new Date().getTime() / 1000);
    const seventyTwoHours = 72 * 3600;

    try {
      const proposalParams = {
        space: snapshotSpace,
        type: 'weighted',
        title: title,
        body: body,
        choices: choices,
        start: currentTime,
        end: currentTime + seventyTwoHours,
        snapshot: await provider.getBlockNumber(),
        network: networkId,
        plugins: JSON.stringify({}),
        app: 'Gov'
      };

      logger.info(proposalParams)

      const receipt = await client.proposal(wallet, ethAddress, proposalParams);

      return { receipt, error: null };
    } catch (error) {
      console.error(`Error creating proposal with RPC ${providerRpc}:`, error);
      return { receipt: null, error };
    }
  }

  /**
   * Helper function to create a delay
   * @param {number} ms - Milliseconds to delay
   */
  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  let attempt = 0;
  let error = null;
  let receipt = null;
  let retryDelay = initialRetryDelay;
  let success = false;

  while (attempt < maxRetries && !success) {
    attempt++;
    console.log(`Attempt ${attempt} to submit proposal...`);

    const primaryResult = await submitProposal(primaryRpc);
    receipt = primaryResult.receipt;
    error = primaryResult.error;

    if (error) {
      console.log('Retrying with secondary RPC...');
      const secondaryResult = await submitProposal(secondaryRpc);
      receipt = secondaryResult.receipt;
      error = secondaryResult.error;
    }

    success = receipt !== null;

    if (error) {
      console.log(`Attempt ${attempt} failed.`);
      if (attempt < maxRetries) {
        console.log(`Waiting for ${retryDelay / 1000} seconds before retrying...`);
        await delay(retryDelay);
        retryDelay *= 2;
      }
    }
  }

  if (error) {
    console.error('Failed to submit proposal after multiple attempts with both RPC endpoints');
    return null
  } else {
    return receipt
  }
}

module.exports = createProposal;
