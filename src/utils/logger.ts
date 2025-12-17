/**
 * Logger utility for consistent output formatting
 */

import chalk from 'chalk';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

let verboseMode = false;

/**
 * Set verbose mode for debug logging
 */
export function setVerbose(verbose: boolean): void {
  verboseMode = verbose;
}

/**
 * Check if verbose mode is enabled
 */
export function isVerbose(): boolean {
  return verboseMode;
}

/**
 * Log a debug message (only in verbose mode)
 */
export function debug(message: string): void {
  if (verboseMode) {
    process.stdout.write(chalk.gray(`[DEBUG] ${message}\n`));
  }
}

/**
 * Log an info message
 */
export function info(message: string): void {
  process.stdout.write(chalk.blue(`[INFO] ${message}\n`));
}

/**
 * Log a warning message
 */
export function warn(message: string): void {
  process.stdout.write(chalk.yellow(`[WARN] ${message}\n`));
}

/**
 * Log an error message
 */
export function error(message: string): void {
  process.stderr.write(chalk.red(`[ERROR] ${message}\n`));
}

/**
 * Log a success message
 */
export function success(message: string): void {
  process.stdout.write(chalk.green(`✓ ${message}\n`));
}

/**
 * Log plain output without formatting
 */
export function output(message: string): void {
  process.stdout.write(`${message}\n`);
}

/**
 * Create a logger instance with a specific prefix
 */
export function createLogger(prefix: string): {
  debug: (msg: string) => void;
  info: (msg: string) => void;
  warn: (msg: string) => void;
  error: (msg: string) => void;
} {
  return {
    debug: (msg: string) => debug(`[${prefix}] ${msg}`),
    info: (msg: string) => info(`[${prefix}] ${msg}`),
    warn: (msg: string) => warn(`[${prefix}] ${msg}`),
    error: (msg: string) => error(`[${prefix}] ${msg}`),
  };
}

export default {
  setVerbose,
  isVerbose,
  debug,
  info,
  warn,
  error,
  success,
  output,
  createLogger,
};
