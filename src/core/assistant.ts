/**
 * Core AI Assistant functionality
 */

import type { Config, Message, AIResponse } from '../types/index.js';
import { debug } from '../utils/logger.js';

/**
 * AI Assistant class for handling conversations
 */
export class Assistant {
  private config: Config;
  private conversationHistory: Message[] = [];

  constructor(config: Config) {
    this.config = config;
  }

  /**
   * Get the current configuration
   */
  getConfig(): Config {
    return { ...this.config };
  }

  /**
   * Add a system message to set context
   */
  setSystemPrompt(prompt: string): void {
    // Remove existing system message if any
    this.conversationHistory = this.conversationHistory.filter(msg => msg.role !== 'system');
    // Add new system message at the beginning
    this.conversationHistory.unshift({
      role: 'system',
      content: prompt,
    });
    debug('System prompt set');
  }

  /**
   * Send a message and get a response
   */
  async chat(userMessage: string): Promise<AIResponse> {
    // Add user message to history
    this.conversationHistory.push({
      role: 'user',
      content: userMessage,
    });

    debug(`Processing message: ${userMessage.substring(0, 50)}...`);

    // Simulate AI response (actual implementation would call AI API)
    const response = await this.generateResponse(userMessage);

    // Add assistant response to history
    this.conversationHistory.push({
      role: 'assistant',
      content: response.content,
    });

    return response;
  }

  /**
   * Generate a response (placeholder for actual AI integration)
   */
  private async generateResponse(message: string): Promise<AIResponse> {
    // This is a placeholder that simulates an AI response
    // In production, this would call the OpenAI API or similar

    const responses: Record<string, string> = {
      help: 'I can help you with terminal commands, coding questions, and general assistance. Just ask!',
      hello: 'Hello! How can I assist you today?',
      default: `I received your message: "${message}". This is a placeholder response. Configure your API key to enable AI responses.`,
    };

    const lowerMessage = message.toLowerCase();
    const defaultResponse = `I received your message: "${message}". This is a placeholder response. Configure your API key to enable AI responses.`;
    let content: string = defaultResponse;

    if (lowerMessage.includes('help')) {
      content = responses['help'] ?? defaultResponse;
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      content = responses['hello'] ?? defaultResponse;
    }

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 100));

    return {
      content,
      tokensUsed: Math.ceil(content.length / 4),
      model: this.config.model,
    };
  }

  /**
   * Get conversation history
   */
  getHistory(): Message[] {
    return [...this.conversationHistory];
  }

  /**
   * Clear conversation history
   */
  clearHistory(): void {
    const systemMessage = this.conversationHistory.find(msg => msg.role === 'system');
    this.conversationHistory = systemMessage ? [systemMessage] : [];
    debug('Conversation history cleared');
  }

  /**
   * Get the number of messages in history
   */
  getHistoryLength(): number {
    return this.conversationHistory.length;
  }
}

/**
 * Create a new assistant instance
 */
export function createAssistant(config: Config): Assistant {
  return new Assistant(config);
}
