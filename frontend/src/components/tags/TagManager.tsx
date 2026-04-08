import { Plus, Settings2, Share2, Trash2, Users } from 'lucide-react';
import { useState } from 'react';

import { SlackChannelPicker } from '@/components/slack';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import type { Tag, User } from '@/openapi/fullstackBase';
import {
    getGetTagsQueryKey,
    useAddTagMember,
    useCreateTag,
    useDeleteTag,
    useGetAllUsers,
    useGetTags,
    useRemoveTagMember,
    useUpdateMyTagPreferences,
    useUpdateTag,
} from '@/openapi/fullstackBase';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { useQueryClient } from '@tanstack/react-query';

import { TagBadge } from './TagBadge';

// Predefined color options
const COLOR_OPTIONS = [
    { label: 'Red', value: '#ef4444' },
    { label: 'Orange', value: '#f97316' },
    { label: 'Yellow', value: '#eab308' },
    { label: 'Green', value: '#22c55e' },
    { label: 'Blue', value: '#3b82f6' },
    { label: 'Purple', value: '#a855f7' },
    { label: 'Pink', value: '#ec4899' },
    { label: 'Gray', value: '#6b7280' },
];

/**
 * Component for managing tags - create, share, update preferences, delete.
 */
export function TagManager() {
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    const { data: tagsResponse, isLoading } = useGetTags();
    const tags = (tagsResponse as { entities: Tag[] } | undefined)?.entities ?? [];

    const { data: usersResponse } = useGetAllUsers();
    const users = (usersResponse as { entities: User[] } | undefined)?.entities ?? [];

    // Create tag state
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [newTagName, setNewTagName] = useState('');
    const [newTagIcon, setNewTagIcon] = useState('');
    const [newTagColor, setNewTagColor] = useState(COLOR_OPTIONS[4].value);

    // Share dialog state
    const [shareTag, setShareTag] = useState<Tag | null>(null);
    const [selectedUserId, setSelectedUserId] = useState<string>('');

    // Preferences dialog state
    const [preferencesTag, setPreferencesTag] = useState<Tag | null>(null);
    const [preferenceColor, setPreferenceColor] = useState('');
    const [slackChannel, setSlackChannel] = useState<{ id: string; name: string } | null>(null);

    // Mutations
    const createTag = useCreateTag({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                setShowCreateDialog(false);
                setNewTagName('');
                setNewTagIcon('');
                setNewTagColor(COLOR_OPTIONS[4].value);
                showSuccess('Tag created!');
            },
            onError: () => showError('Failed to create tag'),
        },
    });

    const deleteTag = useDeleteTag({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                showSuccess('Tag deleted!');
            },
            onError: () => showError('Failed to delete tag'),
        },
    });

    const addMember = useAddTagMember({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                setShareTag(null);
                setSelectedUserId('');
                showSuccess('Tag shared!');
            },
            onError: () => showError('Failed to share tag'),
        },
    });

    const removeMember = useRemoveTagMember({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                showSuccess('Member removed!');
            },
            onError: () => showError('Failed to remove member'),
        },
    });

    const updatePreferences = useUpdateMyTagPreferences({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                setPreferencesTag(null);
                showSuccess('Preferences updated!');
            },
            onError: () => showError('Failed to update preferences'),
        },
    });

    const updateTag = useUpdateTag({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                showSuccess('Tag settings updated!');
            },
            onError: () => showError('Failed to update tag settings'),
        },
    });

    const handleCreateTag = () => {
        if (!newTagName.trim()) return;
        createTag.mutate({
            data: {
                name: newTagName.trim(),
                icon: newTagIcon.trim() || null,
                color: newTagColor,
            },
        });
    };

    const handleShareTag = () => {
        if (!shareTag || !selectedUserId) return;
        addMember.mutate({
            tagId: shareTag.id,
            data: { user_id: parseInt(selectedUserId) },
        });
    };

    const handleUpdatePreferences = () => {
        if (!preferencesTag) return;

        // Update personal color preference
        updatePreferences.mutate({
            tagId: preferencesTag.id,
            data: { color: preferenceColor || null },
        });

        // Update Slack channel if user is creator
        const currentUserMember = preferencesTag.members?.find((m) => m.role === 'creator');
        if (currentUserMember) {
            updateTag.mutate({
                tagId: preferencesTag.id,
                data: {
                    id: preferencesTag.id,
                    slack_channel_id: slackChannel?.id ?? null,
                    slack_channel_name: slackChannel?.name ?? null,
                },
            });
        }
    };

    if (isLoading) {
        return <div>Loading tags...</div>;
    }

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Tags</CardTitle>
                <Button size="sm" onClick={() => setShowCreateDialog(true)}>
                    <Plus className="h-4 w-4 mr-1" />
                    New Tag
                </Button>
            </CardHeader>
            <CardContent>
                {tags.length === 0 ? (
                    <p className="text-muted-foreground text-sm">
                        No tags yet. Create one to get started!
                    </p>
                ) : (
                    <ul className="space-y-2">
                        {tags.map((tag) => {
                            const currentUserMember = tag.members?.find((m) => m.role);
                            const isCreator = currentUserMember?.role === 'creator';

                            return (
                                <li
                                    key={tag.id}
                                    className="flex items-center justify-between p-2 rounded-lg border"
                                >
                                    <div className="flex items-center gap-2">
                                        <TagBadge tag={tag} color={currentUserMember?.color} />
                                        <span className="text-xs text-muted-foreground">
                                            {tag.members?.length ?? 0} member
                                            {(tag.members?.length ?? 0) !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                    <div className="flex gap-1">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => {
                                                setPreferencesTag(tag);
                                                setPreferenceColor(currentUserMember?.color || '');
                                                setSlackChannel(
                                                    tag.slack_channel_id && tag.slack_channel_name
                                                        ? {
                                                              id: tag.slack_channel_id,
                                                              name: tag.slack_channel_name,
                                                          }
                                                        : null
                                                );
                                            }}
                                            title="Preferences"
                                        >
                                            <Settings2 className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => setShareTag(tag)}
                                            title="Share"
                                        >
                                            <Share2 className="h-4 w-4" />
                                        </Button>
                                        {isCreator && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => deleteTag.mutate({ tagId: tag.id })}
                                                title="Delete"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                )}
            </CardContent>

            {/* Create Tag Dialog */}
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create New Tag</DialogTitle>
                        <DialogDescription>
                            Create a tag to organize your todos. You can share it with others later.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name">Name</Label>
                            <Input
                                id="name"
                                value={newTagName}
                                onChange={(e) => setNewTagName(e.target.value)}
                                placeholder="e.g., Work, Personal, Shopping"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="icon">Icon (optional emoji)</Label>
                            <Input
                                id="icon"
                                value={newTagIcon}
                                onChange={(e) => setNewTagIcon(e.target.value)}
                                placeholder="e.g., 🏠"
                                maxLength={4}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="color">Your Color</Label>
                            <Select value={newTagColor} onValueChange={setNewTagColor}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {COLOR_OPTIONS.map((option) => (
                                        <SelectItem key={option.value} value={option.value}>
                                            <div className="flex items-center gap-2">
                                                <div
                                                    className="w-4 h-4 rounded-full"
                                                    style={{ backgroundColor: option.value }}
                                                />
                                                {option.label}
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleCreateTag} disabled={!newTagName.trim()}>
                            Create
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Share Tag Dialog */}
            <Dialog open={!!shareTag} onOpenChange={(open) => !open && setShareTag(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Share Tag</DialogTitle>
                        <DialogDescription>
                            Share "{shareTag?.name}" with another user. They'll be able to see todos
                            with this tag and add it to their own todos.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label>Current Members</Label>
                            <div className="flex flex-wrap gap-2">
                                {shareTag?.members?.map((member) => {
                                    const memberUser = users.find((u) => u.id === member.user_id);
                                    const isCreator = member.role === 'creator';
                                    return (
                                        <div
                                            key={member.user_id}
                                            className="flex items-center gap-1 px-2 py-1 rounded-full bg-secondary text-sm"
                                        >
                                            <Users className="h-3 w-3" />
                                            {memberUser?.name || `User ${member.user_id}`}
                                            {isCreator && (
                                                <span className="text-xs text-muted-foreground">
                                                    (creator)
                                                </span>
                                            )}
                                            {!isCreator &&
                                                shareTag.members?.some(
                                                    (m) => m.role === 'creator'
                                                ) && (
                                                    <button
                                                        onClick={() =>
                                                            removeMember.mutate({
                                                                tagId: shareTag.id,
                                                                targetUserId: member.user_id,
                                                            })
                                                        }
                                                        className="ml-1 hover:text-destructive"
                                                    >
                                                        ×
                                                    </button>
                                                )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="user">Add User</Label>
                            <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a user..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {users
                                        .filter(
                                            (u) =>
                                                !shareTag?.members?.some((m) => m.user_id === u.id)
                                        )
                                        .map((user) => (
                                            <SelectItem key={user.id} value={user.id.toString()}>
                                                {user.name} ({user.email_address})
                                            </SelectItem>
                                        ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShareTag(null)}>
                            Close
                        </Button>
                        <Button onClick={handleShareTag} disabled={!selectedUserId}>
                            Share
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Preferences Dialog */}
            <Dialog
                open={!!preferencesTag}
                onOpenChange={(open) => !open && setPreferencesTag(null)}
            >
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Tag Preferences</DialogTitle>
                        <DialogDescription>
                            Customize how "{preferencesTag?.name}" appears for you.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="prefColor">Your Color</Label>
                            <Select value={preferenceColor} onValueChange={setPreferenceColor}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a color..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {COLOR_OPTIONS.map((option) => (
                                        <SelectItem key={option.value} value={option.value}>
                                            <div className="flex items-center gap-2">
                                                <div
                                                    className="w-4 h-4 rounded-full"
                                                    style={{ backgroundColor: option.value }}
                                                />
                                                {option.label}
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="mt-2">
                            <Label>Preview</Label>
                            <div className="mt-1">
                                {preferencesTag && (
                                    <TagBadge tag={preferencesTag} color={preferenceColor} />
                                )}
                            </div>
                        </div>

                        {/* Slack Channel - only for creators */}
                        {preferencesTag?.members?.some((m) => m.role === 'creator') && (
                            <div className="grid gap-2 pt-4 border-t">
                                <Label>Slack Notification Channel</Label>
                                <p className="text-xs text-muted-foreground">
                                    Notifications for todos with this tag will be sent to this
                                    channel instead of DMs.
                                </p>
                                <SlackChannelPicker
                                    value={slackChannel}
                                    onChange={setSlackChannel}
                                />
                            </div>
                        )}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setPreferencesTag(null)}>
                            Cancel
                        </Button>
                        <Button onClick={handleUpdatePreferences}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </Card>
    );
}
