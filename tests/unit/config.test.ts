/**
 * Unit tests for configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { loadEnvConfig, mergeConfig, getConfig, validateConfig } from '../../src/config/index.js';
import { DEFAULT_CONFIG } from '../../src/types/index.js';

describe('config', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('loadEnvConfig', () => {
    it('should load API key from environment', () => {
      process.env['TERMINALAI_API_KEY'] = 'test-key';
      const config = loadEnvConfig();
      expect(config.apiKey).toBe('test-key');
    });

    it('should load model from environment', () => {
      process.env['TERMINALAI_MODEL'] = 'gpt-3.5-turbo';
      const config = loadEnvConfig();
      expect(config.model).toBe('gpt-3.5-turbo');
    });

    it('should load max tokens from environment', () => {
      process.env['TERMINALAI_MAX_TOKENS'] = '2048';
      const config = loadEnvConfig();
      expect(config.maxTokens).toBe(2048);
    });

    it('should load temperature from environment', () => {
      process.env['TERMINALAI_TEMPERATURE'] = '0.5';
      const config = loadEnvConfig();
      expect(config.temperature).toBe(0.5);
    });

    it('should load verbose from environment', () => {
      process.env['TERMINALAI_VERBOSE'] = 'true';
      const config = loadEnvConfig();
      expect(config.verbose).toBe(true);
    });

    it('should handle invalid max tokens', () => {
      process.env['TERMINALAI_MAX_TOKENS'] = 'invalid';
      const config = loadEnvConfig();
      expect(config.maxTokens).toBeUndefined();
    });

    it('should return empty config when no env vars set', () => {
      const config = loadEnvConfig();
      expect(config.apiKey).toBeUndefined();
    });
  });

  describe('mergeConfig', () => {
    it('should merge with defaults', () => {
      const config = mergeConfig({ model: 'custom-model' });
      expect(config.model).toBe('custom-model');
      expect(config.maxTokens).toBe(DEFAULT_CONFIG.maxTokens);
    });

    it('should merge multiple configs in order', () => {
      const config = mergeConfig({ model: 'first' }, { model: 'second' }, { model: 'third' });
      expect(config.model).toBe('third');
    });

    it('should not override with undefined values', () => {
      const config = mergeConfig({ model: 'custom' }, { model: undefined });
      expect(config.model).toBe('custom');
    });
  });

  describe('getConfig', () => {
    it('should return default config without overrides', () => {
      const config = getConfig();
      expect(config.model).toBe(DEFAULT_CONFIG.model);
    });

    it('should apply overrides', () => {
      const config = getConfig({ model: 'override-model' });
      expect(config.model).toBe('override-model');
    });
  });

  describe('validateConfig', () => {
    it('should validate correct config', () => {
      const result = validateConfig(DEFAULT_CONFIG);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject negative maxTokens', () => {
      const config = { ...DEFAULT_CONFIG, maxTokens: -1 };
      const result = validateConfig(config);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('maxTokens must be positive');
    });

    it('should reject maxTokens over limit', () => {
      const config = { ...DEFAULT_CONFIG, maxTokens: 200000 };
      const result = validateConfig(config);
      expect(result.valid).toBe(false);
    });

    it('should reject invalid temperature', () => {
      const config = { ...DEFAULT_CONFIG, temperature: 3 };
      const result = validateConfig(config);
      expect(result.valid).toBe(false);
    });

    it('should reject empty model', () => {
      const config = { ...DEFAULT_CONFIG, model: '' };
      const result = validateConfig(config);
      expect(result.valid).toBe(false);
    });
  });
});
