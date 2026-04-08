---
id: component-library
title: Shared Component Library
purpose: Documents all reusable UI components available in the frontend. Check this
  before creating new components to avoid duplication.
scope:
  paths:
  - frontend/src/**
  tags:
  - frontend
  - components
  - shadcn
  - ui
---

# Shared Component Library

## Items

<!-- @item source:llm status:proposed -->
**Button** (`@/components/ui/button`) - Standard button with variants: `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`. Sizes: `default`, `sm`, `lg`, `icon`. Supports `asChild` prop for composition with Radix Slot.

<!-- @item source:llm status:proposed -->
**Card** (`@/components/ui/card`) - Container component with sub-components: `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`. Use for grouping related content with consistent styling.

<!-- @item source:llm status:proposed -->
**AuthCard** (`@/components/auth`) - Centered card layout for authentication pages. Uses composition pattern with `AuthCard.Header`, `AuthCard.Content`, `AuthCard.Footer`. Props: `title`, `description` on Header.

<!-- @item source:llm status:proposed -->
**GoogleLoginButton** (`@/components/auth`) - Google OAuth login button. Props: `onSuccess`, `onError`, `className`. Handles the full OAuth flow including backend API call.

<!-- @item source:llm status:proposed -->
**AppSidebar** (`@/components/common`) - Application sidebar layout with navigation. Props: `navGroups` (array of `{ label, items: [{ title, url, icon }] }`), `header`, `footer`, `children`. Includes `SidebarProvider`, responsive mobile drawer, and toggle trigger. Uses React Router for active state detection.

<!-- @item source:llm status:proposed -->
**Snackbar** (`@/store/components/snackbarSlice`, `@/providers/SnackbarProvider`) - Toast notification system for user feedback. Use `useSnackbar()` hook with methods: `showSuccess(msg)`, `showError(msg)`, `showWarning(msg)`, `showInfo(msg)`, `clearAll()`. Messages auto-dismiss (default 5s) and are prioritized by severity (error > warning > success > info). Supports custom duration as second parameter.

<!-- @item source:llm status:proposed -->
**TagChip** (`@/components/tags`) - Compact inline tag display with colored dot. Props: `tag` (TodoTag), `color?` (string), `className?`. Shows a small colored circle followed by the tag name. Use for inline tag display in lists; use `TagBadge` for larger pill-style badges with optional remove button.

<!-- @item source:user status:active -->
**Before creating components**: 1) Can shadcn do this? 2) Can I compose existing components? 3) Will this be used in 2+ places? 4) Is it generic enough? If mostly "no", keep in page component.
