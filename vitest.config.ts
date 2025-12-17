import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Test environment
    environment: 'node',

    // Global test setup
    globals: true,

    // Test file patterns
    include: ['tests/**/*.{test,spec}.ts'],
    exclude: ['node_modules', 'dist', '.git'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'lcov', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.ts'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.ts',
        'src/**/index.ts',
        'src/types/**',
        'src/cli.ts',
      ],
      // Coverage thresholds
      thresholds: {
        global: {
          statements: 70,
          branches: 60,
          functions: 70,
          lines: 70,
        },
      },
      clean: true,
    },

    // Test timeouts
    testTimeout: 10000,
    hookTimeout: 10000,

    // Reporter configuration
    reporters: ['default'],

    // Setup files
    setupFiles: ['./tests/setup.ts'],

    // Mock reset
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,
  },
});
