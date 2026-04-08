import { AppSidebar } from '@/components/common';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCurrentUser } from '@/store/components/authSlice';

export default function ProfilePage() {
    const user = useCurrentUser();

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
            </div>
        </AppSidebar>
    );
}
