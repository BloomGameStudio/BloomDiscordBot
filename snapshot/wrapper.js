const createProposal = require('./snapshot.js');

createProposal().catch(error => {
  console.error('Error in createProposal:', error);
  process.exit(1);
});