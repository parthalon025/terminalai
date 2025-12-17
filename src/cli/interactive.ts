/**
 * Interactive mode for the CLI
 */

import * as readline from 'node:readline';

import chalk from 'chalk';
import ora from 'ora';

import type { Config } from '../types/index.js';
import { createAssistant } from '../core/assistant.js';
import { handleInput } from '../core/processor.js';
import { output, error, debug } from '../utils/logger.js';
import { formatResponse } from '../utils/formatters.js';

/**
 * Start interactive mode
 */
export async function startInteractiveMode(config: Config): Promise<void> {
  const assistant = createAssistant(config);

  // Set up system prompt
  assistant.setSystemPrompt(
    'You are a helpful terminal assistant. Provide concise, accurate answers for terminal and programming questions.'
  );

  output(chalk.bold('\nTerminalAI Interactive Mode'));
  output(chalk.gray('Type your message or /help for commands. Use /exit to quit.\n'));

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const prompt = (): void => {
    rl.question(chalk.green('> '), input => {
      void processInteractiveInput(input, assistant, config, rl, prompt);
    });
  };

  // Handle Ctrl+C gracefully
  rl.on('close', () => {
    output(chalk.gray('\nGoodbye!'));
    process.exit(0);
  });

  prompt();
}

/**
 * Process input in interactive mode
 */
async function processInteractiveInput(
  input: string,
  assistant: ReturnType<typeof createAssistant>,
  config: Config,
  rl: readline.Interface,
  promptFn: () => void
): Promise<void> {
  const trimmedInput = input.trim();

  if (trimmedInput.length === 0) {
    promptFn();
    return;
  }

  const { type, processed, result, error: inputError } = handleInput(trimmedInput);

  if (inputError) {
    error(inputError);
    promptFn();
    return;
  }

  if (type === 'command') {
    if (processed === 'exit') {
      output(chalk.gray('Goodbye!'));
      rl.close();
      return;
    }

    if (processed === 'clear') {
      assistant.clearHistory();
    }

    if (result) {
      output(result.success ? (result.output ?? '') : chalk.red(result.error ?? ''));
    }
    promptFn();
    return;
  }

  // Send message to assistant
  const spinner = ora({
    text: 'Thinking...',
    color: 'cyan',
  }).start();

  try {
    debug(`Sending message: ${processed.substring(0, 50)}...`);
    const response = await assistant.chat(processed);
    spinner.stop();

    output('');
    output(chalk.cyan('Assistant:'));
    output(formatResponse(response.content));
    output('');

    if (config.verbose) {
      output(chalk.gray(`[${response.tokensUsed} tokens, ${response.model}]`));
    }
  } catch (err) {
    spinner.stop();
    const message = err instanceof Error ? err.message : 'Unknown error';
    error(`Failed to get response: ${message}`);
  }

  promptFn();
}
