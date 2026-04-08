import * as React from 'react';
import { format, setHours, setMinutes } from 'date-fns';
import { formatInTimeZone } from 'date-fns-tz';
import { CalendarIcon, X } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface DatePickerProps {
    date: Date | undefined;
    onDateChange: (date: Date | undefined) => void;
    placeholder?: string;
    className?: string;
    disabled?: boolean;
}

/** Get user's IANA timezone string */
export function getUserTimezone(): string {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/** Get short timezone abbreviation (e.g., "PST", "EST") */
function getTimezoneAbbreviation(): string {
    const now = new Date();
    const timezone = getUserTimezone();
    try {
        return formatInTimeZone(now, timezone, 'zzz');
    } catch {
        // Fallback to offset format if timezone name unavailable
        const offset = -now.getTimezoneOffset();
        const hours = Math.floor(Math.abs(offset) / 60);
        const sign = offset >= 0 ? '+' : '-';
        return `UTC${sign}${hours}`;
    }
}

/** Convert 24-hour to 12-hour format */
function to12Hour(hour24: number): { hour: number; period: 'AM' | 'PM' } {
    if (hour24 === 0) return { hour: 12, period: 'AM' };
    if (hour24 === 12) return { hour: 12, period: 'PM' };
    if (hour24 > 12) return { hour: hour24 - 12, period: 'PM' };
    return { hour: hour24, period: 'AM' };
}

/** Convert 12-hour to 24-hour format */
function to24Hour(hour12: number, period: 'AM' | 'PM'): number {
    if (period === 'AM') {
        return hour12 === 12 ? 0 : hour12;
    }
    return hour12 === 12 ? 12 : hour12 + 12;
}

export function DatePicker({
    date,
    onDateChange,
    placeholder = 'Pick a date',
    className,
    disabled,
}: DatePickerProps) {
    const [open, setOpen] = React.useState(false);

    const hours24 = date ? date.getHours() : 9; // Default to 9 AM
    const minutes = date ? date.getMinutes() : 0;
    const { hour: hour12, period } = to12Hour(hours24);

    const handleDateSelect = (newDate: Date | undefined) => {
        if (newDate) {
            // Preserve existing time when selecting a new date
            const withTime = setMinutes(setHours(newDate, hours24), minutes);
            onDateChange(withTime);
        } else {
            onDateChange(undefined);
        }
    };

    const handleHourChange = (value: string) => {
        const numValue = parseInt(value, 10);
        if (isNaN(numValue)) return;

        const currentDate = date || new Date();
        const hour24 = to24Hour(numValue, period);
        const newDate = setHours(currentDate, hour24);
        onDateChange(newDate);
    };

    const handleMinuteChange = (value: string) => {
        const numValue = parseInt(value, 10);
        if (isNaN(numValue)) return;

        const currentDate = date || new Date();
        const newDate = setMinutes(currentDate, numValue);
        onDateChange(newDate);
    };

    const handlePeriodChange = (newPeriod: 'AM' | 'PM') => {
        const currentDate = date || new Date();
        const hour24 = to24Hour(hour12, newPeriod);
        const newDate = setHours(currentDate, hour24);
        onDateChange(newDate);
    };

    const timezoneAbbr = getTimezoneAbbreviation();

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    className={cn(
                        'justify-start text-left font-normal',
                        !date && 'text-muted-foreground',
                        className
                    )}
                    disabled={disabled}
                >
                    <CalendarIcon className="mr-2 h-4 w-4 shrink-0" />
                    {date ? (
                        <span className="truncate">{format(date, 'PPP p')}</span>
                    ) : (
                        <span>{placeholder}</span>
                    )}
                    {date && (
                        <X
                            className="ml-auto h-4 w-4 shrink-0 hover:text-destructive"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDateChange(undefined);
                            }}
                        />
                    )}
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
                <Calendar mode="single" selected={date} onSelect={handleDateSelect} />
                <div className="border-t p-3 space-y-2">
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground w-10">Time:</span>
                        <Select value={hour12.toString()} onValueChange={handleHourChange}>
                            <SelectTrigger className="w-[70px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {[12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((h) => (
                                    <SelectItem key={h} value={h.toString()}>
                                        {h}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <span className="text-muted-foreground">:</span>
                        <Select value={minutes.toString()} onValueChange={handleMinuteChange}>
                            <SelectTrigger className="w-[70px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].map((m) => (
                                    <SelectItem key={m} value={m.toString()}>
                                        {m.toString().padStart(2, '0')}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select
                            value={period}
                            onValueChange={(v) => handlePeriodChange(v as 'AM' | 'PM')}
                        >
                            <SelectTrigger className="w-[70px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="AM">AM</SelectItem>
                                <SelectItem value="PM">PM</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="text-xs text-muted-foreground text-center">
                        Timezone: {timezoneAbbr}
                    </div>
                </div>
            </PopoverContent>
        </Popover>
    );
}
