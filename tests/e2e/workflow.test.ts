/**
 * End-to-end workflow tests
 */

import { describe, it, expect, vi } from 'vitest';

import { getConfig, validateConfig } from '../../src/config/index.js';
import { createAssistant } from '../../src/core/assistant.js';
import { handleInput } from '../../src/core/processor.js';

describe('Complete Workflow Tests', () => {
  describe('User Query Workflow', () => {
    it('should complete a full query workflow', async () => {
      // 1. Get configuration
      const config = getConfig();
      const validation = validateConfig(config);
      expect(validation.valid).toBe(true);

      // 2. Create assistant
      const assistant = createAssistant(config);
      assistant.setSystemPrompt('You are a helpful assistant');

      // 3. Process user input
      const userInput = 'How do I list files in a directory?';
      const { type, processed, error } = handleInput(userInput);

      expect(type).toBe('message');
      expect(error).toBeUndefined();

      // 4. Get response from assistant
      const response = await assistant.chat(processed);

      expect(response.content).toBeDefined();
      expect(response.content.length).toBeGreaterThan(0);
      expect(response.tokensUsed).toBeGreaterThan(0);

      // 5. Verify history
      const history = assistant.getHistory();
      expect(history.length).toBe(3); // system + user + assistant
    });

    it('should handle multiple queries in a session', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      const queries = [
        'What is JavaScript?',
        'How do I create a function?',
        'What are arrow functions?',
      ];

      for (const query of queries) {
        const { processed } = handleInput(query);
        const response = await assistant.chat(processed);
        expect(response.content).toBeDefined();
      }

      // Should have 6 messages (3 user + 3 assistant)
      const history = assistant.getHistory();
      expect(history.length).toBe(6);
    });
  });

  describe('Command Workflow', () => {
    it('should handle command workflow', () => {
      // Test help command
      const helpResult = handleInput('/help');
      expect(helpResult.type).toBe('command');
      expect(helpResult.result?.success).toBe(true);

      // Test version command
      const versionResult = handleInput('/version');
      expect(versionResult.type).toBe('command');
      expect(versionResult.result?.output).toContain('TerminalAI');
    });

    it('should handle mixed commands and queries', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      // Start with help
      const helpResult = handleInput('/help');
      expect(helpResult.result?.success).toBe(true);

      // Send a query
      const queryResult = handleInput('What is Node.js?');
      expect(queryResult.type).toBe('message');

      const response = await assistant.chat(queryResult.processed);
      expect(response.content).toBeDefined();

      // Clear history
      const clearResult = handleInput('/clear');
      expect(clearResult.result?.success).toBe(true);
    });
  });

  describe('Error Recovery Workflow', () => {
    it('should recover from invalid input', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      // Invalid input
      const invalidResult = handleInput('');
      expect(invalidResult.error).toBeDefined();

      // Valid input should still work
      const validResult = handleInput('Valid query');
      expect(validResult.error).toBeUndefined();

      const response = await assistant.chat(validResult.processed);
      expect(response.content).toBeDefined();
    });

    it('should handle unknown commands gracefully', () => {
      const unknownResult = handleInput('/unknowncommand');
      expect(unknownResult.result?.success).toBe(false);

      // Help should still work
      const helpResult = handleInput('/help');
      expect(helpResult.result?.success).toBe(true);
    });
  });

  describe('Configuration Workflow', () => {
    it('should work with custom configuration', async () => {
      const config = getConfig({
        model: 'custom-model',
        maxTokens: 512,
        temperature: 0.5,
        verbose: true,
      });

      const assistant = createAssistant(config);
      const assistantConfig = assistant.getConfig();

      expect(assistantConfig.model).toBe('custom-model');
      expect(assistantConfig.maxTokens).toBe(512);
      expect(assistantConfig.temperature).toBe(0.5);

      const response = await assistant.chat('Test with custom config');
      expect(response.model).toBe('custom-model');
    });
  });

  describe('Session Persistence', () => {
    it('should maintain context across messages', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      assistant.setSystemPrompt('Remember all user messages');

      await assistant.chat('My name is Alice');
      await assistant.chat('I like programming');

      const history = assistant.getHistory();
      const userMessages = history.filter(m => m.role === 'user');

      expect(userMessages.some(m => m.content.includes('Alice'))).toBe(true);
      expect(userMessages.some(m => m.content.includes('programming'))).toBe(true);
    });

    it('should clear session correctly', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      assistant.setSystemPrompt('System prompt');
      await assistant.chat('Message 1');
      await assistant.chat('Message 2');

      expect(assistant.getHistoryLength()).toBe(5); // system + 2 user + 2 assistant

      assistant.clearHistory();

      expect(assistant.getHistoryLength()).toBe(1); // only system prompt
    });
  });
});
