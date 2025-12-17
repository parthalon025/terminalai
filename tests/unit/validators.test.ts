/**
 * Unit tests for validators
 */

import { describe, it, expect } from 'vitest';

import {
  isEmpty,
  isPositiveInteger,
  isInRange,
  isValidTemperature,
  isValidMaxTokens,
  isValidModelName,
  sanitizeInput,
  validatePrompt,
} from '../../src/utils/validators.js';

describe('validators', () => {
  describe('isEmpty', () => {
    it('should return true for undefined', () => {
      expect(isEmpty(undefined)).toBe(true);
    });

    it('should return true for null', () => {
      expect(isEmpty(null)).toBe(true);
    });

    it('should return true for empty string', () => {
      expect(isEmpty('')).toBe(true);
    });

    it('should return true for whitespace only', () => {
      expect(isEmpty('   ')).toBe(true);
      expect(isEmpty('\t\n')).toBe(true);
    });

    it('should return false for non-empty string', () => {
      expect(isEmpty('hello')).toBe(false);
      expect(isEmpty('  hello  ')).toBe(false);
    });
  });

  describe('isPositiveInteger', () => {
    it('should return true for positive integers', () => {
      expect(isPositiveInteger(1)).toBe(true);
      expect(isPositiveInteger(100)).toBe(true);
      expect(isPositiveInteger(999999)).toBe(true);
    });

    it('should return false for zero', () => {
      expect(isPositiveInteger(0)).toBe(false);
    });

    it('should return false for negative numbers', () => {
      expect(isPositiveInteger(-1)).toBe(false);
      expect(isPositiveInteger(-100)).toBe(false);
    });

    it('should return false for floats', () => {
      expect(isPositiveInteger(1.5)).toBe(false);
      expect(isPositiveInteger(0.1)).toBe(false);
    });

    it('should return false for non-numbers', () => {
      expect(isPositiveInteger('1')).toBe(false);
      expect(isPositiveInteger(null)).toBe(false);
      expect(isPositiveInteger(undefined)).toBe(false);
    });
  });

  describe('isInRange', () => {
    it('should return true for values within range', () => {
      expect(isInRange(5, 0, 10)).toBe(true);
      expect(isInRange(0, 0, 10)).toBe(true);
      expect(isInRange(10, 0, 10)).toBe(true);
    });

    it('should return false for values outside range', () => {
      expect(isInRange(-1, 0, 10)).toBe(false);
      expect(isInRange(11, 0, 10)).toBe(false);
    });
  });

  describe('isValidTemperature', () => {
    it('should return true for valid temperatures', () => {
      expect(isValidTemperature(0)).toBe(true);
      expect(isValidTemperature(0.7)).toBe(true);
      expect(isValidTemperature(1)).toBe(true);
      expect(isValidTemperature(2)).toBe(true);
    });

    it('should return false for invalid temperatures', () => {
      expect(isValidTemperature(-0.1)).toBe(false);
      expect(isValidTemperature(2.1)).toBe(false);
    });
  });

  describe('isValidMaxTokens', () => {
    it('should return true for valid token counts', () => {
      expect(isValidMaxTokens(1)).toBe(true);
      expect(isValidMaxTokens(1024)).toBe(true);
      expect(isValidMaxTokens(128000)).toBe(true);
    });

    it('should return false for invalid token counts', () => {
      expect(isValidMaxTokens(0)).toBe(false);
      expect(isValidMaxTokens(-1)).toBe(false);
      expect(isValidMaxTokens(128001)).toBe(false);
      expect(isValidMaxTokens(1.5)).toBe(false);
    });
  });

  describe('isValidModelName', () => {
    it('should return true for valid model names', () => {
      expect(isValidModelName('gpt-4')).toBe(true);
      expect(isValidModelName('gpt-3.5-turbo')).toBe(true);
      expect(isValidModelName('claude-3-opus')).toBe(true);
    });

    it('should return false for invalid model names', () => {
      expect(isValidModelName('')).toBe(false);
      expect(isValidModelName('   ')).toBe(false);
      expect(isValidModelName('-invalid')).toBe(false);
    });
  });

  describe('sanitizeInput', () => {
    it('should trim whitespace', () => {
      expect(sanitizeInput('  hello  ')).toBe('hello');
    });

    it('should remove control characters', () => {
      expect(sanitizeInput('hello\x00world')).toBe('helloworld');
      expect(sanitizeInput('test\x1Fvalue')).toBe('testvalue');
    });

    it('should preserve newlines and tabs in content', () => {
      // Note: our sanitizer trims, so leading/trailing are removed
      expect(sanitizeInput('hello\tworld')).toBe('hello\tworld');
    });
  });

  describe('validatePrompt', () => {
    it('should return valid for good prompts', () => {
      const result = validatePrompt('What is the weather?');
      expect(result.valid).toBe(true);
      expect(result.sanitized).toBe('What is the weather?');
    });

    it('should return invalid for empty prompts', () => {
      const result = validatePrompt('');
      expect(result.valid).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should return invalid for whitespace-only prompts', () => {
      const result = validatePrompt('   ');
      expect(result.valid).toBe(false);
    });

    it('should sanitize the prompt', () => {
      const result = validatePrompt('  hello world  ');
      expect(result.valid).toBe(true);
      expect(result.sanitized).toBe('hello world');
    });
  });
});
