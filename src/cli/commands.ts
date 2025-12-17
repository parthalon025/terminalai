/**
 * CLI command definitions
 */

import { Command } from 'commander';

import { getConfig } from '../config/index.js';
import { createAssistant } from '../core/assistant.js';
import { handleInput } from '../core/processor.js';
import type { CLIOptions } from '../types/index.js';
import { setVerbose, output, error, success } from '../utils/logger.js';

import { startInteractiveMode } from './interactive.js';

/**
 * Create the main CLI program
 */
export function createProgram(): Command {
  const program = new Command();

  program
    .name('terminalai')
    .description('AI-powered terminal assistant')
    .version('0.1.0')
    .option('-i, --interactive', 'Start in interactive mode')
    .option('-v, --verbose', 'Enable verbose logging')
    .option('-m, --model <model>', 'AI model to use', 'gpt-4')
    .option('-t, --max-tokens <number>', 'Maximum tokens in response', '1024')
    .argument('[prompt...]', 'Prompt to send to the AI')
    .action(async (promptParts: string[], options: CLIOptions) => {
      await runCLI(promptParts, options);
    });

  return program;
}

/**
 * Run the CLI with the given options
 */
export async function runCLI(promptParts: string[], options: CLIOptions): Promise<void> {
  // Set up logging
  if (options.verbose) {
    setVerbose(true);
  }

  // Build configuration
  const config = getConfig({
    verbose: options.verbose,
    model: options.model,
    maxTokens: options.maxTokens ? parseInt(String(options.maxTokens), 10) : undefined,
    interactive: options.interactive,
  });

  // Start interactive mode if requested or no prompt provided
  if (options.interactive || promptParts.length === 0) {
    await startInteractiveMode(config);
    return;
  }

  // Process single prompt
  const prompt = promptParts.join(' ');
  const { type, processed, result, error: inputError } = handleInput(prompt);

  if (inputError) {
    error(inputError);
    process.exitCode = 1;
    return;
  }

  if (type === 'command' && result) {
    if (result.success) {
      output(result.output ?? '');
    } else {
      error(result.error ?? 'Command failed');
      process.exitCode = 1;
    }
    return;
  }

  // Send to assistant
  const assistant = createAssistant(config);

  try {
    const response = await assistant.chat(processed);
    output(response.content);
    if (config.verbose) {
      success(`Tokens used: ${response.tokensUsed}`);
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    error(`Failed to get response: ${message}`);
    process.exitCode = 1;
  }
}
