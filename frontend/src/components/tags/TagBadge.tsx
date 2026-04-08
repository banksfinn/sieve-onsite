import { X } from 'lucide-react';

import { cn } from '@/lib/utils';
import type { TodoTag } from '@/openapi/fullstackBase';

interface TagBadgeProps {
    /** The tag to display */
    tag: TodoTag;
    /** Optional color override (from user preferences) */
    color?: string | null;
    /** Callback when remove button is clicked */
    onRemove?: () => void;
    /** Additional className */
    className?: string;
}

/**
 * Displays a tag as a colored badge/pill with optional remove button.
 */
export function TagBadge({ tag, color, onRemove, className }: TagBadgeProps) {
    // Use provided color or default to a neutral gray
    const backgroundColor = color || '#e5e7eb';

    // Determine text color based on background brightness
    const textColor = isLightColor(backgroundColor) ? '#1f2937' : '#ffffff';

    return (
        <span
            className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                className
            )}
            style={{ backgroundColor, color: textColor }}
        >
            {tag.icon && <span>{tag.icon}</span>}
            <span>{tag.name}</span>
            {onRemove && (
                <button
                    type="button"
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove();
                    }}
                    className="ml-0.5 hover:opacity-70 focus:outline-none"
                    aria-label={`Remove ${tag.name} tag`}
                >
                    <X className="h-3 w-3" />
                </button>
            )}
        </span>
    );
}

/**
 * Determines if a hex color is light (for contrast calculation).
 */
function isLightColor(hexColor: string): boolean {
    // Remove # if present
    const hex = hexColor.replace('#', '');

    // Parse RGB values
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    // Calculate luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    return luminance > 0.5;
}
