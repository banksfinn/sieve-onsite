import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
    useGetDelivery,
    useUpdateDelivery,
    useSearchClips,
    useSearchClipFeedback,
    useCreateClipFeedback,
    useSearchDeliveryFeedback,
    useCreateDeliveryFeedback,
    Clip,
    ClipFeedback,
    ClipRating,
    DeliveryStatus,
    DeliveryFeedbackStatus,
    getSearchClipFeedbackQueryKey,
    getSearchDeliveryFeedbackQueryKey,
} from '@/openapi/sieveBase';
import {
    ArrowLeft,
    Play,
    ThumbsUp,
    ThumbsDown,
    HelpCircle,
    ChevronLeft,
    ChevronRight,
    Send,
    Film,
} from 'lucide-react';
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

const ratingConfig = {
    good: { icon: ThumbsUp, label: 'Good', color: 'text-green-600 bg-green-50 border-green-200' },
    bad: { icon: ThumbsDown, label: 'Bad', color: 'text-red-600 bg-red-50 border-red-200' },
    unsure: { icon: HelpCircle, label: 'Unsure', color: 'text-yellow-600 bg-yellow-50 border-yellow-200' },
};

function ClipCard({
    clip,
    isSelected,
    feedback,
    onClick,
}: {
    clip: Clip;
    isSelected: boolean;
    feedback: ClipFeedback | undefined;
    onClick: () => void;
}) {
    return (
        <Card
            className={cn(
                'cursor-pointer transition-all hover:border-primary/50',
                isSelected && 'ring-2 ring-primary border-primary'
            )}
            onClick={onClick}
        >
            <CardContent className="p-3">
                <div className="aspect-video bg-muted rounded flex items-center justify-center mb-2">
                    <Play className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="space-y-1">
                    <p className="text-xs font-medium truncate">Clip #{clip.id}</p>
                    <p className="text-xs text-muted-foreground">
                        {clip.duration.toFixed(1)}s
                    </p>
                    {feedback && (
                        <Badge
                            variant="outline"
                            className={cn('text-xs', ratingConfig[feedback.rating]?.color)}
                        >
                            {ratingConfig[feedback.rating]?.label}
                        </Badge>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

function ClipViewer({
    clip,
    feedback,
    deliveryId,
    onFeedbackSubmitted,
}: {
    clip: Clip;
    feedback: ClipFeedback | undefined;
    deliveryId: number;
    onFeedbackSubmitted: () => void;
}) {
    const [rating, setRating] = useState<ClipRating | null>(feedback?.rating ?? null);
    const [comment, setComment] = useState(feedback?.comment ?? '');

    const createFeedback = useCreateClipFeedback();

    const handleSubmit = () => {
        if (!rating) return;
        createFeedback.mutate(
            {
                deliveryId,
                clipId: clip.id,
                data: {
                    clip_id: clip.id,
                    delivery_id: deliveryId,
                    user_id: 0,
                    rating,
                    comment: comment || undefined,
                },
            },
            { onSuccess: onFeedbackSubmitted }
        );
    };

    return (
        <div className="space-y-4">
            {/* Video player */}
            <div className="aspect-video bg-black rounded-lg flex items-center justify-center">
                <video
                    src={clip.uri}
                    controls
                    className="w-full h-full rounded-lg"
                    key={clip.id}
                >
                    <track kind="captions" />
                </video>
            </div>

            {/* Clip metadata */}
            <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="bg-muted/50 rounded p-2">
                    <span className="text-muted-foreground">Duration</span>
                    <p className="font-medium">{clip.duration.toFixed(2)}s</p>
                </div>
                <div className="bg-muted/50 rounded p-2">
                    <span className="text-muted-foreground">Time Range</span>
                    <p className="font-medium">{clip.start_time.toFixed(2)}s - {clip.end_time.toFixed(2)}s</p>
                </div>
                {clip.avg_face_size != null && (
                    <div className="bg-muted/50 rounded p-2">
                        <span className="text-muted-foreground">Avg Face Size</span>
                        <p className="font-medium">{clip.avg_face_size}</p>
                    </div>
                )}
                {clip.max_num_faces != null && (
                    <div className="bg-muted/50 rounded p-2">
                        <span className="text-muted-foreground">Max Faces</span>
                        <p className="font-medium">{clip.max_num_faces}</p>
                    </div>
                )}
                {clip.is_full_body != null && (
                    <div className="bg-muted/50 rounded p-2">
                        <span className="text-muted-foreground">Full Body</span>
                        <p className="font-medium">{clip.is_full_body ? 'Yes' : 'No'}</p>
                    </div>
                )}
                {clip.has_overlay != null && (
                    <div className="bg-muted/50 rounded p-2">
                        <span className="text-muted-foreground">Has Overlay</span>
                        <p className="font-medium">{clip.has_overlay ? 'Yes' : 'No'}</p>
                    </div>
                )}
            </div>

            {/* Feedback form */}
            <div className="border rounded-lg p-4 space-y-3">
                <h3 className="text-sm font-medium">Feedback</h3>
                <div className="flex gap-2">
                    {(Object.entries(ratingConfig) as [ClipRating, typeof ratingConfig.good][]).map(
                        ([value, config]) => {
                            const Icon = config.icon;
                            return (
                                <Button
                                    key={value}
                                    variant="outline"
                                    size="sm"
                                    className={cn(
                                        'flex-1',
                                        rating === value && config.color
                                    )}
                                    onClick={() => setRating(value)}
                                >
                                    <Icon className="h-4 w-4 mr-1" />
                                    {config.label}
                                </Button>
                            );
                        }
                    )}
                </div>
                <Textarea
                    placeholder="Add a comment (optional)..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={2}
                    className="text-sm"
                />
                <Button
                    size="sm"
                    className="w-full"
                    disabled={!rating || createFeedback.isPending}
                    onClick={handleSubmit}
                >
                    <Send className="h-4 w-4 mr-1" />
                    {createFeedback.isPending ? 'Submitting...' : 'Submit Feedback'}
                </Button>
            </div>
        </div>
    );
}

export default function DeliveryDetailPage() {
    const { deliveryId } = useParams<{ deliveryId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const id = Number(deliveryId);

    const [selectedClipIndex, setSelectedClipIndex] = useState(0);
    const [deliveryComment, setDeliveryComment] = useState('');
    const [deliveryVerdict, setDeliveryVerdict] = useState<DeliveryFeedbackStatus | ''>('');

    const { data: delivery } = useGetDelivery(id);
    const { data: clipsResponse } = useSearchClips({ dataset_version_id: delivery?.dataset_version_id });
    const clips = (clipsResponse as { entities: Clip[] } | undefined)?.entities ?? [];

    const { data: clipFeedbackResponse } = useSearchClipFeedback(id, clips[selectedClipIndex]?.id ?? 0, {
        query: { enabled: !!clips[selectedClipIndex] },
    });
    const allClipFeedback = (clipFeedbackResponse as { entities: ClipFeedback[] } | undefined)?.entities ?? [];
    const currentClipFeedback = allClipFeedback[0];

    const { data: deliveryFeedbackResponse } = useSearchDeliveryFeedback(id);
    const deliveryFeedbacks = (deliveryFeedbackResponse as { entities: { id: number; status: string; summary: string; created_at: string }[] } | undefined)?.entities ?? [];

    const updateDelivery = useUpdateDelivery();
    const createDeliveryFeedback = useCreateDeliveryFeedback();

    const selectedClip = clips[selectedClipIndex];
    const totalClips = clips.length;
    const handleStatusChange = (newStatus: string) => {
        updateDelivery.mutate({
            deliveryId: id,
            data: { id, status: newStatus as DeliveryStatus },
        });
    };

    const handleDeliveryFeedback = () => {
        if (!deliveryVerdict) return;
        createDeliveryFeedback.mutate(
            {
                deliveryId: id,
                data: {
                    delivery_id: id,
                    user_id: 0,
                    status: deliveryVerdict,
                    summary: deliveryComment || undefined,
                },
            },
            {
                onSuccess: () => {
                    setDeliveryComment('');
                    setDeliveryVerdict('');
                    queryClient.invalidateQueries({ queryKey: getSearchDeliveryFeedbackQueryKey(id) });
                },
            }
        );
    };

    return (
        <AppSidebar>
            <div className="h-full flex flex-col">
                {/* Header */}
                <div className="border-b px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Button variant="ghost" size="icon" onClick={() => navigate('/deliveries')}>
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-lg font-semibold">
                                    Delivery #{deliveryId}
                                </h1>
                                {delivery?.status && (
                                    <Badge
                                        variant="outline"
                                        className={cn('text-xs', statusColors[delivery.status])}
                                    >
                                        {delivery.status.replace(/_/g, ' ')}
                                    </Badge>
                                )}
                            </div>
                            {delivery?.customer_request_description && (
                                <p className="text-sm text-muted-foreground">
                                    {delivery.customer_request_description}
                                </p>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">
                            {totalClips} clips
                        </span>
                        <Select
                            value={delivery?.status ?? ''}
                            onValueChange={handleStatusChange}
                        >
                            <SelectTrigger className="w-48">
                                <SelectValue placeholder="Update status" />
                            </SelectTrigger>
                            <SelectContent>
                                {Object.values(DeliveryStatus).map((s) => (
                                    <SelectItem key={s} value={s}>
                                        {s.replace(/_/g, ' ')}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                {/* Main content: clip grid + viewer */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Clip grid (left panel) */}
                    <div className="w-64 border-r overflow-y-auto p-3 space-y-2">
                        {clips.length === 0 ? (
                            <div className="text-center py-8">
                                <Film className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">No clips loaded</p>
                            </div>
                        ) : (
                            clips.map((clip, index) => (
                                <ClipCard
                                    key={clip.id}
                                    clip={clip}
                                    isSelected={index === selectedClipIndex}
                                    feedback={undefined}
                                    onClick={() => setSelectedClipIndex(index)}
                                />
                            ))
                        )}
                    </div>

                    {/* Clip viewer (center) */}
                    <div className="flex-1 overflow-y-auto p-6">
                        {selectedClip ? (
                            <div className="max-w-3xl mx-auto">
                                {/* Navigation */}
                                <div className="flex items-center justify-between mb-4">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        disabled={selectedClipIndex === 0}
                                        onClick={() => setSelectedClipIndex((i) => i - 1)}
                                    >
                                        <ChevronLeft className="h-4 w-4 mr-1" />
                                        Previous
                                    </Button>
                                    <div className="flex items-center gap-3">
                                        <span className="text-sm text-muted-foreground">
                                            {selectedClipIndex + 1} of {totalClips}
                                        </span>
                                        <Button
                                            variant="default"
                                            size="sm"
                                            onClick={() => navigate(`/delivery/${id}/clip/${selectedClip.id}`)}
                                        >
                                            Open Full Viewer
                                        </Button>
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        disabled={selectedClipIndex === totalClips - 1}
                                        onClick={() => setSelectedClipIndex((i) => i + 1)}
                                    >
                                        Next
                                        <ChevronRight className="h-4 w-4 ml-1" />
                                    </Button>
                                </div>

                                <ClipViewer
                                    clip={selectedClip}
                                    feedback={currentClipFeedback}
                                    deliveryId={id}
                                    onFeedbackSubmitted={() => {
                                        queryClient.invalidateQueries({
                                            queryKey: getSearchClipFeedbackQueryKey(id, selectedClip.id),
                                        });
                                    }}
                                />
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                Select a clip to review
                            </div>
                        )}
                    </div>

                    {/* Delivery feedback panel (right) */}
                    <div className="w-80 border-l overflow-y-auto p-4 space-y-4">
                        <h2 className="font-medium text-sm">Delivery Feedback</h2>

                        {/* Existing feedback */}
                        {deliveryFeedbacks.length > 0 && (
                            <div className="space-y-2">
                                {deliveryFeedbacks.map((fb) => (
                                    <div key={fb.id} className="border rounded p-3 text-sm space-y-1">
                                        <Badge
                                            variant="outline"
                                            className={cn(
                                                'text-xs',
                                                fb.status === 'approved' && 'bg-green-50 text-green-700',
                                                fb.status === 'needs_changes' && 'bg-yellow-50 text-yellow-700',
                                                fb.status === 'rejected' && 'bg-red-50 text-red-700'
                                            )}
                                        >
                                            {fb.status.replace(/_/g, ' ')}
                                        </Badge>
                                        {fb.summary && (
                                            <p className="text-muted-foreground">{fb.summary}</p>
                                        )}
                                        <p className="text-xs text-muted-foreground">
                                            {new Date(fb.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* New feedback form */}
                        <div className="border rounded-lg p-3 space-y-3">
                            <h3 className="text-sm font-medium">Overall Verdict</h3>
                            <Select
                                value={deliveryVerdict}
                                onValueChange={(v) => setDeliveryVerdict(v as DeliveryFeedbackStatus)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select verdict..." />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="approved">Approved</SelectItem>
                                    <SelectItem value="needs_changes">Needs Changes</SelectItem>
                                    <SelectItem value="rejected">Rejected</SelectItem>
                                </SelectContent>
                            </Select>
                            <Textarea
                                placeholder="Summary of feedback..."
                                value={deliveryComment}
                                onChange={(e) => setDeliveryComment(e.target.value)}
                                rows={3}
                                className="text-sm"
                            />
                            <Button
                                size="sm"
                                className="w-full"
                                disabled={!deliveryVerdict || createDeliveryFeedback.isPending}
                                onClick={handleDeliveryFeedback}
                            >
                                Submit Verdict
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </AppSidebar>
    );
}
