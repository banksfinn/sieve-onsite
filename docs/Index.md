# Sieve Onsite - Documentation Vault

Full-stack application for GTM-Engineering video sample review collaboration. Built with [[Backend Architecture|FastAPI]] + [[Frontend Architecture|React/TypeScript]], deployed via [[Infrastructure|Docker Compose]].

## Architecture

- [[Architecture Overview]] - System-level view of all components
- [[Backend Architecture]] - FastAPI gateway, libs, and tools
- [[Frontend Architecture]] - React + TypeScript SPA
- [[Infrastructure]] - Docker Compose, ports, and deployment

## Clients & Services

- [[DatabaseClient]] - Async SQLAlchemy engine and session management
- [[BaseEntityStore]] - Generic CRUD store with pagination and sorting
- [[UserStore]] - User-specific data access
- [[GCSClient]] - Google Cloud Storage operations
- [[GoogleOAuthClient]] - Google OAuth flow and token exchange

## Data Models

- [[Data Model Overview]] - Entity system and type hierarchy
- [[BaseEntity]] - Shared fields and base classes
- [[User Model]] - User entity with notification preferences

## API

- [[API Overview]] - Route registration and conventions
- [[Authentication Routes]] - Google OAuth login endpoint
- [[User Routes]] - User profile and preferences

## Design Decisions

- [[Cookie-Based JWT Auth]] - Why cookies over Authorization headers
- [[Async-First Backend]] - asyncpg + SQLAlchemy 2.0 async
- [[Editable Library Installs]] - Monorepo lib architecture
- [[OpenAPI Type Generation]] - Orval codegen for frontend types
- [[Redux Plus React Query]] - Dual state management strategy
- [[Blueprint Pattern]] - Entity definition convention

## Frontend

- [[Provider Stack]] - App.tsx wrapper hierarchy
- [[Auth Flow]] - Session initialization and route protection
- [[State Management]] - Redux Toolkit + React Query
- [[Component Library]] - shadcn/ui + custom components

## Reference

- [[Project Requirements]] - Original problem statement and rubric
