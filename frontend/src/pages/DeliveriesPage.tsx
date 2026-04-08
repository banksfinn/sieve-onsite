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
    useCreateDelivery,
    useCreateDataset,
    useCreateDatasetVersion,
    Delivery,
    DeliveryStatus,
} from '@/openapi/sieveBase';
import { Plus, Package, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

const statusColors: Record<string, string> = {
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

function DeliveryCard({ delivery, onClick }: { delivery: Delivery; onClick: () => void }) {
    return (
        <Card
            className="cursor-pointer hover:border-primary/50 transition-colors"
            onClick={onClick}
        >
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

export default function DeliveriesPage() {
    const navigate = useNavigate();
    const [createOpen, setCreateOpen] = useState(false);
    const [newDatasetName, setNewDatasetName] = useState('');
    const [newDescription, setNewDescription] = useState('');

    const { data: deliveriesResponse, isLoading, refetch: refetchDeliveries } = useSearchDeliveries({});
    const deliveries = (deliveriesResponse as { entities: Delivery[] } | undefined)?.entities ?? [];

    const createDataset = useCreateDataset();
    const createDatasetVersion = useCreateDatasetVersion();
    const createDelivery = useCreateDelivery();

    const handleCreate = async () => {
        if (!newDatasetName.trim()) return;

        // Create dataset -> version -> delivery
        const dataset = await createDataset.mutateAsync({ data: { name: newDatasetName } });
        const version = await createDatasetVersion.mutateAsync({
            datasetId: dataset.id,
            data: { dataset_id: dataset.id, version_number: 1, created_by: 0 },
        });
        await createDelivery.mutateAsync({
            data: {
                dataset_version_id: version.id,
                customer_request_description: newDescription || undefined,
                created_by: 0,
                status: DeliveryStatus.draft,
            },
        });

        setCreateOpen(false);
        setNewDatasetName('');
        setNewDescription('');
        refetchDeliveries();
    };

    const isPending = createDataset.isPending || createDatasetVersion.isPending || createDelivery.isPending;

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold">Deliveries</h1>
                    <Button onClick={() => setCreateOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        New Delivery
                    </Button>
                </div>

                {isLoading ? (
                    <p className="text-muted-foreground text-center py-12">Loading deliveries...</p>
                ) : deliveries.length === 0 ? (
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
                )}
            </div>

            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create New Delivery</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 pt-2">
                        <div>
                            <label className="text-sm font-medium mb-1 block">Dataset Name</label>
                            <Input
                                placeholder="e.g. Customer X - Face Detection Samples"
                                value={newDatasetName}
                                onChange={(e) => setNewDatasetName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">
                                Description (optional)
                            </label>
                            <Textarea
                                placeholder="What is this delivery for?"
                                value={newDescription}
                                onChange={(e) => setNewDescription(e.target.value)}
                                rows={3}
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
                                {isPending ? 'Creating...' : 'Create'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </AppSidebar>
    );
}
