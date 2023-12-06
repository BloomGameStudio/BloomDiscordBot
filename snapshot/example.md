import { Web3Provider } from '@ethersproject/providers';

const web3 = new Web3Provider(window.ethereum);
const [account] = await web3.listAccounts();

const receipt = await client.proposal(web3, account, {
  space: 'yam.eth',
  type: 'single-choice', // define the voting system
  title: 'Test proposal using Snapshot.js',
  body: 'This is the content of the proposal',
  choices: ['Alice', 'Bob', 'Carol'],
  start: 1636984800,
  end: 1637244000,
  snapshot: 13620822,
  network: '1',
  plugins: JSON.stringify({}),
  app: 'my-app' // provide the name of your project which is using this snapshot.js integration
});