import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
    useListUsers,
    useUpdateUser,
    useListInvitations,
    useCreateInvitation,
    useCreateFakeUser,
    useImpersonateUser,
    useStopImpersonation,
    User,
    Invitation,
    getListUsersQueryKey,
    getListInvitationsQueryKey,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import { useSnackbar } from '@/store/components/snackbarSlice';
import {
    Shield,
    UserPlus,
    Mail,
    Eye,
} from 'lucide-react';

const roleColors: Record<string, string> = {
    customer: 'bg-green-50 text-green-700',
    gtm: 'bg-blue-50 text-blue-700',
    researcher: 'bg-purple-50 text-purple-700',
};

export default function AdminPage() {
    const queryClient = useQueryClient();
    const currentUser = useCurrentUser();
    const { showSuccess } = useSnackbar();

    const [inviteOpen, setInviteOpen] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState('customer');
    const [inviteAccess, setInviteAccess] = useState('regular');

    const [fakeOpen, setFakeOpen] = useState(false);
    const [fakeName, setFakeName] = useState('');
    const [fakeEmail, setFakeEmail] = useState('');
    const [fakeRole, setFakeRole] = useState('customer');

    const { data: usersResponse } = useListUsers({});
    const users = (usersResponse as { entities: User[] } | undefined)?.entities ?? [];

    const { data: invitationsResponse } = useListInvitations({});
    const invitations = (invitationsResponse as { entities: Invitation[] } | undefined)?.entities ?? [];

    const updateUser = useUpdateUser();
    const createInvitation = useCreateInvitation();
    const createFakeUser = useCreateFakeUser();
    const impersonate = useImpersonateUser();
    const stopImpersonation = useStopImpersonation();

    const handleInvite = async () => {
        if (!inviteEmail.trim()) return;
        await createInvitation.mutateAsync({
            data: {
                email_address: inviteEmail,
                role: inviteRole,
                access_level: inviteAccess,
            },
        });
        setInviteOpen(false);
        setInviteEmail('');
        showSuccess('Invitation created');
        queryClient.invalidateQueries({ queryKey: getListInvitationsQueryKey({}) });
    };

    const handleCreateFake = async () => {
        if (!fakeName.trim() || !fakeEmail.trim()) return;
        await createFakeUser.mutateAsync({
            data: { name: fakeName, email_address: fakeEmail, role: fakeRole as 'customer' | 'gtm' | 'researcher', access_level: 'regular' },
        });
        setFakeOpen(false);
        setFakeName('');
        setFakeEmail('');
        showSuccess('Test user created');
        queryClient.invalidateQueries({ queryKey: getListUsersQueryKey({}) });
    };

    const handleRoleChange = async (userId: number, newRole: string) => {
        await updateUser.mutateAsync({ userId, data: { id: userId, role: newRole } });
        queryClient.invalidateQueries({ queryKey: getListUsersQueryKey({}) });
    };

    const handleImpersonate = async (userId: number) => {
        await impersonate.mutateAsync({ data: { user_id: userId } });
        window.location.reload();
    };

    const handleStopImpersonation = async () => {
        await stopImpersonation.mutateAsync();
        window.location.reload();
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <Shield className="h-6 w-6" />
                        <h1 className="text-2xl font-bold">Admin</h1>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setFakeOpen(true)}>
                            <UserPlus className="h-4 w-4 mr-2" />
                            Create Test User
                        </Button>
                        <Button onClick={() => setInviteOpen(true)}>
                            <Mail className="h-4 w-4 mr-2" />
                            Invite User
                        </Button>
                    </div>
                </div>

                {/* Users */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="text-base">Users ({users.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {users.map((user) => (
                                <div key={user.id} className="flex items-center justify-between p-3 rounded border">
                                    <div className="flex items-center gap-3">
                                        <div>
                                            <span className="font-medium text-sm">{user.name}</span>
                                            <p className="text-xs text-muted-foreground">{user.email_address}</p>
                                        </div>
                                        <Badge variant="outline" className={`text-xs ${roleColors[user.role ?? ''] ?? ''}`}>
                                            {user.role}
                                        </Badge>
                                        {user.access_level === 'admin' && (
                                            <Badge variant="outline" className="text-xs bg-red-50 text-red-700">
                                                admin
                                            </Badge>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Select
                                            value={user.role ?? 'customer'}
                                            onValueChange={(v) => handleRoleChange(user.id, v)}
                                        >
                                            <SelectTrigger className="w-32 h-8 text-xs">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="customer">Customer</SelectItem>
                                                <SelectItem value="gtm">GTM</SelectItem>
                                                <SelectItem value="researcher">Researcher</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        {user.id !== currentUser?.id && user.access_level !== 'admin' && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-8 text-xs"
                                                onClick={() => handleImpersonate(user.id)}
                                            >
                                                <Eye className="h-3 w-3 mr-1" />
                                                Impersonate
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Invitations */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Invitations ({invitations.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {invitations.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4">No pending invitations</p>
                        ) : (
                            <div className="space-y-2">
                                {invitations.map((inv) => (
                                    <div key={inv.id} className="flex items-center justify-between p-3 rounded border">
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm">{inv.email_address}</span>
                                            <Badge variant="outline" className={`text-xs ${roleColors[inv.role] ?? ''}`}>
                                                {inv.role}
                                            </Badge>
                                        </div>
                                        <Badge variant={inv.accepted ? 'default' : 'outline'} className="text-xs">
                                            {inv.accepted ? 'Accepted' : 'Pending'}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Invite Dialog */}
            <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Invite User</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <Input placeholder="Email address" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} />
                        <div className="grid grid-cols-2 gap-3">
                            <Select value={inviteRole} onValueChange={setInviteRole}>
                                <SelectTrigger><SelectValue placeholder="Role" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="customer">Customer</SelectItem>
                                    <SelectItem value="gtm">GTM</SelectItem>
                                    <SelectItem value="researcher">Researcher</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select value={inviteAccess} onValueChange={setInviteAccess}>
                                <SelectTrigger><SelectValue placeholder="Access" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="regular">Regular</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setInviteOpen(false)}>Cancel</Button>
                            <Button onClick={handleInvite} disabled={!inviteEmail.trim() || createInvitation.isPending}>
                                {createInvitation.isPending ? 'Sending...' : 'Send Invite'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Fake User Dialog */}
            <Dialog open={fakeOpen} onOpenChange={setFakeOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create Test User</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <Input placeholder="Name" value={fakeName} onChange={(e) => setFakeName(e.target.value)} />
                        <Input placeholder="Email" value={fakeEmail} onChange={(e) => setFakeEmail(e.target.value)} />
                        <Select value={fakeRole} onValueChange={setFakeRole}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                                <SelectItem value="customer">Customer</SelectItem>
                                <SelectItem value="gtm">GTM</SelectItem>
                                <SelectItem value="researcher">Researcher</SelectItem>
                            </SelectContent>
                        </Select>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setFakeOpen(false)}>Cancel</Button>
                            <Button onClick={handleCreateFake} disabled={!fakeName.trim() || !fakeEmail.trim() || createFakeUser.isPending}>
                                {createFakeUser.isPending ? 'Creating...' : 'Create'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
