import { Bell } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Toggle } from '@/components/ui/toggle';
import { cn } from '@/lib/utils';

import { NOTIFICATION_TIMING_OPTIONS } from './NotificationTimingSelector';

interface SlackNotificationChipProps {
    /**
     * Whether Slack notification is enabled
     */
    enabled: boolean;

    /**
     * Callback when enabled state changes
     */
    onEnabledChange: (enabled: boolean) => void;

    /**
     * Notification timing override (null means use default)
     */
    timingOverride: string[] | null;

    /**
     * Callback when timing override changes (null means use default)
     */
    onTimingChange: (timing: string[] | null) => void;

    /**
     * Whether the chip is disabled (e.g., when no due date)
     */
    disabled?: boolean;

    /**
     * Size variant
     */
    size?: 'default' | 'sm';

    /**
     * Additional className
     */
    className?: string;
}

/**
 * Chip component for configuring Slack notifications.
 * - Toggle on the chip to enable/disable
 * - Click the chip to open timing configuration dialog
 */
export function SlackNotificationChip({
    enabled,
    onEnabledChange,
    timingOverride,
    onTimingChange,
    disabled = false,
    size = 'default',
    className,
}: SlackNotificationChipProps) {
    const [dialogOpen, setDialogOpen] = useState(false);
    const [localTiming, setLocalTiming] = useState<string[] | null>(timingOverride);

    const handleChipClick = (e: React.MouseEvent) => {
        // Don't open dialog if disabled or if clicking on the switch
        if (disabled || !enabled) return;
        const target = e.target as HTMLElement;
        if (target.closest('[role="switch"]')) return;
        setLocalTiming(timingOverride);
        setDialogOpen(true);
    };

    const handleToggleEnabled = (checked: boolean) => {
        onEnabledChange(checked);
    };

    const handleTimingToggle = (value: string) => {
        setLocalTiming((prev) => {
            const current = prev ?? [];
            if (current.includes(value)) {
                const newTiming = current.filter((v) => v !== value);
                return newTiming.length === 0 ? null : newTiming;
            } else {
                return [...current, value];
            }
        });
    };

    const handleUseDefault = () => {
        setLocalTiming(null);
    };

    const handleSave = () => {
        onTimingChange(localTiming);
        setDialogOpen(false);
    };

    const getTimingLabel = () => {
        if (!timingOverride || timingOverride.length === 0) {
            return 'Default';
        }
        return `${timingOverride.length} timing${timingOverride.length > 1 ? 's' : ''}`;
    };

    const isUsingDefault = localTiming === null || localTiming.length === 0;
    const isSmall = size === 'sm';

    return (
        <>
            <div
                className={cn(
                    'inline-flex items-center gap-2 rounded-full border transition-colors',
                    isSmall ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
                    enabled
                        ? 'border-primary/30 bg-primary/10 text-primary'
                        : 'border-muted bg-muted/50 text-muted-foreground',
                    !disabled && enabled && 'cursor-pointer hover:bg-primary/20',
                    disabled && 'opacity-50 cursor-not-allowed',
                    className
                )}
                onClick={handleChipClick}
            >
                <Bell className={cn(isSmall ? 'h-3 w-3' : 'h-4 w-4')} />
                <span>Slack</span>
                {enabled && <span className="text-xs opacity-70">({getTimingLabel()})</span>}
                <Switch
                    checked={enabled}
                    onCheckedChange={handleToggleEnabled}
                    disabled={disabled}
                    className={cn(isSmall ? 'scale-75' : 'scale-90')}
                    onClick={(e) => e.stopPropagation()}
                />
            </div>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle>Notification Timing</DialogTitle>
                        <DialogDescription>
                            Choose when you want to be notified. Select multiple options or use your
                            default preferences.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-4 space-y-4">
                        <Button
                            variant={isUsingDefault ? 'default' : 'outline'}
                            onClick={handleUseDefault}
                            className="w-full"
                        >
                            Use My Default Preferences
                        </Button>

                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-background px-2 text-muted-foreground">
                                    Or customize
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                            {NOTIFICATION_TIMING_OPTIONS.map((option) => (
                                <Toggle
                                    key={option.value}
                                    variant="outline"
                                    pressed={localTiming?.includes(option.value) ?? false}
                                    onPressedChange={() => handleTimingToggle(option.value)}
                                    className="justify-start h-auto py-2 px-3"
                                >
                                    {option.label}
                                </Toggle>
                            ))}
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDialogOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    );
}
