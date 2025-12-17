/**
 * TerminalAI - AI-powered terminal assistant
 *
 * This is the main entry point for the library.
 */

// Export types
export type {
  Config,
  Message,
  AIResponse,
  CommandResult,
  CLIOptions,
  PromptTemplate,
} from './types/index.js';

export { DEFAULT_CONFIG } from './types/index.js';

// Export configuration utilities
export { getConfig, mergeConfig, validateConfig, loadEnvConfig } from './config/index.js';

// Export core functionality
export { Assistant, createAssistant } from './core/assistant.js';
export {
  processInput,
  parseCommand,
  executeBuiltinCommand,
  isSpecialCommand,
  handleInput,
} from './core/processor.js';

// Export utilities
export {
  setVerbose,
  isVerbose,
  debug,
  info,
  warn,
  error,
  success,
  output,
  createLogger,
} from './utils/logger.js';

export {
  isEmpty,
  isPositiveInteger,
  isInRange,
  isValidTemperature,
  isValidMaxTokens,
  isValidModelName,
  sanitizeInput,
  validatePrompt,
} from './utils/validators.js';

export {
  formatNumber,
  formatBytes,
  formatDuration,
  truncate,
  wrapText,
  formatResponse,
} from './utils/formatters.js';
