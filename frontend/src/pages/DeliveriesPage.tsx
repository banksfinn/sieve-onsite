import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
    useSearchDeliveries,
    useSearchDatasets,
    useSearchAssignments,
    useCreateDataset,
    Dataset,
    Delivery,
    DatasetAssignment,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import { Plus, Package, Database, ArrowRight, Clock, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const statusColors: Record<string, string> = {
    requested: 'bg-amber-100 text-amber-700',
    initialized: 'bg-blue-100 text-blue-700',
    active: 'bg-green-100 text-green-700',
    draft: 'bg-gray-100 text-gray-700',
    sent_to_customer: 'bg-blue-100 text-blue-700',
    in_review: 'bg-yellow-100 text-yellow-700',
    feedback_received: 'bg-purple-100 text-purple-700',
    iterating: 'bg-orange-100 text-orange-700',
    ready_for_approval: 'bg-cyan-100 text-cyan-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
};

function StatusBadge({ status }: { status: string }) {
    return (
        <Badge variant="outline" className={cn('text-xs font-medium', statusColors[status])}>
            {status.replace(/_/g, ' ')}
        </Badge>
    );
}

// --- Customer view: shows their dataset requests ---

function CustomerRequestCard({ dataset, onClick }: { dataset: Dataset; onClick: () => void }) {
    const status = dataset.status ?? 'requested';
    const statusLabel: Record<string, string> = {
        requested: 'Submitted — waiting for team to review',
        initialized: 'In progress — team is preparing samples',
        active: 'Samples ready for review',
    };

    return (
        <Card className="cursor-pointer hover:border-primary/50 transition-colors" onClick={onClick}>
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="font-medium truncate">{dataset.name}</span>
                            <StatusBadge status={status} />
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                            {statusLabel[status] ?? status}
                        </p>
                        {dataset.description && (
                            <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                                {dataset.description}
                            </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">
                            Submitted {new Date(dataset.created_at).toLocaleDateString()}
                        </p>
                    </div>
                    {status === 'active' ? (
                        <Badge className="bg-green-600 text-white text-xs flex-shrink-0">
                            Review
                        </Badge>
                    ) : (
                        <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

// --- GTM/Researcher view: shows deliveries ---

function DeliveryCard({ delivery, onClick }: { delivery: Delivery; onClick: () => void }) {
    return (
        <Card className="cursor-pointer hover:border-primary/50 transition-colors" onClick={onClick}>
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <Package className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="font-medium truncate">
                                Delivery #{delivery.id}
                            </span>
                            <StatusBadge status={delivery.status ?? 'draft'} />
                        </div>
                        {delivery.customer_request_description && (
                            <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                {delivery.customer_request_description}
                            </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">
                            Created {new Date(delivery.created_at).toLocaleDateString()}
                        </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
                </div>
            </CardContent>
        </Card>
    );
}

// --- Main page ---

export default function DeliveriesPage() {
    const navigate = useNavigate();
    const currentUser = useCurrentUser();
    const isCustomer = currentUser?.role === 'customer';

    const [createOpen, setCreateOpen] = useState(false);
    const [newDatasetName, setNewDatasetName] = useState('');
    const [newDescription, setNewDescription] = useState('');

    // GTM/Researcher: fetch deliveries
    const { data: deliveriesResponse, isLoading: deliveriesLoading } = useSearchDeliveries(
        {},
        { query: { enabled: !isCustomer } }
    );
    const deliveries = (deliveriesResponse as { entities: Delivery[] } | undefined)?.entities ?? [];

    // Customer: fetch their datasets (which are their requests)
    const { data: datasetsResponse, isLoading: datasetsLoading, refetch: refetchDatasets } = useSearchDatasets({});
    const allDatasets = (datasetsResponse as { entities: Dataset[] } | undefined)?.entities ?? [];

    const { data: assignmentsResponse } = useSearchAssignments(
        {},
        { query: { enabled: isCustomer } }
    );
    const assignments = (assignmentsResponse as { entities: DatasetAssignment[] } | undefined)?.entities ?? [];

    // Customer sees only datasets assigned to them
    const myDatasetIds = new Set(
        assignments.filter((a) => a.user_id === currentUser?.id).map((a) => a.dataset_id)
    );
    const myDatasets = isCustomer
        ? allDatasets.filter((d) => myDatasetIds.has(d.id))
        : [];

    const createDataset = useCreateDataset();

    const handleCreate = async () => {
        if (!newDatasetName.trim()) return;

        await createDataset.mutateAsync({
            data: {
                name: newDatasetName,
                description: newDescription || undefined,
            },
        });

        setCreateOpen(false);
        setNewDatasetName('');
        setNewDescription('');
        refetchDatasets();
    };

    const isPending = createDataset.isPending;
    const isLoading = isCustomer ? datasetsLoading : deliveriesLoading;

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold">
                        {isCustomer ? 'My Requests' : 'Deliveries'}
                    </h1>
                    <Button onClick={() => setCreateOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        {isCustomer ? 'Request a New Dataset' : 'New Delivery'}
                    </Button>
                </div>

                {isLoading ? (
                    <p className="text-muted-foreground text-center py-12">Loading...</p>
                ) : isCustomer ? (
                    /* Customer view: dataset requests */
                    myDatasets.length === 0 ? (
                        <div className="text-center py-12">
                            <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <p className="text-muted-foreground mb-2">No requests yet</p>
                            <p className="text-sm text-muted-foreground">
                                Request a dataset to get started.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {myDatasets.map((dataset) => (
                                <CustomerRequestCard
                                    key={dataset.id}
                                    dataset={dataset}
                                    onClick={() => navigate(`/dataset/${dataset.id}`)}
                                />
                            ))}
                        </div>
                    )
                ) : (
                    /* GTM/Researcher view: deliveries */
                    deliveries.length === 0 ? (
                        <div className="text-center py-12">
                            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <p className="text-muted-foreground mb-2">No deliveries yet</p>
                            <p className="text-sm text-muted-foreground">
                                Create a delivery to start sending samples to customers.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {deliveries.map((delivery) => (
                                <DeliveryCard
                                    key={delivery.id}
                                    delivery={delivery}
                                    onClick={() => navigate(`/delivery/${delivery.id}`)}
                                />
                            ))}
                        </div>
                    )
                )}
            </div>

            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>
                            {isCustomer ? 'Request a New Dataset' : 'Create New Delivery'}
                        </DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <div>
                            <label className="text-sm font-medium mb-1 block">
                                {isCustomer ? 'What do you need?' : 'Dataset Name'}
                            </label>
                            <Input
                                placeholder={isCustomer
                                    ? 'e.g. Full-body videos with face detection'
                                    : 'e.g. Customer X - Face Detection Samples'}
                                value={newDatasetName}
                                onChange={(e) => setNewDatasetName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">
                                {isCustomer ? 'Additional details' : 'Description (optional)'}
                            </label>
                            <Textarea
                                placeholder={isCustomer
                                    ? 'Describe your requirements — resolution, content type, metadata needs, quantity...'
                                    : 'What is this delivery for?'}
                                value={newDescription}
                                onChange={(e) => setNewDescription(e.target.value)}
                                rows={4}
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setCreateOpen(false)}>
                                Cancel
                            </Button>
                            <Button
                                onClick={handleCreate}
                                disabled={!newDatasetName.trim() || isPending}
                            >
                                {isPending ? 'Submitting...' : isCustomer ? 'Submit Request' : 'Create'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
