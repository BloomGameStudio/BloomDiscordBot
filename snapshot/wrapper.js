/**
 * This is a wrapper for the createProposal function defined in snapshot.js.
 * It reads the proposal details from the command line arguments and passes them to createProposal.
 * 
 * The command line arguments are expected to be in the following order:
 * 1. Title of the proposal
 * 2. JSON string containing sections of the proposal
 * 3. Result prefix to prepend to output
 * 4. Choices for the proposal (arbitrary number of choices can be provided)
 * 
 * This wrapper is called from the gov/proposals.py Python script using the subprocess.run function.
 * The arguments are passed in the following order: ["node", "./snapshot/wrapper.js", title, sectionsJson, resultPrefix, "Yes", "No", "Abstain"]
 * 
 * If the createProposal function throws an error, the error is logged and the process exits with a status code of 1.
 * 
 * The function returns a JSON string containing the proposal receipt that can be parsed by the calling Python script.
 */
const createProposal = require('./snapshot.js');

const title = process.argv[2];
const sectionsJson = process.argv[3];
const resultPrefix = process.argv[4];
const choices = process.argv.slice(5);

if (!choices.length) {
  console.error('No choices provided.');
  process.exit(1);
}

try {
  const sections = JSON.parse(sectionsJson);
  
  // Use messages array if available, otherwise use content
  const messages = sections.messages || [sections.content];
  const body = messages.join('\n\n');

  createProposal(
    title,
    body,
    choices
  ).then(receipt => {
    // Print receipt as JSON string to stdout for Python to capture
    console.log(resultPrefix + JSON.stringify(receipt));
  }).catch(error => {
    console.error('Error in createProposal:', error);
    process.exit(1);
  });
} catch (error) {
  console.error('Error parsing sections JSON:', error);
  process.exit(1);
}
