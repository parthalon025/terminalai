/**
 * Unit tests for the Assistant class
 */

import { describe, it, expect, beforeEach } from 'vitest';

import { Assistant, createAssistant } from '../../src/core/assistant.js';
import { DEFAULT_CONFIG } from '../../src/types/index.js';

describe('Assistant', () => {
  let assistant: Assistant;

  beforeEach(() => {
    assistant = new Assistant(DEFAULT_CONFIG);
  });

  describe('constructor', () => {
    it('should create an assistant with config', () => {
      const config = assistant.getConfig();
      expect(config.model).toBe(DEFAULT_CONFIG.model);
    });
  });

  describe('getConfig', () => {
    it('should return a copy of the config', () => {
      const config = assistant.getConfig();
      expect(config).toEqual(DEFAULT_CONFIG);
      expect(config).not.toBe(DEFAULT_CONFIG);
    });
  });

  describe('setSystemPrompt', () => {
    it('should set the system prompt', () => {
      assistant.setSystemPrompt('You are a helpful assistant');
      const history = assistant.getHistory();
      expect(history[0]?.role).toBe('system');
      expect(history[0]?.content).toBe('You are a helpful assistant');
    });

    it('should replace existing system prompt', () => {
      assistant.setSystemPrompt('First prompt');
      assistant.setSystemPrompt('Second prompt');
      const history = assistant.getHistory();
      const systemMessages = history.filter(m => m.role === 'system');
      expect(systemMessages).toHaveLength(1);
      expect(systemMessages[0]?.content).toBe('Second prompt');
    });
  });

  describe('chat', () => {
    it('should add user message to history', async () => {
      await assistant.chat('Hello');
      const history = assistant.getHistory();
      expect(history.some(m => m.role === 'user' && m.content === 'Hello')).toBe(true);
    });

    it('should add assistant response to history', async () => {
      await assistant.chat('Hello');
      const history = assistant.getHistory();
      expect(history.some(m => m.role === 'assistant')).toBe(true);
    });

    it('should return an AIResponse', async () => {
      const response = await assistant.chat('Hello');
      expect(response.content).toBeDefined();
      expect(response.tokensUsed).toBeGreaterThan(0);
      expect(response.model).toBe(DEFAULT_CONFIG.model);
    });

    it('should handle help keyword', async () => {
      const response = await assistant.chat('I need help');
      expect(response.content).toContain('help');
    });

    it('should handle hello keyword', async () => {
      const response = await assistant.chat('hello');
      expect(response.content.toLowerCase()).toContain('hello');
    });
  });

  describe('getHistory', () => {
    it('should return empty array initially', () => {
      expect(assistant.getHistory()).toEqual([]);
    });

    it('should return a copy of history', async () => {
      await assistant.chat('Test');
      const history1 = assistant.getHistory();
      const history2 = assistant.getHistory();
      expect(history1).not.toBe(history2);
    });
  });

  describe('clearHistory', () => {
    it('should clear conversation history', async () => {
      await assistant.chat('Message 1');
      await assistant.chat('Message 2');
      assistant.clearHistory();
      expect(assistant.getHistory()).toEqual([]);
    });

    it('should preserve system prompt when clearing', async () => {
      assistant.setSystemPrompt('System');
      await assistant.chat('User message');
      assistant.clearHistory();
      const history = assistant.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0]?.role).toBe('system');
    });
  });

  describe('getHistoryLength', () => {
    it('should return 0 for empty history', () => {
      expect(assistant.getHistoryLength()).toBe(0);
    });

    it('should return correct length', async () => {
      assistant.setSystemPrompt('System');
      await assistant.chat('Message');
      // system + user + assistant = 3
      expect(assistant.getHistoryLength()).toBe(3);
    });
  });

  describe('createAssistant', () => {
    it('should create an Assistant instance', () => {
      const instance = createAssistant(DEFAULT_CONFIG);
      expect(instance).toBeInstanceOf(Assistant);
    });
  });
});
