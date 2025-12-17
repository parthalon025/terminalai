#!/usr/bin/env node
/**
 * TerminalAI CLI Entry Point
 */

import { createProgram } from './cli/commands.js';

const program = createProgram();
program.parse();
