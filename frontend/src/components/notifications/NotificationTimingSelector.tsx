import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

/**
 * Available notification timing options
 */
export const NOTIFICATION_TIMING_OPTIONS = [
    { value: 'at_due_time', label: 'At due time' },
    { value: '15_minutes_before', label: '15 minutes before' },
    { value: '30_minutes_before', label: '30 minutes before' },
    { value: '60_minutes_before', label: '1 hour before' },
    { value: 'morning_of', label: 'Morning of (9 AM)' },
    { value: 'night_before', label: 'Night before (8 PM)' },
] as const;

export type NotificationTimingValue = (typeof NOTIFICATION_TIMING_OPTIONS)[number]['value'];

interface NotificationTimingSelectorProps {
    /**
     * Currently selected timing values
     */
    value: string[];

    /**
     * Callback when selection changes
     */
    onChange: (value: string[]) => void;

    /**
     * Additional className for the container
     */
    className?: string;

    /**
     * Whether the selector is disabled
     */
    disabled?: boolean;
}

/**
 * Multi-select component for notification timing options.
 * Allows users to select when they want to be notified about todos.
 */
export function NotificationTimingSelector({
    value,
    onChange,
    className,
    disabled = false,
}: NotificationTimingSelectorProps) {
    const handleToggle = (optionValue: string) => {
        if (disabled) return;

        if (value.includes(optionValue)) {
            onChange(value.filter((v) => v !== optionValue));
        } else {
            onChange([...value, optionValue]);
        }
    };

    return (
        <div className={cn('space-y-2', className)}>
            {NOTIFICATION_TIMING_OPTIONS.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                    <Checkbox
                        id={`timing-${option.value}`}
                        checked={value.includes(option.value)}
                        onCheckedChange={() => handleToggle(option.value)}
                        disabled={disabled}
                    />
                    <Label
                        htmlFor={`timing-${option.value}`}
                        className={cn(
                            'text-sm font-normal cursor-pointer',
                            disabled && 'cursor-not-allowed opacity-50'
                        )}
                    >
                        {option.label}
                    </Label>
                </div>
            ))}
        </div>
    );
}
