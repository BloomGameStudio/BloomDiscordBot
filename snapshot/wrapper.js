/**
 * This is a wrapper for the createProposal function defined in snapshot.js.
 * It reads the proposal details from the command line arguments and passes them to createProposal.
 * 
 * The command line arguments are expected to be in the following order:
 * 1. Title of the proposal
 * 2. Abstract of the proposal
 * 3. Background of the proposal
 * 4. Choices for the proposal (arbitrary number of choices can be provided)
 * 
 * This wrapper is called from the gov/proposals.py Python script using the subprocess.run function.
 * The arguments are passed in the following order: ["node", "./snapshot/wrapper.js", title, abstract, background, "Yes", "No", "Abstain"]
 * 
 * If the createProposal function throws an error, the error is logged and the process exits with a status code of 1.
 */
const createProposal = require('./snapshot.js');

const title = process.argv[2];
const abstract = process.argv[3];
const background = process.argv[4];
const additional = process.argv[5];
const choices = process.argv.slice(6);

createProposal(title, abstract, background, additional, choices).catch(error => {
  console.error('Error in createProposal:', error);
  process.exit(1);
});