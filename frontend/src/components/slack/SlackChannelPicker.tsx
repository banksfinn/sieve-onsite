import { Check, ChevronsUpDown, Hash, Lock, X } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import type { SlackChannel } from '@/openapi/fullstackBase';
import { useSearchSlackChannels } from '@/openapi/fullstackBase';

interface SlackChannelPickerProps {
    /**
     * Currently selected channel (id and name)
     */
    value: { id: string; name: string } | null;

    /**
     * Callback when channel is selected or cleared
     */
    onChange: (channel: { id: string; name: string } | null) => void;

    /**
     * Placeholder text when no channel is selected
     */
    placeholder?: string;

    /**
     * Additional className for the trigger button
     */
    className?: string;

    /**
     * Whether the picker is disabled
     */
    disabled?: boolean;
}

/**
 * Combobox component for searching and selecting Slack channels.
 * Searches channels via the backend API as the user types.
 */
export function SlackChannelPicker({
    value,
    onChange,
    placeholder = 'Select channel...',
    className,
    disabled = false,
}: SlackChannelPickerProps) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');

    // Only search when there's at least 2 characters
    const { data: channelsResponse, isLoading } = useSearchSlackChannels(
        { q: search },
        { query: { enabled: search.length >= 2 } }
    );
    const channels = (channelsResponse as { channels: SlackChannel[] } | undefined)?.channels ?? [];

    const handleSelect = (channel: SlackChannel) => {
        onChange({ id: channel.id, name: channel.name });
        setOpen(false);
        setSearch('');
    };

    const handleClear = (e: React.MouseEvent) => {
        e.stopPropagation();
        onChange(null);
    };

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    disabled={disabled}
                    className={cn('w-full justify-between', className)}
                >
                    <span className="flex items-center gap-2 truncate">
                        {value ? (
                            <>
                                <Hash className="h-4 w-4 shrink-0 text-muted-foreground" />
                                {value.name}
                            </>
                        ) : (
                            <span className="text-muted-foreground">{placeholder}</span>
                        )}
                    </span>
                    <span className="flex items-center">
                        {value && (
                            <X
                                className="h-4 w-4 shrink-0 opacity-50 hover:opacity-100 mr-1"
                                onClick={handleClear}
                            />
                        )}
                        <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
                    </span>
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[300px] p-0" align="start">
                <Command shouldFilter={false}>
                    <CommandInput
                        placeholder="Search channels..."
                        value={search}
                        onValueChange={setSearch}
                    />
                    <CommandList>
                        {search.length < 2 ? (
                            <CommandEmpty>Type to search channels...</CommandEmpty>
                        ) : isLoading ? (
                            <CommandEmpty>Loading...</CommandEmpty>
                        ) : channels.length === 0 ? (
                            <CommandEmpty>No channels found.</CommandEmpty>
                        ) : (
                            <CommandGroup>
                                {channels.map((channel) => (
                                    <CommandItem
                                        key={channel.id}
                                        value={channel.id}
                                        onSelect={() => handleSelect(channel)}
                                        className="flex items-center gap-2"
                                    >
                                        {channel.is_private ? (
                                            <Lock className="h-4 w-4 text-muted-foreground" />
                                        ) : (
                                            <Hash className="h-4 w-4 text-muted-foreground" />
                                        )}
                                        <span className="flex-1">{channel.name}</span>
                                        {channel.num_members !== null &&
                                            channel.num_members !== undefined && (
                                                <span className="text-xs text-muted-foreground">
                                                    {channel.num_members} members
                                                </span>
                                            )}
                                        <Check
                                            className={cn(
                                                'h-4 w-4',
                                                value?.id === channel.id
                                                    ? 'opacity-100'
                                                    : 'opacity-0'
                                            )}
                                        />
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        )}
                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    );
}
