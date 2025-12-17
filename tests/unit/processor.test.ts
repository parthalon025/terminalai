/**
 * Unit tests for the processor module
 */

import { describe, it, expect } from 'vitest';

import {
  processInput,
  parseCommand,
  executeBuiltinCommand,
  isSpecialCommand,
  handleInput,
} from '../../src/core/processor.js';

describe('processor', () => {
  describe('processInput', () => {
    it('should process valid input', () => {
      const result = processInput('Hello world');
      expect(result.valid).toBe(true);
      expect(result.processed).toBe('Hello world');
    });

    it('should reject empty input', () => {
      const result = processInput('');
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should trim and sanitize input', () => {
      const result = processInput('  Hello  ');
      expect(result.processed).toBe('Hello');
    });
  });

  describe('parseCommand', () => {
    it('should parse simple commands', () => {
      const result = parseCommand('/help');
      expect(result.command).toBe('help');
      expect(result.args).toEqual([]);
    });

    it('should parse commands with arguments', () => {
      const result = parseCommand('/search foo bar');
      expect(result.command).toBe('search');
      expect(result.args).toEqual(['foo', 'bar']);
    });

    it('should return null for non-commands', () => {
      const result = parseCommand('hello world');
      expect(result.command).toBeNull();
    });

    it('should lowercase command names', () => {
      const result = parseCommand('/HELP');
      expect(result.command).toBe('help');
    });
  });

  describe('executeBuiltinCommand', () => {
    it('should execute help command', () => {
      const result = executeBuiltinCommand('help', []);
      expect(result.success).toBe(true);
      expect(result.output).toContain('Available commands');
    });

    it('should execute version command', () => {
      const result = executeBuiltinCommand('version', []);
      expect(result.success).toBe(true);
      expect(result.output).toContain('TerminalAI');
    });

    it('should execute clear command', () => {
      const result = executeBuiltinCommand('clear', []);
      expect(result.success).toBe(true);
    });

    it('should execute exit command', () => {
      const result = executeBuiltinCommand('exit', []);
      expect(result.success).toBe(true);
      expect(result.output).toContain('Goodbye');
    });

    it('should handle unknown commands', () => {
      const result = executeBuiltinCommand('unknown', []);
      expect(result.success).toBe(false);
      expect(result.error).toContain('Unknown command');
    });
  });

  describe('isSpecialCommand', () => {
    it('should return true for commands starting with /', () => {
      expect(isSpecialCommand('/help')).toBe(true);
      expect(isSpecialCommand('/exit')).toBe(true);
    });

    it('should return false for regular messages', () => {
      expect(isSpecialCommand('hello')).toBe(false);
      expect(isSpecialCommand('help me')).toBe(false);
    });

    it('should handle whitespace', () => {
      expect(isSpecialCommand('  /help')).toBe(true);
    });
  });

  describe('handleInput', () => {
    it('should handle commands', () => {
      const result = handleInput('/help');
      expect(result.type).toBe('command');
      expect(result.result?.success).toBe(true);
    });

    it('should handle messages', () => {
      const result = handleInput('Hello world');
      expect(result.type).toBe('message');
      expect(result.processed).toBe('Hello world');
    });

    it('should handle invalid input', () => {
      const result = handleInput('');
      expect(result.error).toBeDefined();
    });

    it('should handle unknown commands', () => {
      const result = handleInput('/unknown');
      expect(result.type).toBe('command');
      expect(result.result?.success).toBe(false);
    });
  });
});
