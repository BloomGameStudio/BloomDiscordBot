/**
 * This file contains the code for creating a proposal on Snapshot.
 * It uses the ethers.js library to interact with the Ethereum blockchain.
 * The proposal is created using the Snapshot.js library.
 * The environment variables ETH_ADDRESS and ETH_PRIVATE_KEY must be set in a .env file.
 * The ETH_ADDRESS is the address of the account that will create the proposal.
 * The ETH_PRIVATE_KEY is the private key of the ETH_ADDRESS account.
 */
const { ethers } = require('ethers');
const snapshot = require('@snapshot-labs/snapshot.js');
const dotenv = require('dotenv');

dotenv.config();

/**
 * 
 * @param {string} text - The text to remove markdown from 
 * @returns {string} - The text with markdown removed.
 */
function removeMarkdown(text) {
  const markdownRegex = /([_*~`]|(\\r\\n|\\n))/g;
  return text.replace(markdownRegex, '');
}

/**
 * 
 * @param {string} title - The title of the proposal 
 * @param {*} abstract  - The abstract of the proposal
 * @param {*} background - The background of the proposal
 * @param {*} choices - The choices for the proposal
 */
async function createProposal(title, abstract, background, choices) {
  try {
    const ethAddress = process.env.ETH_ADDRESS;
    const ethPrivateKey = process.env.ETH_PRIVATE_KEY;

    if (!ethAddress || !ethPrivateKey) {
      throw new Error('Ethereum address or private key not provided in environment variables');
    }

    const provider = new ethers.providers.JsonRpcProvider('https://rpc.ankr.com/eth_goerli');

    const wallet = new ethers.Wallet(ethPrivateKey, provider);

    const hub = 'https://hub.snapshot.org';

    // Initialize Snapshot client
    const client = new snapshot.Client712(hub);

    // Define proposal parameters
    const currentTime = Math.floor(new Date().getTime() / 1000); // Current time in seconds
    const fortyeighthoursinSeconds = 48 * 3600;

    const proposalParams = {
      space: 'gov.bloomstudio.eth',
      type: 'weighted', // define the voting system
      title: removeMarkdown(title),
      body: `Abstract:\n ${removeMarkdown(abstract)}\n\n Background:\n ${removeMarkdown(background)}`,
      choices: choices.map(removeMarkdown),
      start: currentTime,
      end: currentTime + fortyeighthoursinSeconds, // End time is one hour later as an example
      snapshot: await provider.getBlockNumber(), // Current block number as snapshot
      network: '1',
      plugins: JSON.stringify({}),
      app: 'Bloom-Gov' // provide the name of your project using this Snapshot.js integration
    };

    // Submit the proposal
    const receipt = await client.proposal(wallet, ethAddress, proposalParams);

    // Log the receipt details
    console.log('Proposal submitted. Receipt:', receipt);
  } catch (error) {
    console.error('Error creating proposal:', error);
  }
}

module.exports = createProposal;