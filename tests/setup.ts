/**
 * Test Setup File
 *
 * This file runs before all tests and sets up the test environment.
 */

import { beforeAll, afterAll, afterEach, vi } from 'vitest';

// Set test environment variables
process.env['NODE_ENV'] = 'test';
process.env['CI'] = process.env['CI'] ?? 'false';

// Mock console methods in tests to reduce noise
beforeAll(() => {
  // Suppress console output during tests unless explicitly needed
  if (process.env['DEBUG_TESTS'] !== 'true') {
    vi.spyOn(process.stdout, 'write').mockImplementation(() => true);
    vi.spyOn(process.stderr, 'write').mockImplementation(() => true);
  }
});

afterAll(() => {
  vi.restoreAllMocks();
});

afterEach(() => {
  vi.clearAllMocks();
});
