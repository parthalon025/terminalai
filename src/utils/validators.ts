/**
 * Input validation utilities
 */

/**
 * Check if a string is empty or only whitespace
 */
export function isEmpty(value: string | undefined | null): boolean {
  return value === undefined || value === null || value.trim().length === 0;
}

/**
 * Check if a value is a valid positive integer
 */
export function isPositiveInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value) && value > 0;
}

/**
 * Check if a value is within a numeric range
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/**
 * Validate temperature value (0.0 to 2.0)
 */
export function isValidTemperature(value: number): boolean {
  return isInRange(value, 0, 2);
}

/**
 * Validate max tokens value
 */
export function isValidMaxTokens(value: number): boolean {
  return isPositiveInteger(value) && value <= 128000;
}

/**
 * Validate model name format
 */
export function isValidModelName(model: string): boolean {
  if (isEmpty(model)) {
    return false;
  }
  // Allow common model name patterns
  const modelPattern = /^[a-zA-Z0-9][\w\-.]*$/;
  return modelPattern.test(model);
}

/**
 * Sanitize user input by trimming and removing control characters
 */
export function sanitizeInput(input: string): string {
  // Remove control characters except newlines and tabs
  // eslint-disable-next-line no-control-regex
  return input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '').trim();
}

/**
 * Validate and sanitize a prompt
 */
export function validatePrompt(prompt: string): {
  valid: boolean;
  sanitized: string;
  error?: string;
} {
  if (isEmpty(prompt)) {
    return { valid: false, sanitized: '', error: 'Prompt cannot be empty' };
  }

  const sanitized = sanitizeInput(prompt);

  if (sanitized.length === 0) {
    return { valid: false, sanitized: '', error: 'Prompt contains no valid content' };
  }

  if (sanitized.length > 100000) {
    return { valid: false, sanitized: '', error: 'Prompt exceeds maximum length' };
  }

  return { valid: true, sanitized };
}
