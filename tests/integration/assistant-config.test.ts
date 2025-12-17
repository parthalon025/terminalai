/**
 * Integration tests for Assistant with Configuration
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { createAssistant } from '../../src/core/assistant.js';
import { getConfig, validateConfig } from '../../src/config/index.js';

describe('Assistant with Configuration Integration', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Configuration Loading', () => {
    it('should create assistant with default config', () => {
      const config = getConfig();
      const assistant = createAssistant(config);
      const assistantConfig = assistant.getConfig();

      expect(assistantConfig.model).toBe('gpt-4');
      expect(assistantConfig.maxTokens).toBe(1024);
    });

    it('should create assistant with environment config', () => {
      process.env['TERMINALAI_MODEL'] = 'gpt-3.5-turbo';
      process.env['TERMINALAI_MAX_TOKENS'] = '2048';

      const config = getConfig();
      const assistant = createAssistant(config);
      const assistantConfig = assistant.getConfig();

      expect(assistantConfig.model).toBe('gpt-3.5-turbo');
      expect(assistantConfig.maxTokens).toBe(2048);
    });

    it('should create assistant with override config', () => {
      const config = getConfig({
        model: 'custom-model',
        temperature: 0.5,
      });
      const assistant = createAssistant(config);
      const assistantConfig = assistant.getConfig();

      expect(assistantConfig.model).toBe('custom-model');
      expect(assistantConfig.temperature).toBe(0.5);
    });
  });

  describe('Configuration Validation', () => {
    it('should validate config before creating assistant', () => {
      const config = getConfig();
      const validation = validateConfig(config);

      expect(validation.valid).toBe(true);

      const assistant = createAssistant(config);
      expect(assistant).toBeDefined();
    });

    it('should handle invalid config gracefully', () => {
      const config = getConfig({ maxTokens: -1 });
      const validation = validateConfig(config);

      expect(validation.valid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });
  });

  describe('Assistant Conversation Flow', () => {
    it('should maintain conversation context', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      assistant.setSystemPrompt('You are a test assistant');

      await assistant.chat('First message');
      await assistant.chat('Second message');

      const history = assistant.getHistory();
      expect(history.length).toBe(5); // system + 2 user + 2 assistant
    });

    it('should clear history while preserving system prompt', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      assistant.setSystemPrompt('System prompt');
      await assistant.chat('User message');

      assistant.clearHistory();

      const history = assistant.getHistory();
      expect(history.length).toBe(1);
      expect(history[0]?.role).toBe('system');
    });
  });
});
