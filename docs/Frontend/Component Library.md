# Component Library

UI components built on shadcn/ui primitives + Tailwind CSS.

## shadcn/ui Components

Located in `frontend/src/components/ui/`. Installed via:

```bash
npx shadcn@latest add <component>
```

Available components:

| Component | Variants/Notes |
|-----------|---------------|
| Button | default, destructive, outline, secondary, ghost, link |
| Card | CardHeader, CardTitle, CardDescription, CardContent, CardFooter |
| Input | Standard text input |
| Label | Form labels |
| Textarea | Multi-line input |
| Select | Dropdown select |
| Dialog | Modal dialogs |
| Sheet | Slide-out panels |
| Popover | Positioned popover |
| Tooltip | Hover tooltips |
| Checkbox | Boolean input |
| Switch | Toggle switch |
| Toggle | Pressed/unpressed state |
| Badge | Status indicators |
| Separator | Visual divider |
| Sidebar | SidebarProvider, SidebarContent, SidebarTrigger, etc. |
| DatePicker | Date selection |
| Calendar | Calendar display |
| ScrollArea | Custom scrollbar |
| Collapsible | Expand/collapse sections |
| Command | Command palette / search |

## Custom Components

### AuthCard

`frontend/src/components/auth/AuthCard.tsx`

Centered card layout for authentication pages. Uses Card primitives with consistent styling.

### GoogleLoginButton

`frontend/src/components/auth/GoogleLoginButton.tsx`

Wrapper around `@react-oauth/google` that handles:
- Google One Tap credential callback
- Calling the [[Authentication Routes|login endpoint]]
- Success/error feedback via snackbar

### AppSidebar

`frontend/src/components/common/AppSidebar.tsx`

Main application layout with:
- Responsive sidebar navigation
- Active route detection
- Logout button
- User display

## Styling

- **Tailwind CSS**: Utility-first styling
- **`cn()` utility**: `frontend/src/lib/utils.ts` - merges Tailwind classes conditionally
- **CSS variables**: Defined in `index.css` for theming (light/dark mode support)
- **Icons**: Lucide React icon library

## Adding Components

1. Check if a shadcn/ui component exists: `npx shadcn@latest add <name>`
2. If custom, create in `components/` organized by domain
3. Use `cn()` for conditional classes
4. Follow existing patterns for consistency

## See Also

- [[Frontend Architecture]]
- [[Auth Flow]]
