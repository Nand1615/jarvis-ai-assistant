# System Architecture

This document describes the high-level architecture of the Jarvis AI Assistant.

## High-Level Flow

User (Voice / Text)
↓
Speech-to-Text (if voice)
↓
NLP Preprocessing
↓
Intent Analyzer
↓
Core Router
├── Memory Manager
│ ├── Short-Term Memory
│ └── Long-Term Memory
├── ML / LLM Handler
└── Action Executor
↓
Response Generator
↓
Text-to-Speech / UI Output


## Design Notes

- The system follows a modular architecture with clear separation of concerns.
- Each component can be modified or replaced independently.
- Memory and response generation are decoupled from intent analysis.
- LLM integration is abstracted to allow multiple backends.
