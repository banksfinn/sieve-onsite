import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { NotificationTimingSelector } from '@/components/notifications';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    useGetNotificationPreferences,
    useUpdateNotificationPreferences,
    getGetNotificationPreferencesQueryKey,
} from '@/openapi/fullstackBase';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { useCurrentUser } from '@/store/components/authSlice';

export default function ProfilePage() {
    const user = useCurrentUser();
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    const { data: preferences, isLoading: preferencesLoading } = useGetNotificationPreferences();

    const [notificationTiming, setNotificationTiming] = useState<string[]>(['30_minutes_before']);
    const [isDirty, setIsDirty] = useState(false);

    // Sync local state with fetched preferences
    useEffect(() => {
        if (preferences?.notification_timing) {
            setNotificationTiming(preferences.notification_timing);
            setIsDirty(false);
        }
    }, [preferences]);

    const updatePreferences = useUpdateNotificationPreferences({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({
                    queryKey: getGetNotificationPreferencesQueryKey(),
                });
                setIsDirty(false);
                showSuccess('Notification preferences saved!');
            },
            onError: () => {
                showError('Failed to save notification preferences');
            },
        },
    });

    const handleTimingChange = (newTiming: string[]) => {
        setNotificationTiming(newTiming);
        setIsDirty(true);
    };

    const handleSave = () => {
        updatePreferences.mutate({
            data: {
                notification_timing: notificationTiming.length > 0 ? notificationTiming : null,
            },
        });
    };

    return (
        <AppSidebar>
            <div className="max-w-2xl space-y-6">
                <h1 className="text-2xl font-bold tracking-tight">Profile</h1>

                <Card>
                    <CardHeader>
                        <CardTitle>Account Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Name</p>
                            <p className="text-lg">{user?.name ?? 'Not set'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Email</p>
                            <p className="text-lg">{user?.email_address ?? 'Not available'}</p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Notification Preferences</CardTitle>
                        <CardDescription>
                            Choose when you want to receive Slack notifications for your todos.
                            These are your default settings - you can override them for individual
                            todos.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {preferencesLoading ? (
                            <p className="text-muted-foreground">Loading preferences...</p>
                        ) : (
                            <>
                                <NotificationTimingSelector
                                    value={notificationTiming}
                                    onChange={handleTimingChange}
                                />
                                <div className="flex justify-end pt-4">
                                    <Button
                                        onClick={handleSave}
                                        disabled={!isDirty || updatePreferences.isPending}
                                    >
                                        {updatePreferences.isPending
                                            ? 'Saving...'
                                            : 'Save Preferences'}
                                    </Button>
                                </div>
                            </>
                        )}
                    </CardContent>
                </Card>
            </div>
        </AppSidebar>
    );
}
