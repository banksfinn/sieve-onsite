---
id: shadcn-ui
title: shadcn/ui Component Guidelines
purpose: Guidelines for using and extending shadcn/ui components, theming, and form
  handling.
scope:
  paths:
  - frontend/src/**
  tags:
  - frontend
  - shadcn
  - ui
  - components
  - tailwind
---

# shadcn/ui Component Guidelines

## Items

<!-- @item source:user status:active -->
**Adding components**: Run `npx shadcn@latest add <component>` from the `frontend/` directory. Components are installed to `src/components/ui/`.

<!-- @item source:user status:active -->
**cn() utility**: Use `cn()` from `@/lib/utils` to merge Tailwind classes conditionally. Example: `cn('base-class', isActive && 'active-class', className)`.

<!-- @item source:user status:active -->
**Theming**: Uses CSS variables in `src/index.css`. Semantic tokens: `background/foreground`, `primary/primary-foreground`, `secondary`, `muted`, `accent`, `destructive`, `card`, `popover`, `border`, `input`, `ring`.

<!-- @item source:user status:active -->
**Component composition**: Use sub-components for complex UI. Example: `<Card><CardHeader><CardTitle>...</CardTitle></CardHeader><CardContent>...</CardContent></Card>`.

<!-- @item source:user status:active -->
**Form handling**: Use shadcn/ui form components with react-hook-form and zod. Add via `npx shadcn@latest add form input label`. Use FormField, FormItem, FormLabel, FormControl, FormMessage for validation.

<!-- @item source:user status:active -->
**Icons**: Use Lucide React for icons (already installed). Example: `import { Search, Menu } from 'lucide-react'`. Standard sizing: `className="h-4 w-4"`.

<!-- @item source:user status:active -->
**Dark mode**: Supported via `dark` class on root element. CSS variables automatically switch. Toggle with `document.documentElement.classList.toggle('dark')`.
