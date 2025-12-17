/**
 * Command and input processor
 */

import type { CommandResult } from '../types/index.js';
import { validatePrompt, sanitizeInput } from '../utils/validators.js';
import { debug, error as logError } from '../utils/logger.js';

/**
 * Process user input and prepare it for the assistant
 */
export function processInput(input: string): { processed: string; valid: boolean; error?: string } {
  const validation = validatePrompt(input);

  if (!validation.valid) {
    return {
      processed: '',
      valid: false,
      error: validation.error,
    };
  }

  return {
    processed: validation.sanitized,
    valid: true,
  };
}

/**
 * Parse command-line style input for special commands
 */
export function parseCommand(input: string): { command: string | null; args: string[] } {
  const trimmed = sanitizeInput(input);

  if (!trimmed.startsWith('/')) {
    return { command: null, args: [] };
  }

  const parts = trimmed.slice(1).split(/\s+/);
  const command = parts[0]?.toLowerCase() ?? null;
  const args = parts.slice(1);

  debug(`Parsed command: ${command}, args: ${args.join(', ')}`);

  return { command, args };
}

/**
 * Execute a built-in command
 */
export function executeBuiltinCommand(command: string, _args: string[]): CommandResult {
  const commands: Record<string, () => CommandResult> = {
    help: () => ({
      success: true,
      output: `Available commands:
  /help     - Show this help message
  /clear    - Clear conversation history
  /exit     - Exit the application
  /version  - Show version information`,
    }),
    version: () => ({
      success: true,
      output: 'TerminalAI v0.1.0',
    }),
    clear: () => ({
      success: true,
      output: 'Conversation cleared.',
    }),
    exit: () => ({
      success: true,
      output: 'Goodbye!',
    }),
  };

  const handler = commands[command];

  if (!handler) {
    logError(`Unknown command: ${command}`);
    return {
      success: false,
      error: `Unknown command: /${command}. Type /help for available commands.`,
    };
  }

  return handler();
}

/**
 * Check if input is a special command
 */
export function isSpecialCommand(input: string): boolean {
  return sanitizeInput(input).startsWith('/');
}

/**
 * Process and handle any input (command or message)
 */
export function handleInput(input: string): {
  type: 'command' | 'message';
  processed: string;
  result?: CommandResult;
  error?: string;
} {
  if (isSpecialCommand(input)) {
    const { command, args } = parseCommand(input);
    if (command) {
      const result = executeBuiltinCommand(command, args);
      return {
        type: 'command',
        processed: command,
        result,
      };
    }
    return {
      type: 'command',
      processed: '',
      error: 'Invalid command format',
    };
  }

  const { processed, valid, error } = processInput(input);
  return {
    type: 'message',
    processed,
    error: valid ? undefined : error,
  };
}
