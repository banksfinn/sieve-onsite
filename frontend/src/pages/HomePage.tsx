import { useNavigate } from 'react-router-dom';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
    useSearchDatasets,
    useSearchAssignments,
    useSearchDeliveries,
    Dataset,
    DatasetAssignment,
    Delivery,
} from '@/openapi/sieveOnsite';
import { useCurrentUser } from '@/store/components/authSlice';
import {
    Database,
    Package,
    ArrowRight,
    Inbox,
    AlertCircle,
    Clock,
    CheckCircle2,
    Plus,
} from 'lucide-react';

const statusColors: Record<string, string> = {
    requested: 'bg-amber-100 text-amber-700',
    draft: 'bg-gray-100 text-gray-700',
    sent_to_customer: 'bg-blue-100 text-blue-700',
    in_review: 'bg-yellow-100 text-yellow-700',
    feedback_received: 'bg-purple-100 text-purple-700',
    iterating: 'bg-orange-100 text-orange-700',
    ready_for_approval: 'bg-cyan-100 text-cyan-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
};

// --- Shared Components ---

function DeliveryRow({ delivery, onClick }: { delivery: Delivery; onClick: () => void }) {
    const status = delivery.status ?? 'requested';
    return (
        <button
            onClick={onClick}
            className="w-full flex items-center justify-between p-3 rounded-lg border hover:border-primary/50 transition-colors text-left"
        >
            <div className="flex items-center gap-3 min-w-0">
                <Package className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <div className="min-w-0">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Delivery #{delivery.id}</span>
                        <Badge variant="outline" className={`text-xs ${statusColors[status]}`}>
                            {status.replace(/_/g, ' ')}
                        </Badge>
                    </div>
                    {delivery.customer_request_description && (
                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                            {delivery.customer_request_description}
                        </p>
                    )}
                </div>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
        </button>
    );
}

function DatasetRow({
    dataset,
    role,
    onClick,
}: {
    dataset: Dataset;
    role?: string;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className="w-full flex items-center justify-between p-3 rounded-lg border hover:border-primary/50 transition-colors text-left"
        >
            <div className="flex items-center gap-3">
                <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <div>
                    <span className="text-sm font-medium">{dataset.name}</span>
                    {role && (
                        <Badge variant="outline" className="ml-2 text-xs">
                            {role.replace(/_/g, ' ')}
                        </Badge>
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
    icon: typeof Package;
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

// --- Customer Home ---

function CustomerHome({
    myDatasets,
    myAssignments,
    deliveries,
}: {
    myDatasets: Dataset[];
    myAssignments: DatasetAssignment[];
    deliveries: Delivery[];
}) {
    const navigate = useNavigate();

    // Deliveries the customer can review (sent_to_customer or in_review)
    const reviewable = deliveries.filter(
        (d) => d.status === 'sent_to_customer' || d.status === 'in_review'
    );
    const pending = deliveries.filter((d) => d.status === 'requested');
    const completed = deliveries.filter((d) => d.status === 'approved');

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard label="Pending requests" value={pending.length} icon={Clock} />
                <StatCard
                    label="Ready to review"
                    value={reviewable.length}
                    icon={AlertCircle}
                    onClick={reviewable.length > 0 ? () => navigate('/deliveries') : undefined}
                />
                <StatCard label="Completed" value={completed.length} icon={CheckCircle2} />
            </div>

            {/* Ready to Review */}
            {reviewable.length > 0 && (
                <section>
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                        Ready for Your Review
                    </h2>
                    <div className="space-y-2">
                        {reviewable.map((d) => (
                            <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
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
                    <Button variant="outline" size="sm" onClick={() => navigate('/deliveries')}>
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
                        {myDatasets.map((d) => {
                            const role = myAssignments.find((a) => a.dataset_id === d.id)?.role;
                            return (
                                <DatasetRow key={d.id} dataset={d} role={role} onClick={() => navigate(`/dataset/${d.id}`)} />
                            );
                        })}
                    </div>
                )}
            </section>

            {/* Pending Requests */}
            {pending.length > 0 && (
                <section>
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                        Pending Requests
                    </h2>
                    <div className="space-y-2">
                        {pending.map((d) => (
                            <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}

// --- GTM Home ---

function GTMHome({
    datasets,
    allAssignments,
    myAssignments,
    myDatasets,
    deliveries,
}: {
    datasets: Dataset[];
    allAssignments: DatasetAssignment[];
    myAssignments: DatasetAssignment[];
    myDatasets: Dataset[];
    deliveries: Delivery[];
}) {
    const navigate = useNavigate();

    // New customer requests needing GTM attention
    const newRequests = deliveries.filter((d) => d.status === 'requested');

    // Unassigned datasets (no GTM lead)
    const unassignedDatasets = datasets.filter(
        (d) => !allAssignments.some((a) => a.dataset_id === d.id && a.role === 'gtm_lead')
    );

    // Active deliveries (not approved/rejected)
    const activeDeliveries = deliveries.filter(
        (d) => d.status !== 'approved' && d.status !== 'rejected' && d.status !== 'requested'
    );

    // Deliveries with feedback needing attention
    const feedbackDeliveries = deliveries.filter((d) => d.status === 'feedback_received');

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <StatCard
                    label="New requests"
                    value={newRequests.length}
                    icon={AlertCircle}
                    onClick={newRequests.length > 0 ? () => navigate('/deliveries') : undefined}
                />
                <StatCard label="Unassigned datasets" value={unassignedDatasets.length} icon={Database} onClick={() => navigate('/datasets')} />
                <StatCard label="Active deliveries" value={activeDeliveries.length} icon={Package} />
                <StatCard label="Feedback waiting" value={feedbackDeliveries.length} icon={Clock} />
            </div>

            {/* New Customer Requests */}
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
                                <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
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

            {/* Active Deliveries */}
            {activeDeliveries.length > 0 && (
                <section>
                    <div className="flex items-center justify-between mb-3">
                        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                            Active Deliveries ({activeDeliveries.length})
                        </h2>
                        <Button variant="ghost" size="sm" onClick={() => navigate('/deliveries')}>
                            View All
                        </Button>
                    </div>
                    <div className="space-y-2">
                        {activeDeliveries.slice(0, 5).map((d) => (
                            <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}

// --- Researcher Home ---

function ResearcherHome({
    myAssignments,
    myDatasets,
    deliveries,
}: {
    myAssignments: DatasetAssignment[];
    myDatasets: Dataset[];
    deliveries: Delivery[];
}) {
    const navigate = useNavigate();

    // Deliveries in iterating or feedback_received (need researcher work)
    const needsWork = deliveries.filter(
        (d) => d.status === 'iterating' || d.status === 'feedback_received'
    );

    // Deliveries in draft (researcher preparing)
    const inDraft = deliveries.filter((d) => d.status === 'draft');

    // Datasets sorted by most recently updated
    const sortedDatasets = [...myDatasets].sort(
        (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );

    return (
        <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <StatCard
                    label="Needs iteration"
                    value={needsWork.length}
                    icon={AlertCircle}
                    onClick={needsWork.length > 0 ? () => navigate('/deliveries') : undefined}
                />
                <StatCard label="In draft" value={inDraft.length} icon={Clock} />
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
                                <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
                            ))}
                        </CardContent>
                    </Card>
                </section>
            )}

            {/* Inbox: My Datasets */}
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

            {/* In Draft */}
            {inDraft.length > 0 && (
                <section>
                    <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                        In Draft ({inDraft.length})
                    </h2>
                    <div className="space-y-2">
                        {inDraft.map((d) => (
                            <DeliveryRow key={d.id} delivery={d} onClick={() => navigate(`/delivery/${d.id}`)} />
                        ))}
                    </div>
                </section>
            )}
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

    const { data: deliveriesResponse } = useSearchDeliveries({});
    const deliveries = (deliveriesResponse as { entities: Delivery[] } | undefined)?.entities ?? [];

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
                    <CustomerHome
                        myDatasets={myDatasets}
                        myAssignments={myAssignments}
                        deliveries={deliveries}
                    />
                )}
                {role === 'gtm' && (
                    <GTMHome
                        datasets={datasets}
                        allAssignments={allAssignments}
                        myAssignments={myAssignments}
                        myDatasets={myDatasets}
                        deliveries={deliveries}
                    />
                )}
                {role === 'researcher' && (
                    <ResearcherHome
                        myAssignments={myAssignments}
                        myDatasets={myDatasets}
                        deliveries={deliveries}
                    />
                )}
            </div>
        </AppSidebar>
    );
}
