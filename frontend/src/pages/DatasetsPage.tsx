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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
    useSearchDatasets,
    useSearchAssignments,
    useCreateDataset,
    useCreateAssignment,
    useListUsers,
    Dataset,
    DatasetAssignment,
    User,
    getSearchDatasetsQueryKey,
    getSearchAssignmentsQueryKey,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import { Plus, Database, ArrowRight } from 'lucide-react';

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
    const [assignCustomerId, setAssignCustomerId] = useState<string>('');
    const [filter, setFilter] = useState<'all' | 'mine' | 'unassigned'>('all');

    const { data: datasetsResponse, isLoading } = useSearchDatasets({});
    const datasets = (datasetsResponse as { entities: Dataset[] } | undefined)?.entities ?? [];

    const { data: assignmentsResponse } = useSearchAssignments({});
    const allAssignments = (assignmentsResponse as { entities: DatasetAssignment[] } | undefined)?.entities ?? [];

    const { data: usersResponse } = useListUsers({});
    const users = (usersResponse as { entities: User[] } | undefined)?.entities ?? [];
    const customers = users.filter((u) => u.role === 'customer');

    const createDataset = useCreateDataset();
    const createAssignment = useCreateAssignment();

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
        if (!newName.trim()) return;

        const dataset = await createDataset.mutateAsync({
            data: { name: newName, description: newDescription || undefined },
        });

        // Assign current user as GTM lead
        if (currentUser) {
            await createAssignment.mutateAsync({
                data: { dataset_id: dataset.id, user_id: currentUser.id, role: 'gtm_lead' },
            });
        }

        // Assign customer if selected
        if (assignCustomerId) {
            await createAssignment.mutateAsync({
                data: { dataset_id: dataset.id, user_id: Number(assignCustomerId), role: 'customer' },
            });
        }

        setCreateOpen(false);
        setNewName('');
        setNewDescription('');
        setAssignCustomerId('');
        queryClient.invalidateQueries({ queryKey: getSearchDatasetsQueryKey({}) });
        queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({}) });
    };

    const handleAssignSelf = async (datasetId: number) => {
        if (!currentUser) return;
        const role = currentUser.role === 'researcher' ? 'researcher' : 'gtm_lead';
        await createAssignment.mutateAsync({
            data: { dataset_id: datasetId, user_id: currentUser.id, role },
        });
        queryClient.invalidateQueries({ queryKey: getSearchAssignmentsQueryKey({}) });
    };

    const isPending = createDataset.isPending || createAssignment.isPending;

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold">Datasets</h1>
                    <Button onClick={() => setCreateOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        New Dataset
                    </Button>
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
                            <label className="text-sm font-medium mb-1 block">Description</label>
                            <Textarea
                                placeholder="Dataset requirements and notes..."
                                value={newDescription}
                                onChange={(e) => setNewDescription(e.target.value)}
                                rows={3}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">Assign Customer</label>
                            <Select value={assignCustomerId} onValueChange={setAssignCustomerId}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select customer..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {customers.map((c) => (
                                        <SelectItem key={c.id} value={String(c.id)}>
                                            {c.name} ({c.email_address})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
                            <Button onClick={handleCreate} disabled={!newName.trim() || isPending}>
                                {isPending ? 'Creating...' : 'Create'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
