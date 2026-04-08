import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
    useSearchDatasets,
    useSearchAssignments,
    useCreateDataset,
    Dataset,
    DatasetAssignment,
    DatasetCreateFromBucketRequest,
    getSearchDatasetsQueryKey,
    getSearchAssignmentsQueryKey,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import { Plus, Database, ArrowRight } from 'lucide-react';

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

function DatasetCard({
    dataset,
    assignments,
    onClick,
}: {
    dataset: Dataset;
    assignments: DatasetAssignment[];
    onClick: () => void;
}) {
    const myAssignments = assignments.filter((a) => a.dataset_id === dataset.id);
    const gtmLeads = myAssignments.filter((a) => a.role === 'gtm_lead');
    const researchers = myAssignments.filter((a) => a.role === 'researcher');
    const customers = myAssignments.filter((a) => a.role === 'customer');

    return (
        <Card className="cursor-pointer hover:border-primary/50 transition-colors" onClick={onClick}>
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="font-medium truncate">{dataset.name}</span>
                            {dataset.request_status && (
                                <Badge
                                    variant="outline"
                                    className={`text-xs ${requestStatusColors[dataset.request_status] ?? ''}`}
                                >
                                    {requestStatusLabels[dataset.request_status] ?? dataset.request_status}
                                </Badge>
                            )}
                        </div>
                        {dataset.description && (
                            <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                {dataset.description}
                            </p>
                        )}
                        <div className="flex items-center gap-3 mt-2">
                            {gtmLeads.length > 0 && (
                                <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700">
                                    {gtmLeads.length} GTM
                                </Badge>
                            )}
                            {researchers.length > 0 && (
                                <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700">
                                    {researchers.length} Researcher{researchers.length > 1 ? 's' : ''}
                                </Badge>
                            )}
                            {customers.length > 0 && (
                                <Badge variant="outline" className="text-xs bg-green-50 text-green-700">
                                    {customers.length} Customer{customers.length > 1 ? 's' : ''}
                                </Badge>
                            )}
                            {myAssignments.length === 0 && (
                                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700">
                                    Unassigned
                                </Badge>
                            )}
                            <span className="text-xs text-muted-foreground">
                                {new Date(dataset.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
                </div>
            </CardContent>
        </Card>
    );
}

export default function DatasetsPage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const currentUser = useCurrentUser();

    const [createOpen, setCreateOpen] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDescription, setNewDescription] = useState('');
    const [newBucketPath, setNewBucketPath] = useState('gs://product-onsite/sample2/');
    const [clipMetadataText, setClipMetadataText] = useState('');
    const [createError, setCreateError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'all' | 'mine' | 'unassigned'>('all');

    const { data: datasetsResponse, isLoading } = useSearchDatasets(
        {},
        { query: { refetchInterval: (query) => {
            const entities = (query.state.data as { entities: Dataset[] } | undefined)?.entities;
            const hasProcessing = entities?.some((d) => d.lifecycle === 'pending' && d.request_status !== 'requested');
            return hasProcessing ? 3000 : false;
        }}}
    );
    const datasets = (datasetsResponse as { entities: Dataset[] } | undefined)?.entities ?? [];

    const { data: assignmentsResponse } = useSearchAssignments({});
    const allAssignments = (assignmentsResponse as { entities: DatasetAssignment[] } | undefined)?.entities ?? [];

    const createDataset = useCreateDataset();
    const canCreate = currentUser?.role === 'gtm' || currentUser?.role === 'customer';

    // Filter datasets
    const filteredDatasets = datasets.filter((d) => {
        if (filter === 'mine') {
            return allAssignments.some((a) => a.dataset_id === d.id && a.user_id === currentUser?.id);
        }
        if (filter === 'unassigned') {
            return !allAssignments.some((a) => a.dataset_id === d.id);
        }
        return true;
    });

    const handleCreate = async () => {
        if (!newName.trim() || !newBucketPath.trim()) return;
        setCreateError(null);

        let clipMetadata: unknown[] | undefined;
        if (clipMetadataText.trim()) {
            try {
                const text = clipMetadataText.trim();
                if (text.startsWith('[')) {
                    clipMetadata = JSON.parse(text);
                } else {
                    clipMetadata = text.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
                }
            } catch {
                setCreateError('Invalid clip metadata JSON/JSONL');
                return;
            }
        }

        try {
            const result = await createDataset.mutateAsync({
                data: {
                    name: newName,
                    description: newDescription || undefined,
                    bucket_path: newBucketPath,
                    clip_metadata: clipMetadata as DatasetCreateFromBucketRequest['clip_metadata'],
                },
            });

            setCreateOpen(false);
            setNewName('');
            setNewDescription('');
            setNewBucketPath('gs://product-onsite/sample2/');
            setClipMetadataText('');
            setCreateError(null);
            queryClient.invalidateQueries({ queryKey: getSearchDatasetsQueryKey({}) });
            queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({}) });
            navigate(`/dataset/${result.dataset.id}`);
        } catch (e) {
            const message = e instanceof Error ? e.message : 'Failed to create dataset';
            setCreateError(message);
        }
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold">Datasets</h1>
                    {canCreate && (
                        <Button onClick={() => setCreateOpen(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            New Dataset
                        </Button>
                    )}
                </div>

                {/* Filters */}
                <div className="flex gap-2 mb-4">
                    {(['all', 'mine', 'unassigned'] as const).map((f) => (
                        <Button
                            key={f}
                            variant={filter === f ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setFilter(f)}
                        >
                            {f === 'all' ? 'All' : f === 'mine' ? 'My Datasets' : 'Unassigned'}
                        </Button>
                    ))}
                </div>

                {isLoading ? (
                    <p className="text-muted-foreground text-center py-12">Loading datasets...</p>
                ) : filteredDatasets.length === 0 ? (
                    <div className="text-center py-12">
                        <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-muted-foreground mb-2">No datasets found</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredDatasets.map((dataset) => (
                            <DatasetCard
                                key={dataset.id}
                                dataset={dataset}
                                assignments={allAssignments}
                                onClick={() => navigate(`/dataset/${dataset.id}`)}
                            />
                        ))}
                    </div>
                )}
            </div>

            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create New Dataset</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <div>
                            <label className="text-sm font-medium mb-1 block">Dataset Name</label>
                            <Input
                                placeholder="e.g. Customer X - Face Detection"
                                value={newName}
                                onChange={(e) => setNewName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">GCS Bucket Path</label>
                            <Input
                                placeholder="gs://product-onsite/sample2/"
                                value={newBucketPath}
                                onChange={(e) => setNewBucketPath(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Bucket must contain clip_metadata.jsonl and video_metadata.jsonl
                            </p>
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">Description</label>
                            <Textarea
                                placeholder="Dataset requirements and notes..."
                                value={newDescription}
                                onChange={(e) => setNewDescription(e.target.value)}
                                rows={3}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">
                                Clip Metadata (optional)
                            </label>
                            <Textarea
                                placeholder="Paste JSONL clip metadata to use a specific subset. Leave empty to use all clips from the bucket."
                                value={clipMetadataText}
                                onChange={(e) => setClipMetadataText(e.target.value)}
                                rows={4}
                                className="font-mono text-xs"
                            />
                        </div>
                        {createError && (
                            <p className="text-sm text-destructive">{createError}</p>
                        )}
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
                            <Button onClick={handleCreate} disabled={!newName.trim() || !newBucketPath.trim() || createDataset.isPending}>
                                {createDataset.isPending ? 'Creating...' : 'Create'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
