import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
    getSearchDatasetsQueryKey,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import {
    Database,
    ArrowRight,
    Inbox,
    AlertCircle,
    Clock,
    CheckCircle2,
    Plus,
} from 'lucide-react';

const lifecycleColors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-700',
    active: 'bg-green-100 text-green-700',
    archived: 'bg-slate-100 text-slate-500',
};

const requestStatusColors: Record<string, string> = {
    requested: 'bg-amber-100 text-amber-700',
    in_progress: 'bg-blue-100 text-blue-700',
    review_requested: 'bg-purple-100 text-purple-700',
    changes_requested: 'bg-orange-100 text-orange-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
};

const requestStatusLabels: Record<string, string> = {
    requested: 'requested',
    in_progress: 'in progress',
    review_requested: 'review requested',
    changes_requested: 'changes requested',
    approved: 'approved',
    rejected: 'rejected',
};

// --- Shared Components ---

function DatasetRow({
    dataset,
    role,
    onClick,
}: {
    dataset: Dataset;
    role?: string;
    onClick: () => void;
}) {
    const requestStatus = dataset.request_status ?? 'requested';
    return (
        <button
            onClick={onClick}
            className="w-full flex items-center justify-between p-3 rounded-lg border hover:border-primary/50 transition-colors text-left"
        >
            <div className="flex items-center gap-3 min-w-0">
                <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <div className="min-w-0">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{dataset.name}</span>
                        <Badge variant="outline" className={`text-xs ${requestStatusColors[requestStatus] ?? ''}`}>
                            {requestStatusLabels[requestStatus] ?? requestStatus}
                        </Badge>
                        {role && (
                            <Badge variant="outline" className="text-xs">
                                {role.replace(/_/g, ' ')}
                            </Badge>
                        )}
                    </div>
                    {dataset.description && (
                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                            {dataset.description}
                        </p>
                    )}
                </div>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
        </button>
    );
}

function StatCard({
    label,
    value,
    icon: Icon,
    onClick,
}: {
    label: string;
    value: number;
    icon: typeof Database;
    onClick?: () => void;
}) {
    return (
        <Card
            className={onClick ? 'cursor-pointer hover:border-primary/50 transition-colors' : ''}
            onClick={onClick}
        >
            <CardContent className="p-4 flex items-center gap-3">
                <Icon className="h-8 w-8 text-muted-foreground" />
                <div>
                    <p className="text-2xl font-bold">{value}</p>
                    <p className="text-xs text-muted-foreground">{label}</p>
                </div>
            </CardContent>
        </Card>
    );
}

function RequestDatasetDialog({
    open,
    onOpenChange,
}: {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}) {
    const queryClient = useQueryClient();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const createDataset = useCreateDataset();

    const handleSubmit = async () => {
        if (!name.trim()) return;
        await createDataset.mutateAsync({
            data: { name, description: description || undefined },
        });
        setName('');
        setDescription('');
        onOpenChange(false);
        queryClient.invalidateQueries({ queryKey: getSearchDatasetsQueryKey({}) });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Request a New Dataset</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-2">
                    <div>
                        <label className="text-sm font-medium mb-1 block">What do you need?</label>
                        <Input
                            placeholder="e.g. Full-body videos with face detection"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium mb-1 block">Additional details</label>
                        <Textarea
                            placeholder="Describe your requirements — resolution, content type, metadata needs, quantity..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            rows={4}
                        />
                    </div>
                    <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button
                            onClick={handleSubmit}
                            disabled={!name.trim() || createDataset.isPending}
                        >
                            {createDataset.isPending ? 'Submitting...' : 'Submit Request'}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}

// --- Customer Home ---

function CustomerHome({
    myDatasets,
}: {
    myDatasets: Dataset[];
}) {
    const navigate = useNavigate();
    const [requestOpen, setRequestOpen] = useState(false);

    const pending = myDatasets.filter((d) => d.request_status === 'requested');
    const ready = myDatasets.filter((d) => d.request_status === 'review_requested');
    const inProgress = myDatasets.filter((d) => d.request_status === 'in_progress');

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="Pending requests" value={pending.length} icon={Clock} />
                <StatCard label="Ready to review" value={ready.length} icon={AlertCircle} />
                <StatCard label="In progress" value={inProgress.length} icon={CheckCircle2} />
            </div>

            {/* Ready to Review */}
            {ready.length > 0 && (
                <section>
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                        Ready for Your Review
                    </h2>
                    <div className="space-y-2">
                        {ready.map((d) => (
                            <DatasetRow key={d.id} dataset={d} onClick={() => navigate(`/dataset/${d.id}`)} />
                        ))}
                    </div>
                </section>
            )}

            {/* My Datasets */}
            <section>
                <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                        My Datasets ({myDatasets.length})
                    </h2>
                    <Button variant="outline" size="sm" onClick={() => setRequestOpen(true)}>
                        <Plus className="h-3 w-3 mr-1" />
                        Request New Dataset
                    </Button>
                </div>
                {myDatasets.length === 0 ? (
                    <Card>
                        <CardContent className="p-8 text-center">
                            <Inbox className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                            <p className="text-muted-foreground mb-1">No datasets yet</p>
                            <p className="text-sm text-muted-foreground">Request a dataset to get started.</p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-2">
                        {myDatasets.map((d) => (
                            <DatasetRow key={d.id} dataset={d} onClick={() => navigate(`/dataset/${d.id}`)} />
                        ))}
                    </div>
                )}
            </section>

            <RequestDatasetDialog open={requestOpen} onOpenChange={setRequestOpen} />
        </div>
    );
}

// --- GTM Home ---

function GTMHome({
    datasets,
    allAssignments,
    myAssignments,
    myDatasets,
}: {
    datasets: Dataset[];
    allAssignments: DatasetAssignment[];
    myAssignments: DatasetAssignment[];
    myDatasets: Dataset[];
}) {
    const navigate = useNavigate();

    const newRequests = datasets.filter((d) => d.request_status === 'requested');
    const unassigned = datasets.filter(
        (d) => !allAssignments.some((a) => a.dataset_id === d.id && a.role === 'gtm_lead')
    );
    const active = myDatasets.filter((d) => d.lifecycle === 'active');

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="New requests" value={newRequests.length} icon={AlertCircle} onClick={() => navigate('/datasets')} />
                <StatCard label="Unassigned datasets" value={unassigned.length} icon={Database} onClick={() => navigate('/datasets')} />
                <StatCard label="Active datasets" value={active.length} icon={CheckCircle2} />
            </div>

            {/* New Requests */}
            {newRequests.length > 0 && (
                <section>
                    <Card className="border-amber-200 bg-amber-50/30">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-amber-800">
                                <AlertCircle className="h-4 w-4" />
                                New Customer Requests ({newRequests.length})
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {newRequests.map((d) => (
                                <DatasetRow key={d.id} dataset={d} onClick={() => navigate(`/dataset/${d.id}`)} />
                            ))}
                        </CardContent>
                    </Card>
                </section>
            )}

            {/* My Datasets */}
            <section>
                <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                        My Datasets ({myDatasets.length})
                    </h2>
                    <Button variant="ghost" size="sm" onClick={() => navigate('/datasets')}>
                        View All Datasets
                    </Button>
                </div>
                {myDatasets.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No datasets assigned to you yet.</p>
                ) : (
                    <div className="space-y-2">
                        {myDatasets.slice(0, 5).map((d) => {
                            const role = myAssignments.find((a) => a.dataset_id === d.id)?.role;
                            return (
                                <DatasetRow key={d.id} dataset={d} role={role} onClick={() => navigate(`/dataset/${d.id}`)} />
                            );
                        })}
                    </div>
                )}
            </section>
        </div>
    );
}

// --- Researcher Home ---

function ResearcherHome({
    myAssignments,
    myDatasets,
}: {
    myAssignments: DatasetAssignment[];
    myDatasets: Dataset[];
}) {
    const navigate = useNavigate();

    const needsWork = myDatasets.filter((d) => d.request_status === 'requested' && d.lifecycle === 'pending');
    const active = myDatasets.filter((d) => d.lifecycle === 'active');

    const sortedDatasets = [...myDatasets].sort(
        (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="Needs work" value={needsWork.length} icon={AlertCircle} />
                <StatCard label="Active" value={active.length} icon={CheckCircle2} />
                <StatCard label="My datasets" value={myDatasets.length} icon={Database} onClick={() => navigate('/datasets')} />
            </div>

            {/* Needs Work */}
            {needsWork.length > 0 && (
                <section>
                    <Card className="border-orange-200 bg-orange-50/30">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-orange-800">
                                <AlertCircle className="h-4 w-4" />
                                Needs Your Attention ({needsWork.length})
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {needsWork.map((d) => (
                                <DatasetRow key={d.id} dataset={d} onClick={() => navigate(`/dataset/${d.id}`)} />
                            ))}
                        </CardContent>
                    </Card>
                </section>
            )}

            {/* Research Inbox */}
            <section>
                <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                        Research Inbox ({sortedDatasets.length})
                    </h2>
                    <Button variant="ghost" size="sm" onClick={() => navigate('/datasets')}>
                        Browse All Datasets
                    </Button>
                </div>
                {sortedDatasets.length === 0 ? (
                    <Card>
                        <CardContent className="p-8 text-center">
                            <Inbox className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                            <p className="text-muted-foreground mb-1">No datasets in your inbox</p>
                            <p className="text-sm text-muted-foreground">
                                Browse datasets to self-assign, or wait for GTM to assign you.
                            </p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-2">
                        {sortedDatasets.map((d) => {
                            const role = myAssignments.find((a) => a.dataset_id === d.id)?.role;
                            return (
                                <DatasetRow key={d.id} dataset={d} role={role} onClick={() => navigate(`/dataset/${d.id}`)} />
                            );
                        })}
                    </div>
                )}
            </section>
        </div>
    );
}

// --- Main Page ---

export default function HomePage() {
    const currentUser = useCurrentUser();
    const role = currentUser?.role ?? 'customer';

    const { data: datasetsResponse } = useSearchDatasets({});
    const datasets = (datasetsResponse as { entities: Dataset[] } | undefined)?.entities ?? [];

    const { data: assignmentsResponse } = useSearchAssignments({});
    const allAssignments = (assignmentsResponse as { entities: DatasetAssignment[] } | undefined)?.entities ?? [];

    const myAssignments = allAssignments.filter((a) => a.user_id === currentUser?.id);
    const myDatasetIds = new Set(myAssignments.map((a) => a.dataset_id));
    const myDatasets = datasets.filter((d) => myDatasetIds.has(d.id));

    const greeting = role === 'customer' ? 'Dashboard' : role === 'gtm' ? 'GTM Dashboard' : 'Research Inbox';

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-bold">{greeting}</h1>
                        <p className="text-sm text-muted-foreground">
                            Welcome back, {currentUser?.name ?? 'User'}
                        </p>
                    </div>
                    <Badge variant="outline" className="text-xs capitalize">{role}</Badge>
                </div>

                {role === 'customer' && (
                    <CustomerHome myDatasets={myDatasets} />
                )}
                {role === 'gtm' && (
                    <GTMHome
                        datasets={datasets}
                        allAssignments={allAssignments}
                        myAssignments={myAssignments}
                        myDatasets={myDatasets}
                    />
                )}
                {role === 'researcher' && (
                    <ResearcherHome
                        myAssignments={myAssignments}
                        myDatasets={myDatasets}
                    />
                )}
            </div>
        </AppSidebar>
    );
}
