/**
 * Test Setup File
 *
 * This file runs before all tests and sets up the test environment.
 */

import { beforeAll, afterAll, afterEach, vi } from 'vitest';

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.CI = process.env.CI || 'false';

// Mock console methods in tests to reduce noise
beforeAll(() => {
  // Suppress console output during tests unless explicitly needed
  if (process.env.DEBUG_TESTS !== 'true') {
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'debug').mockImplementation(() => {});
  }
});

afterAll(() => {
  vi.restoreAllMocks();
});

afterEach(() => {
  vi.clearAllMocks();
});

// Global test utilities
declare global {
  var testUtils: {
    createMockResponse: (data: unknown) => Response;
    delay: (ms: number) => Promise<void>;
  };
}

globalThis.testUtils = {
  /**
   * Create a mock Response object for fetch testing
   */
  createMockResponse: (data: unknown): Response => {
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  },

  /**
   * Promise-based delay utility
   */
  delay: (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  },
};
