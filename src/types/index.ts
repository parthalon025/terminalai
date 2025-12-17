/**
 * Type definitions for TerminalAI
 */

/**
 * Configuration options for the CLI
 */
export interface Config {
  /** API key for AI service */
  apiKey?: string;
  /** Model to use for completions */
  model: string;
  /** Maximum tokens in response */
  maxTokens: number;
  /** Temperature for response randomness */
  temperature: number;
  /** Enable verbose logging */
  verbose: boolean;
  /** Enable interactive mode */
  interactive: boolean;
}

/**
 * Default configuration values
 */
export const DEFAULT_CONFIG: Config = {
  model: 'gpt-4',
  maxTokens: 1024,
  temperature: 0.7,
  verbose: false,
  interactive: false,
};

/**
 * Message format for chat conversations
 */
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * Response from the AI service
 */
export interface AIResponse {
  content: string;
  tokensUsed: number;
  model: string;
}

/**
 * Command result from execution
 */
export interface CommandResult {
  success: boolean;
  output?: string;
  error?: string;
}

/**
 * CLI command options
 */
export interface CLIOptions {
  interactive?: boolean;
  verbose?: boolean;
  model?: string;
  maxTokens?: number;
}

/**
 * Prompt template for system messages
 */
export interface PromptTemplate {
  name: string;
  template: string;
  description?: string;
}
