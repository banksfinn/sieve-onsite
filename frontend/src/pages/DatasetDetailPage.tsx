import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
    useGetDataset,
    useUpdateDataset,
    useSearchDatasetVersions,
    useIngestDataset,
    DatasetIngestRequest,
    useSearchAssignments,
    useCreateAssignment,
    useDeleteAssignment,
    useListAllUsers,
    useSearchReviews,
    DatasetVersion,
    DatasetAssignment,
    DatasetReview,
    User,
    getSearchAssignmentsQueryKey,
    getGetDatasetQueryKey,
    getSearchDatasetVersionsQueryKey,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import {
    ArrowLeft,
    Users,
    UserPlus,
    Trash2,
    Pencil,
    FolderOpen,
    MessageSquare,
    Send,
    CheckCircle2,
    RotateCcw,
    XCircle,
    ArrowRight,
    Plus,
} from 'lucide-react';

const requestStatusColors: Record<string, string> = {
    requested: 'bg-yellow-50 text-yellow-700',
    in_progress: 'bg-blue-50 text-blue-700',
    review_requested: 'bg-purple-50 text-purple-700',
    changes_requested: 'bg-orange-50 text-orange-700',
    approved: 'bg-green-50 text-green-700',
    rejected: 'bg-red-50 text-red-700',
};

const requestStatusLabels: Record<string, string> = {
    requested: 'requested',
    in_progress: 'in progress',
    review_requested: 'review requested',
    changes_requested: 'changes requested',
    approved: 'approved',
    rejected: 'rejected',
};

export default function DatasetDetailPage() {
    const { datasetId } = useParams<{ datasetId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const currentUser = useCurrentUser();
    const id = Number(datasetId);

    const [assignUserId, setAssignUserId] = useState('');
    const [assignRole, setAssignRole] = useState('researcher');
    const [teamOpen, setTeamOpen] = useState(false);
    const [ingestOpen, setIngestOpen] = useState(false);
    const [ingestBucketPath, setIngestBucketPath] = useState('gs://product-onsite/sample2/');
    const [ingestClipMetadata, setIngestClipMetadata] = useState('');

    const { data: dataset } = useGetDataset(id, {
        query: {
            refetchInterval: (query) => {
                const ds = query.state.data as { lifecycle?: string } | undefined;
                return ds?.lifecycle === 'pending' ? 2000 : false;
            },
        },
    });
    const isProcessing = dataset?.lifecycle === 'pending';
    const { data: versionsResponse } = useSearchDatasetVersions(id, {
        query: { enabled: !isProcessing },
    });
    const versions = (versionsResponse as { entities: DatasetVersion[] } | undefined)?.entities ?? [];

    const { data: reviewsResponse } = useSearchReviews(id);
    const allReviews = (reviewsResponse as { entities: DatasetReview[] } | undefined)?.entities ?? [];

    const { data: assignmentsResponse } = useSearchAssignments({ dataset_id: id });
    const assignments = (assignmentsResponse as { entities: DatasetAssignment[] } | undefined)?.entities ?? [];

    const isInternal = currentUser?.role !== 'customer';
    const { data: usersResponse } = useListAllUsers({}, { query: { enabled: isInternal } });
    const users = (usersResponse as { entities: User[] } | undefined)?.entities ?? [];

    const createAssignment = useCreateAssignment();
    const deleteAssignment = useDeleteAssignment();
    const ingestDataset = useIngestDataset();
    const updateDataset = useUpdateDataset();

    const handleStatusTransition = async (newStatus: string) => {
        await updateDataset.mutateAsync({
            datasetId: id,
            data: { id, request_status: newStatus },
        });
        queryClient.invalidateQueries({ queryKey: getGetDatasetQueryKey(id) });
    };

    const handleIngest = async () => {
        if (!ingestBucketPath.trim()) return;
        console.log('[ingest] starting', { datasetId: id, bucketPath: ingestBucketPath });
        try {
            let clipMetadata: unknown[] | undefined;
            if (ingestClipMetadata.trim()) {
                const text = ingestClipMetadata.trim();
                // Support both JSON array and JSONL (one object per line)
                if (text.startsWith('[')) {
                    clipMetadata = JSON.parse(text);
                } else {
                    clipMetadata = text.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
                }
            }
            const result = await ingestDataset.mutateAsync({
                datasetId: id,
                data: {
                    bucket_path: ingestBucketPath,
                    clip_metadata: clipMetadata as DatasetIngestRequest['clip_metadata'],
                },
            });
            console.log('[ingest] success', result);
            setIngestOpen(false);
            setIngestBucketPath('gs://product-onsite/sample2/');
            setIngestClipMetadata('');
            queryClient.invalidateQueries({ queryKey: getGetDatasetQueryKey(id) });
            queryClient.invalidateQueries({ queryKey: getSearchDatasetVersionsQueryKey(id) });
        } catch (e) {
            console.error('[ingest] failed', e);
        }
    };

    const handleAssign = async () => {
        if (!assignUserId) return;
        await createAssignment.mutateAsync({
            data: { dataset_id: id, user_id: Number(assignUserId), role: assignRole },
        });
        setAssignUserId('');
        queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({ dataset_id: id }) });
    };

    const handleRemoveAssignment = async (assignmentId: number) => {
        await deleteAssignment.mutateAsync({ assignmentId });
        queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({ dataset_id: id }) });
    };

    const handleAssignSelf = async () => {
        if (!currentUser) return;
        const role = currentUser.role === 'researcher' ? 'researcher' : 'gtm_lead';
        await createAssignment.mutateAsync({
            data: { dataset_id: id, user_id: currentUser.id, role },
        });
        queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({ dataset_id: id }) });
    };

    const isAssigned = assignments.some((a) => a.user_id === currentUser?.id);
    const assignedUserIds = new Set(assignments.map((a) => a.user_id));
    const unassignedUsers = users.filter((u) => !assignedUserIds.has(u.id));

    const displayVersions = versions.map((v) => ({
        ...v,
        label: `v${v.version_number}`,
    }));

    const roleColors: Record<string, string> = {
        gtm_lead: 'bg-blue-50 text-blue-700',
        researcher: 'bg-purple-50 text-purple-700',
        customer: 'bg-green-50 text-green-700',
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-6">
                    <Button variant="ghost" size="icon" onClick={() => navigate('/datasets')}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div className="flex-1">
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold">{dataset?.name ?? 'Loading...'}</h1>
                            {dataset?.request_status && (
                                <Badge variant="outline" className={requestStatusColors[dataset.request_status] ?? ''}>
                                    {requestStatusLabels[dataset.request_status] ?? dataset.request_status}
                                </Badge>
                            )}
                        </div>
                        {dataset?.description && (
                            <p className="text-muted-foreground mt-1">{dataset.description}</p>
                        )}
                        {dataset?.bucket_path && (
                            <p className="text-xs text-muted-foreground mt-1 font-mono">
                                {dataset.bucket_path}
                            </p>
                        )}
                    </div>
                    {isInternal && displayVersions.length > 0 && (
                        <Button
                            onClick={() => {
                                const latest = displayVersions.find((v) => v.version_number > 0);
                                if (latest) navigate(`/dataset/${id}/version/${latest.id}/edit`);
                            }}
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Create New Version
                        </Button>
                    )}
                    {isInternal && !isAssigned && (
                        <Button variant="outline" onClick={handleAssignSelf}>
                            <UserPlus className="h-4 w-4 mr-2" />
                            Assign Myself
                        </Button>
                    )}
                </div>

                {/* Review Summary — prominent CTA for latest version */}
                {(() => {
                    const latestVersion = displayVersions.find((v) => v.version_number > 0);
                    const totalOpen = allReviews.filter((r) => r.status === 'open').length;
                    const totalResolved = allReviews.filter((r) => r.status !== 'open').length;

                    if (!latestVersion) return null;

                    return (
                        <Card className="mb-6">
                            <CardContent className="p-5">
                                {latestVersion ? (
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <h2 className="font-semibold">
                                                    Latest: {latestVersion.label}
                                                </h2>
                                                {latestVersion.commit_message && (
                                                    <span className="text-sm text-muted-foreground">
                                                        — {latestVersion.commit_message}
                                                    </span>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-3 text-sm">
                                                {allReviews.length === 0 ? (
                                                    <span className="text-muted-foreground">No reviews yet</span>
                                                ) : (
                                                    <>
                                                        {totalOpen > 0 && (
                                                            <span className="text-yellow-600 font-medium">
                                                                {totalOpen} open review{totalOpen !== 1 ? 's' : ''}
                                                            </span>
                                                        )}
                                                        {totalResolved > 0 && (
                                                            <span className="text-green-600">
                                                                {totalResolved} resolved
                                                            </span>
                                                        )}
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                        <Button
                                            onClick={() => navigate(`/dataset/${id}/version/${latestVersion.id}/review`)}
                                        >
                                            <MessageSquare className="h-4 w-4 mr-2" />
                                            Review Clips
                                        </Button>
                                    </div>
                                ) : null}
                            </CardContent>
                        </Card>
                    );
                })()}

                {/* Dataset Status */}
                {dataset && dataset.lifecycle !== 'pending' && (
                    <Card className="mb-6">
                        <CardContent className="p-5">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-muted-foreground">Status</span>
                                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                                    <Badge variant="outline" className={requestStatusColors[dataset.request_status ?? ''] ?? ''}>
                                        {requestStatusLabels[dataset.request_status ?? ''] ?? dataset.request_status}
                                    </Badge>
                                </div>
                                <div className="flex items-center gap-2">
                                    {/* Researcher/GTM: submit for review */}
                                    {isInternal && (dataset.request_status === 'in_progress' || dataset.request_status === 'changes_requested') && (
                                        <Button
                                            size="sm"
                                            onClick={() => handleStatusTransition('review_requested')}
                                            disabled={updateDataset.isPending}
                                        >
                                            <Send className="h-3.5 w-3.5 mr-1" />
                                            {dataset.request_status === 'changes_requested' ? 'Resubmit for Review' : 'Submit for Review'}
                                        </Button>
                                    )}

                                    {/* Customer (or GTM acting as reviewer): approve / request changes */}
                                    {dataset.request_status === 'review_requested' && (
                                        <>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleStatusTransition('changes_requested')}
                                                disabled={updateDataset.isPending}
                                            >
                                                <RotateCcw className="h-3.5 w-3.5 mr-1" />
                                                Request Changes
                                            </Button>
                                            <Button
                                                size="sm"
                                                onClick={() => handleStatusTransition('approved')}
                                                disabled={updateDataset.isPending}
                                                className="bg-green-600 hover:bg-green-700"
                                            >
                                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                                                Approve
                                            </Button>
                                        </>
                                    )}

                                    {/* Reject — available for GTM/customer on any non-terminal status */}
                                    {(currentUser?.role === 'gtm' || currentUser?.role === 'customer') &&
                                        dataset.request_status !== 'approved' &&
                                        dataset.request_status !== 'rejected' && (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                            onClick={() => handleStatusTransition('rejected')}
                                            disabled={updateDataset.isPending}
                                        >
                                            <XCircle className="h-3.5 w-3.5 mr-1" />
                                            Reject
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                <div className={`grid grid-cols-1 ${isInternal ? 'lg:grid-cols-2' : ''} gap-6`}>
                    {/* Versions */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between pb-3">
                            <CardTitle className="text-base">
                                <GitBranch className="h-4 w-4 inline mr-2" />
                                Versions ({displayVersions.length})
                            </CardTitle>
                            {dataset?.lifecycle === 'pending' && isInternal && (
                                <Button size="sm" onClick={() => setIngestOpen(true)}>
                                    <FolderOpen className="h-3 w-3 mr-1" />
                                    Ingest from Bucket
                                </Button>
                            )}
                        </CardHeader>
                        <CardContent>
                            {displayVersions.length === 0 ? (
                                <p className="text-sm text-muted-foreground text-center py-6">
                                    No versions yet
                                </p>
                            ) : (
                                <div className="space-y-2">
                                    {displayVersions.map((v, i) => {
                                        const versionReviews = allReviews.filter((r) => r.dataset_version_id === v.id);
                                        const openCount = versionReviews.filter((r) => r.status === 'open').length;
                                        const resolvedCount = versionReviews.filter((r) => r.status !== 'open').length;

                                        return (
                                        <div
                                            key={v.id}
                                            className="flex items-center justify-between p-3 rounded border hover:bg-muted/50 transition-colors"
                                        >
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium text-sm">{v.label}</span>
                                                    {i === 0 && v.version_number > 0 && (
                                                        <Badge variant="outline" className="text-xs bg-primary/10 text-primary">
                                                            Latest
                                                        </Badge>
                                                    )}
                                                </div>
                                                {v.commit_message && (
                                                    <p className="text-xs text-muted-foreground mt-0.5">
                                                        {v.commit_message}
                                                    </p>
                                                )}
                                                <div className="flex items-center gap-2 mt-0.5">
                                                    <span className="text-xs text-muted-foreground">
                                                        {new Date(v.created_at).toLocaleString()}
                                                    </span>
                                                    {versionReviews.length > 0 && (
                                                        <span className="text-xs">
                                                            {openCount > 0 && (
                                                                <span className="text-yellow-600">{openCount} open</span>
                                                            )}
                                                            {openCount > 0 && resolvedCount > 0 && ' · '}
                                                            {resolvedCount > 0 && (
                                                                <span className="text-green-600">{resolvedCount} resolved</span>
                                                            )}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                {v.parent_version_id && (
                                                    <span className="text-xs text-muted-foreground mr-1">
                                                        from {displayVersions.find((p) => p.id === v.parent_version_id)?.label ?? '?'}
                                                    </span>
                                                )}
                                                {v.version_number > 0 && (
                                                    <>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-7 w-7"
                                                            onClick={() => navigate(`/dataset/${id}/version/${v.id}/review`)}
                                                            title="Review"
                                                        >
                                                            <MessageSquare className="h-3 w-3" />
                                                        </Button>
                                                        {isInternal && (
                                                            <Button
                                                                variant="ghost"
                                                                size="icon"
                                                                className="h-7 w-7"
                                                                onClick={() => navigate(`/dataset/${id}/version/${v.id}/edit`)}
                                                                title="Edit"
                                                            >
                                                                <Pencil className="h-3 w-3" />
                                                            </Button>
                                                        )}
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                        );
                                    })}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Team Assignments — hidden from customers */}
                    {isInternal && (
                    <Card>
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">
                                <Users className="h-4 w-4 inline mr-2" />
                                Team ({assignments.length})
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {assignments.length === 0 ? (
                                <p className="text-sm text-muted-foreground text-center py-4">No team members</p>
                            ) : (
                                <div className="space-y-2">
                                    {assignments.map((a) => {
                                        const user = users.find((u) => u.id === a.user_id);
                                        return (
                                            <div key={a.id} className="flex items-center justify-between p-2 rounded border">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-sm">{user?.name ?? `User #${a.user_id}`}</span>
                                                    <Badge variant="outline" className={`text-xs ${roleColors[a.role] ?? ''}`}>
                                                        {a.role.replace(/_/g, ' ')}
                                                    </Badge>
                                                </div>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={() => handleRemoveAssignment(a.id)}
                                                >
                                                    <Trash2 className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Add assignment */}
                            <div className="flex gap-2 pt-2 border-t">
                                <Select value={assignUserId} onValueChange={setAssignUserId}>
                                    <SelectTrigger className="flex-1 text-sm">
                                        <SelectValue placeholder="Select user..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {unassignedUsers.map((u) => (
                                            <SelectItem key={u.id} value={String(u.id)}>
                                                {u.name} ({u.role})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <Select value={assignRole} onValueChange={setAssignRole}>
                                    <SelectTrigger className="w-36 text-sm">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="gtm_lead">GTM Lead</SelectItem>
                                        <SelectItem value="researcher">Researcher</SelectItem>
                                        <SelectItem value="customer">Customer</SelectItem>
                                    </SelectContent>
                                </Select>
                                <Button
                                    size="sm"
                                    disabled={!assignUserId || createAssignment.isPending}
                                    onClick={handleAssign}
                                >
                                    <UserPlus className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                    )}
                </div>
            </div>

            {/* Ingest Dialog */}
            <Dialog open={ingestOpen} onOpenChange={setIngestOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Ingest from GCS Bucket</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <div>
                            <label className="text-sm font-medium mb-1 block">GCS Bucket Path</label>
                            <Input
                                placeholder="gs://product-onsite/sample2/"
                                value={ingestBucketPath}
                                onChange={(e) => setIngestBucketPath(e.target.value)}
                                className="font-mono text-sm"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Bucket must contain clip_metadata.jsonl and video_metadata.jsonl
                            </p>
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">
                                Clip Metadata (optional)
                            </label>
                            <Textarea
                                placeholder="Paste JSON clip metadata to use a specific subset. Leave empty to use all clips."
                                value={ingestClipMetadata}
                                onChange={(e) => setIngestClipMetadata(e.target.value)}
                                rows={4}
                                className="font-mono text-xs"
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setIngestOpen(false)}>
                                Cancel
                            </Button>
                            <Button
                                onClick={handleIngest}
                                disabled={!ingestBucketPath.trim() || ingestDataset.isPending}
                            >
                                {ingestDataset.isPending ? 'Ingesting...' : 'Ingest'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
