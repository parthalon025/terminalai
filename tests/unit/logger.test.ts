/**
 * Unit tests for the logger module
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

import {
  setVerbose,
  isVerbose,
  debug,
  info,
  warn,
  error,
  success,
  output,
  createLogger,
} from '../../src/utils/logger.js';

describe('logger', () => {
  beforeEach(() => {
    setVerbose(false);
    vi.restoreAllMocks();
  });

  describe('setVerbose / isVerbose', () => {
    it('should default to false', () => {
      setVerbose(false);
      expect(isVerbose()).toBe(false);
    });

    it('should set verbose mode', () => {
      setVerbose(true);
      expect(isVerbose()).toBe(true);
    });
  });

  describe('debug', () => {
    it('should not output when verbose is false', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      setVerbose(false);
      debug('test message');
      expect(spy).not.toHaveBeenCalled();
    });

    it('should output when verbose is true', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      setVerbose(true);
      debug('test message');
      expect(spy).toHaveBeenCalled();
    });
  });

  describe('info', () => {
    it('should write to stdout', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      info('test message');
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0]?.[0]).toContain('INFO');
    });
  });

  describe('warn', () => {
    it('should write to stdout', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      warn('test message');
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0]?.[0]).toContain('WARN');
    });
  });

  describe('error', () => {
    it('should write to stderr', () => {
      const spy = vi.spyOn(process.stderr, 'write').mockImplementation(() => true);
      error('test message');
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0]?.[0]).toContain('ERROR');
    });
  });

  describe('success', () => {
    it('should write to stdout with checkmark', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      success('test message');
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0]?.[0]).toContain('✓');
    });
  });

  describe('output', () => {
    it('should write to stdout without formatting', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      output('test message');
      expect(spy).toHaveBeenCalledWith('test message\n');
    });
  });

  describe('createLogger', () => {
    it('should create a logger with prefix', () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
      const logger = createLogger('TestModule');
      logger.info('test');
      expect(spy.mock.calls[0]?.[0]).toContain('TestModule');
    });

    it('should have all logging methods', () => {
      const logger = createLogger('Test');
      expect(typeof logger.debug).toBe('function');
      expect(typeof logger.info).toBe('function');
      expect(typeof logger.warn).toBe('function');
      expect(typeof logger.error).toBe('function');
    });
  });
});
