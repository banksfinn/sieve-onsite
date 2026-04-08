# shadcn/ui Guide

Detailed patterns for using and extending shadcn/ui in this project.

## Adding Components

```bash
cd frontend
npx shadcn@latest add <component>
```

Components install to `src/components/ui/` as source files you own and can modify.

## cn() Utility

`@/lib/utils` exports `cn()` for merging Tailwind classes conditionally:

```tsx
import { cn } from '@/lib/utils';

<div className={cn("base-classes", isActive && "active-classes", className)} />
```

Always use `cn()` when combining classes or accepting a `className` prop.

## Theming

CSS variables defined in `src/index.css` control all colors:

| Variable | Purpose |
|----------|---------|
| `--background` / `--foreground` | Page background and text |
| `--primary` / `--primary-foreground` | Primary actions |
| `--secondary` / `--secondary-foreground` | Secondary actions |
| `--muted` / `--muted-foreground` | Subtle backgrounds and text |
| `--accent` / `--accent-foreground` | Hover states |
| `--destructive` / `--destructive-foreground` | Danger actions |
| `--card` / `--card-foreground` | Card surfaces |
| `--popover` / `--popover-foreground` | Popover surfaces |
| `--border` | Border color |
| `--input` | Input borders |
| `--ring` | Focus rings |

Dark mode activates via the `dark` class on the root element. Each variable has a dark-mode override.

## Form Handling

For validated forms, use the shadcn/ui form pattern with react-hook-form and zod:

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';

const schema = z.object({ name: z.string().min(1) });

const form = useForm({ resolver: zodResolver(schema) });
```

## Component Composition

shadcn/ui uses sub-component composition (not monolithic prop APIs):

```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Subtitle</CardDescription>
  </CardHeader>
  <CardContent>Body</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>
```

## Icons

Lucide React for all icons. Standard sizing: `h-4 w-4`.

```tsx
import { ChevronRight } from 'lucide-react';
<ChevronRight className="h-4 w-4" />
```

## Component Props Convention

```tsx
interface MyComponentProps {
  /** Description for IDE hints */
  label: string;
  className?: string;
  children?: React.ReactNode;
}
```

Always accept optional `className` for parent styling overrides.

## See Also

- [[Component Library]]
- [[Frontend Architecture]]
