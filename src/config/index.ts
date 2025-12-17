/**
 * Configuration management for TerminalAI
 */

import type { Config } from '../types/index.js';
import { DEFAULT_CONFIG } from '../types/index.js';

/**
 * Load configuration from environment variables
 */
export function loadEnvConfig(): Partial<Config> {
  const config: Partial<Config> = {};

  if (process.env['TERMINALAI_API_KEY']) {
    config.apiKey = process.env['TERMINALAI_API_KEY'];
  }

  if (process.env['TERMINALAI_MODEL']) {
    config.model = process.env['TERMINALAI_MODEL'];
  }

  if (process.env['TERMINALAI_MAX_TOKENS']) {
    const maxTokens = parseInt(process.env['TERMINALAI_MAX_TOKENS'], 10);
    if (!isNaN(maxTokens)) {
      config.maxTokens = maxTokens;
    }
  }

  if (process.env['TERMINALAI_TEMPERATURE']) {
    const temperature = parseFloat(process.env['TERMINALAI_TEMPERATURE']);
    if (!isNaN(temperature)) {
      config.temperature = temperature;
    }
  }

  if (process.env['TERMINALAI_VERBOSE'] === 'true') {
    config.verbose = true;
  }

  return config;
}

/**
 * Merge configuration objects with defaults
 */
export function mergeConfig(...configs: Partial<Config>[]): Config {
  return configs.reduce<Config>(
    (merged, config) => ({
      ...merged,
      ...Object.fromEntries(Object.entries(config).filter(([_, value]) => value !== undefined)),
    }),
    { ...DEFAULT_CONFIG }
  );
}

/**
 * Get the full configuration with all sources merged
 */
export function getConfig(overrides?: Partial<Config>): Config {
  const envConfig = loadEnvConfig();
  return mergeConfig(DEFAULT_CONFIG, envConfig, overrides ?? {});
}

/**
 * Validate configuration
 */
export function validateConfig(config: Config): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (config.maxTokens <= 0) {
    errors.push('maxTokens must be positive');
  }

  if (config.maxTokens > 128000) {
    errors.push('maxTokens exceeds maximum allowed value');
  }

  if (config.temperature < 0 || config.temperature > 2) {
    errors.push('temperature must be between 0 and 2');
  }

  if (!config.model || config.model.trim().length === 0) {
    errors.push('model is required');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
