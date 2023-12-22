const createProposal = require('./snapshot.js');

const title = process.argv[2];
const abstract = process.argv[3];
const background = process.argv[4];
const options = process.argv.slice(5);

createProposal(title, abstract, background, options).catch(error => {
  console.error('Error in createProposal:', error);
  process.exit(1);
});