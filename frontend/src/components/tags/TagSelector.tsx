import { Check, ChevronsUpDown, Plus } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
} from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import type { Tag } from '@/openapi/fullstackBase';
import { useGetTags } from '@/openapi/fullstackBase';

import { TagBadge } from './TagBadge';

interface TagSelectorProps {
    /** Currently selected tag IDs */
    selectedTagIds: number[];
    /** Callback when selection changes */
    onChange: (tagIds: number[]) => void;
    /** Callback to create a new tag */
    onCreateTag?: (name: string) => void;
    /** Placeholder text */
    placeholder?: string;
    /** Additional className */
    className?: string;
}

/**
 * Multi-select dropdown for picking tags on todos.
 */
export function TagSelector({
    selectedTagIds,
    onChange,
    onCreateTag,
    placeholder = 'Select tags...',
    className,
}: TagSelectorProps) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');

    const { data: tagsResponse } = useGetTags();
    const tags = (tagsResponse as { entities: Tag[] } | undefined)?.entities ?? [];

    const selectedTags = tags.filter((tag) => selectedTagIds.includes(tag.id));

    const toggleTag = (tagId: number) => {
        if (selectedTagIds.includes(tagId)) {
            onChange(selectedTagIds.filter((id) => id !== tagId));
        } else {
            onChange([...selectedTagIds, tagId]);
        }
    };

    const removeTag = (tagId: number) => {
        onChange(selectedTagIds.filter((id) => id !== tagId));
    };

    // Check if search matches any existing tag (case-insensitive)
    const searchMatchesExisting = tags.some(
        (tag) => tag.name.toLowerCase() === search.toLowerCase()
    );

    return (
        <div className={cn('flex flex-col gap-2', className)}>
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="justify-between h-auto min-h-9"
                    >
                        {selectedTags.length === 0 ? (
                            <span className="text-muted-foreground">{placeholder}</span>
                        ) : (
                            <div className="flex flex-wrap gap-1">
                                {selectedTags.map((tag) => {
                                    const member = tag.members?.find((m) => m.user_id);
                                    return (
                                        <TagBadge
                                            key={tag.id}
                                            tag={tag}
                                            color={member?.color}
                                            onRemove={() => removeTag(tag.id)}
                                        />
                                    );
                                })}
                            </div>
                        )}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[300px] p-0" align="start">
                    <Command>
                        <CommandInput
                            placeholder="Search tags..."
                            value={search}
                            onValueChange={setSearch}
                        />
                        <CommandList>
                            <CommandEmpty>
                                {search && !searchMatchesExisting ? (
                                    <div className="py-2 text-center text-sm">
                                        No tag found.
                                        {onCreateTag && (
                                            <Button
                                                variant="link"
                                                className="px-1"
                                                onClick={() => {
                                                    onCreateTag(search);
                                                    setSearch('');
                                                }}
                                            >
                                                <Plus className="h-3 w-3 mr-1" />
                                                Create "{search}"
                                            </Button>
                                        )}
                                    </div>
                                ) : (
                                    'No tags found.'
                                )}
                            </CommandEmpty>
                            <CommandGroup>
                                {tags.map((tag) => {
                                    const isSelected = selectedTagIds.includes(tag.id);
                                    const member = tag.members?.find((m) => m.user_id);
                                    return (
                                        <CommandItem
                                            key={tag.id}
                                            value={tag.name}
                                            onSelect={() => toggleTag(tag.id)}
                                        >
                                            <Check
                                                className={cn(
                                                    'mr-2 h-4 w-4',
                                                    isSelected ? 'opacity-100' : 'opacity-0'
                                                )}
                                            />
                                            <TagBadge tag={tag} color={member?.color} />
                                        </CommandItem>
                                    );
                                })}
                            </CommandGroup>
                            {onCreateTag && search && !searchMatchesExisting && tags.length > 0 && (
                                <>
                                    <CommandSeparator />
                                    <CommandGroup>
                                        <CommandItem
                                            onSelect={() => {
                                                onCreateTag(search);
                                                setSearch('');
                                            }}
                                        >
                                            <Plus className="mr-2 h-4 w-4" />
                                            Create "{search}"
                                        </CommandItem>
                                    </CommandGroup>
                                </>
                            )}
                        </CommandList>
                    </Command>
                </PopoverContent>
            </Popover>
        </div>
    );
}
