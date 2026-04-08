---
id: frontend-patterns
title: Frontend Patterns
purpose: React + TypeScript patterns including component organization, styling with
  shadcn/ui, and state management.
scope:
  paths:
  - frontend/src/**
  tags:
  - frontend
  - react
  - typescript
  - shadcn
---

# Frontend Patterns

## Items

<!-- @item source:user status:active enforcement:strict -->
Use the `@/` path alias for all imports (configured in `tsconfig.json` and `vite.config.ts`). Example: `import { Button } from '@/components/ui/button'`.

<!-- @item source:user status:active enforcement:strict -->
Place page components in `pages/` directory. Place reusable components in `components/`.

<!-- @item source:user status:active enforcement:recommended -->
Custom hooks go in `hooks/`. React context providers go in `providers/`. Router configuration is in `router/`.

<!-- @item source:user status:active enforcement:recommended -->
State management uses Redux Toolkit in `store/`.

<!-- @item source:user status:active enforcement:recommended -->
Theming uses CSS variables in `src/index.css`. Light/dark mode is supported.

<!-- @item source:user status:active -->
**Tech stack**: React 18 + TypeScript, Vite build tooling, shadcn/ui, React Query (TanStack Query) for server state, Redux Toolkit for client state, React Router, Orval for OpenAPI codegen.

<!-- @item source:user status:active -->
**Server state (React Query)**: Use generated Orval hooks from `@/openapi/fullstackBase` for API calls. Example: `const { data, isLoading } = useGetUsers()`.

<!-- @item source:user status:active -->
**Client state (Redux)**: Use typed hooks from `@/store/hooks`. Example: `const dispatch = useAppDispatch(); const state = useAppSelector(selectSomeState);`.

<!-- @item source:user status:active -->
**Environment variables**: Access via `window.ENV` (injected at runtime). For build-time, use `import.meta.env.VITE_*`.

<!-- @item source:user status:active -->
**Component structure**: Define Props interface with JSDoc comments, include `className?` for styling and `children?` if needed. Extend HTML attributes when wrapping native elements.

<!-- @item source:user status:active -->
**Barrel exports**: Each component directory should have `index.ts` for clean imports. Example: `export { AuthCard } from './AuthCard';` enables `import { AuthCard } from '@/components/auth';`.

<!-- @item source:llm status:proposed -->
**API error handling pattern**: Always provide user feedback for backend requests. Use snackbars for transient feedback (success confirmations, errors). Errors are prioritized over other message types and will display first if multiple messages are queued.

<!-- @item source:llm status:proposed -->
**Import paths**: Always use absolute imports with `@/` prefix. The only exception is barrel export files (`index.ts`) which should use `./` to re-export siblings. Never use `../` relative imports—convert these to absolute paths. Example: `import { RootState } from '@/store/store'` not `import { RootState } from '../store'`.
