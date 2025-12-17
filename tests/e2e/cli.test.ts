/**
 * End-to-end tests for the CLI
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

import { createProgram, runCLI } from '../../src/cli/commands.js';

describe('CLI End-to-End', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    process.exitCode = undefined;
  });

  describe('Program Creation', () => {
    it('should create a commander program', () => {
      const program = createProgram();
      expect(program.name()).toBe('terminalai');
    });

    it('should have correct version', () => {
      const program = createProgram();
      expect(program.version()).toBe('0.1.0');
    });

    it('should have required options', () => {
      const program = createProgram();
      const options = program.options;

      const optionNames = options.map(opt => opt.long);
      expect(optionNames).toContain('--interactive');
      expect(optionNames).toContain('--verbose');
      expect(optionNames).toContain('--model');
    });
  });

  describe('CLI Execution', () => {
    it('should handle single prompt', async () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['Hello'], { verbose: false });

      expect(spy).toHaveBeenCalled();
    });

    it('should handle verbose mode', async () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['Test prompt'], { verbose: true });

      // Should have additional verbose output
      expect(spy).toHaveBeenCalled();
    });

    it('should handle help command', async () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['/help'], {});

      expect(spy).toHaveBeenCalled();
      const output = spy.mock.calls.map(c => c[0]).join('');
      expect(output).toContain('Available commands');
    });

    it('should handle version command', async () => {
      const spy = vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['/version'], {});

      expect(spy).toHaveBeenCalled();
      const output = spy.mock.calls.map(c => c[0]).join('');
      expect(output).toContain('TerminalAI');
    });

    it('should set exit code on error', async () => {
      vi.spyOn(process.stderr, 'write').mockImplementation(() => true);
      vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['/unknown'], {});

      expect(process.exitCode).toBe(1);
    });
  });

  describe('CLI Options', () => {
    it('should accept model option', async () => {
      vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['Test'], { model: 'gpt-3.5-turbo' });

      // Should not throw
    });

    it('should accept maxTokens option', async () => {
      vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['Test'], { maxTokens: 2048 });

      // Should not throw
    });
  });

  describe('Error Handling', () => {
    it('should handle empty input gracefully', async () => {
      const stderrSpy = vi.spyOn(process.stderr, 'write').mockImplementation(() => true);

      // Empty array simulates no prompt provided
      // In the actual CLI this would trigger interactive mode
      // but we can test the error path
      await runCLI([], { interactive: false });

      // Should either go to interactive mode or handle gracefully
    });

    it('should handle whitespace-only input', async () => {
      vi.spyOn(process.stderr, 'write').mockImplementation(() => true);
      vi.spyOn(process.stdout, 'write').mockImplementation(() => true);

      await runCLI(['   '], {});

      // Should handle gracefully (either error or process as empty)
    });
  });
});
