import { cn } from '@/lib/utils';
import type { TodoTag } from '@/openapi/fullstackBase';

interface TagChipProps {
    /** The tag to display */
    tag: TodoTag;
    /** Optional color override (from user preferences) */
    color?: string | null;
    /** Additional className */
    className?: string;
}

/**
 * Compact tag chip for inline display in todo lists.
 * Shows a small colored dot with the tag name.
 */
export function TagChip({ tag, color, className }: TagChipProps) {
    // Use provided color or default to a neutral gray
    const dotColor = color || '#9ca3af';

    return (
        <span
            className={cn(
                'inline-flex items-center gap-1 text-xs text-muted-foreground',
                className
            )}
        >
            <span
                className="h-2 w-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: dotColor }}
            />
            <span className="truncate">{tag.name}</span>
        </span>
    );
}
