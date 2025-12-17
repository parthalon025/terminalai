/**
 * Integration tests for input processing flow
 */

import { describe, it, expect } from 'vitest';

import { handleInput, processInput } from '../../src/core/processor.js';
import { createAssistant } from '../../src/core/assistant.js';
import { getConfig } from '../../src/config/index.js';

describe('Processor Flow Integration', () => {
  describe('Command Processing', () => {
    it('should process help command through full flow', () => {
      const result = handleInput('/help');

      expect(result.type).toBe('command');
      expect(result.result?.success).toBe(true);
      expect(result.result?.output).toContain('Available commands');
    });

    it('should process exit command through full flow', () => {
      const result = handleInput('/exit');

      expect(result.type).toBe('command');
      expect(result.result?.success).toBe(true);
      expect(result.result?.output).toContain('Goodbye');
    });

    it('should handle unknown commands gracefully', () => {
      const result = handleInput('/nonexistent');

      expect(result.type).toBe('command');
      expect(result.result?.success).toBe(false);
      expect(result.result?.error).toContain('Unknown command');
    });
  });

  describe('Message Processing', () => {
    it('should process messages through full flow', () => {
      const result = handleInput('Hello, how are you?');

      expect(result.type).toBe('message');
      expect(result.processed).toBe('Hello, how are you?');
      expect(result.error).toBeUndefined();
    });

    it('should sanitize and validate messages', () => {
      const result = handleInput('  Message with spaces  ');

      expect(result.processed).toBe('Message with spaces');
    });

    it('should reject empty messages', () => {
      const result = handleInput('');

      expect(result.error).toBeDefined();
    });

    it('should reject whitespace-only messages', () => {
      const result = handleInput('   ');

      expect(result.error).toBeDefined();
    });
  });

  describe('Assistant Integration', () => {
    it('should process message and send to assistant', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      const { processed, valid } = processInput('Test message');
      expect(valid).toBe(true);

      const response = await assistant.chat(processed);
      expect(response.content).toBeDefined();
      expect(response.tokensUsed).toBeGreaterThan(0);
    });

    it('should handle multiple messages in sequence', async () => {
      const config = getConfig();
      const assistant = createAssistant(config);

      const messages = ['First message', 'Second message', 'Third message'];

      for (const msg of messages) {
        const { processed, valid } = processInput(msg);
        expect(valid).toBe(true);
        await assistant.chat(processed);
      }

      const history = assistant.getHistory();
      expect(history.filter(m => m.role === 'user')).toHaveLength(3);
    });
  });

  describe('Edge Cases', () => {
    it('should handle command-like messages', () => {
      // Message starting with / but not a valid command
      const result = handleInput('/123abc');

      expect(result.type).toBe('command');
    });

    it('should handle very long messages', () => {
      const longMessage = 'a'.repeat(10000);
      const result = handleInput(longMessage);

      expect(result.type).toBe('message');
      expect(result.processed.length).toBe(10000);
    });

    it('should handle special characters', () => {
      const result = handleInput('Hello! How are you? 🎉');

      expect(result.type).toBe('message');
      expect(result.error).toBeUndefined();
    });
  });
});
