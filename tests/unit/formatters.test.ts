/**
 * Unit tests for formatters
 */

import { describe, it, expect } from 'vitest';

import {
  formatNumber,
  formatBytes,
  formatDuration,
  truncate,
  wrapText,
  formatResponse,
} from '../../src/utils/formatters.js';

describe('formatters', () => {
  describe('formatNumber', () => {
    it('should format numbers with thousand separators', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
    });

    it('should handle small numbers', () => {
      expect(formatNumber(0)).toBe('0');
      expect(formatNumber(999)).toBe('999');
    });

    it('should handle negative numbers', () => {
      expect(formatNumber(-1000)).toBe('-1,000');
    });
  });

  describe('formatBytes', () => {
    it('should format bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
      expect(formatBytes(500)).toBe('500 Bytes');
    });

    it('should format kilobytes', () => {
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(2048)).toBe('2 KB');
    });

    it('should format megabytes', () => {
      expect(formatBytes(1048576)).toBe('1 MB');
    });

    it('should format gigabytes', () => {
      expect(formatBytes(1073741824)).toBe('1 GB');
    });
  });

  describe('formatDuration', () => {
    it('should format milliseconds', () => {
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(0)).toBe('0ms');
    });

    it('should format seconds', () => {
      expect(formatDuration(1000)).toBe('1.0s');
      expect(formatDuration(5500)).toBe('5.5s');
    });

    it('should format minutes', () => {
      expect(formatDuration(60000)).toBe('1m 0s');
      expect(formatDuration(90000)).toBe('1m 30s');
    });
  });

  describe('truncate', () => {
    it('should not truncate short strings', () => {
      expect(truncate('hello', 10)).toBe('hello');
    });

    it('should truncate long strings', () => {
      expect(truncate('hello world', 8)).toBe('hello...');
    });

    it('should handle exact length', () => {
      expect(truncate('hello', 5)).toBe('hello');
    });
  });

  describe('wrapText', () => {
    it('should wrap long lines', () => {
      const text = 'This is a long line that should be wrapped';
      const result = wrapText(text, 20);
      expect(result).toContain('\n');
    });

    it('should not wrap short lines', () => {
      const text = 'Short';
      const result = wrapText(text, 20);
      expect(result).toBe('Short');
    });

    it('should handle empty string', () => {
      expect(wrapText('', 20)).toBe('');
    });
  });

  describe('formatResponse', () => {
    it('should format bold text', () => {
      const result = formatResponse('This is **bold** text');
      expect(result).toContain('\x1b[1m');
      expect(result).toContain('bold');
    });

    it('should format inline code', () => {
      const result = formatResponse('Use `console.log`');
      expect(result).toContain('\x1b[36m');
      expect(result).toContain('console.log');
    });

    it('should handle text without formatting', () => {
      const text = 'Plain text';
      expect(formatResponse(text)).toBe(text);
    });
  });
});
