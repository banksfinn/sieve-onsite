import { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import {
    useGetClip,
    useSearchClipFeedback,
    useCreateClipFeedback,
    useUpdateClipFeedback,
    useSearchDatasetVersions,
    useGetDelivery,
    ClipFeedback,
    ClipRating,
    DatasetVersion,
    getSearchClipFeedbackQueryKey,
} from '@/openapi/sieveBase';
import {
    ArrowLeft,
    ThumbsUp,
    ThumbsDown,
    HelpCircle,
    Clock,
    Tag,
    CheckCircle2,
    Circle,
    Send,
    ChevronDown,
    ChevronUp,
    GripHorizontal,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const METADATA_FIELDS = [
    { key: 'avg_face_size', label: 'Avg Face Size' },
    { key: 'max_num_faces', label: 'Max Faces' },
    { key: 'is_full_body', label: 'Full Body' },
    { key: 'has_overlay', label: 'Has Overlay' },
    { key: 'duration', label: 'Duration' },
    { key: 'start_time', label: 'Start Time' },
    { key: 'end_time', label: 'End Time' },
] as const;

const ratingConfig = {
    good: { icon: ThumbsUp, label: 'Good', color: 'text-green-600 bg-green-50 border-green-200', hoverColor: 'hover:bg-green-50' },
    bad: { icon: ThumbsDown, label: 'Bad', color: 'text-red-600 bg-red-50 border-red-200', hoverColor: 'hover:bg-red-50' },
    unsure: { icon: HelpCircle, label: 'Unsure', color: 'text-yellow-600 bg-yellow-50 border-yellow-200', hoverColor: 'hover:bg-yellow-50' },
};

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
}

// --- Metadata Panel (time-synced) ---
function MetadataPanel({
    clip,
    currentTime,
    clipStartTime,
    onFieldClick,
    highlightedField,
}: {
    clip: { avg_face_size?: number | null; max_num_faces?: number | null; is_full_body?: boolean | null; has_overlay?: boolean | null; duration: number; start_time: number; end_time: number };
    currentTime: number;
    clipStartTime: number;
    onFieldClick: (field: string) => void;
    highlightedField: string | null;
}) {
    const videoTime = clipStartTime + currentTime;
    const progress = clip.duration > 0 ? (currentTime / clip.duration) * 100 : 0;

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Clip Metadata</h3>
                <span className="text-xs text-muted-foreground font-mono">
                    {formatTime(videoTime)} in source
                </span>
            </div>

            {/* Time progress bar */}
            <div className="space-y-1">
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                        className="h-full bg-primary rounded-full transition-all duration-100"
                        style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                </div>
                <div className="flex justify-between text-xs text-muted-foreground font-mono">
                    <span>{formatTime(clip.start_time)}</span>
                    <span>{formatTime(clip.end_time)}</span>
                </div>
            </div>

            <Separator />

            {/* Metadata fields */}
            <div className="space-y-1">
                {METADATA_FIELDS.map(({ key, label }) => {
                    const value = clip[key as keyof typeof clip];
                    if (value === null || value === undefined) return null;
                    const isHighlighted = highlightedField === key;
                    const displayValue = typeof value === 'boolean' ? (value ? 'Yes' : 'No') : typeof value === 'number' ? value.toFixed(2) : String(value);

                    return (
                        <button
                            key={key}
                            onClick={() => onFieldClick(key)}
                            className={cn(
                                'w-full flex items-center justify-between p-2 rounded text-sm transition-colors',
                                isHighlighted
                                    ? 'bg-primary/10 ring-1 ring-primary/30'
                                    : 'hover:bg-muted/80'
                            )}
                        >
                            <span className="text-muted-foreground">{label}</span>
                            <span className={cn('font-mono font-medium', isHighlighted && 'text-primary')}>
                                {displayValue}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

// --- Feedback Item ---
function FeedbackItem({
    feedback,
    onResolve,
    onSeek,
    isResolving,
}: {
    feedback: ClipFeedback;
    onResolve: (id: number) => void;
    onSeek: (time: number) => void;
    isResolving: boolean;
}) {
    const config = ratingConfig[feedback.rating];
    const Icon = config.icon;

    return (
        <div className={cn(
            'border rounded-lg p-3 space-y-2 transition-opacity',
            feedback.is_resolved && 'opacity-50'
        )}>
            <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                    <Icon className={cn('h-4 w-4', config.color.split(' ')[0])} />
                    <Badge variant="outline" className={cn('text-xs', config.color)}>
                        {config.label}
                    </Badge>
                    {feedback.metadata_field && (
                        <Badge variant="secondary" className="text-xs">
                            <Tag className="h-3 w-3 mr-1" />
                            {METADATA_FIELDS.find(f => f.key === feedback.metadata_field)?.label ?? feedback.metadata_field}
                        </Badge>
                    )}
                </div>
                <button
                    onClick={() => onResolve(feedback.id)}
                    disabled={isResolving || feedback.is_resolved}
                    className="flex-shrink-0"
                    title={feedback.is_resolved ? 'Resolved' : 'Mark as resolved'}
                >
                    {feedback.is_resolved ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                        <Circle className="h-4 w-4 text-muted-foreground hover:text-green-500 transition-colors" />
                    )}
                </button>
            </div>

            {feedback.comment && (
                <p className="text-sm">{feedback.comment}</p>
            )}

            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                {feedback.timestamp != null && (
                    <button
                        onClick={() => onSeek(feedback.timestamp!)}
                        className="flex items-center gap-1 hover:text-primary transition-colors"
                    >
                        <Clock className="h-3 w-3" />
                        {formatTime(feedback.timestamp)}
                    </button>
                )}
                <span>{new Date(feedback.created_at).toLocaleString()}</span>
            </div>
        </div>
    );
}

// --- Feedback Form ---
function FeedbackForm({
    deliveryId,
    clipId,
    currentTime,
    selectedField,
    onSubmitted,
}: {
    deliveryId: number;
    clipId: number;
    currentTime: number;
    selectedField: string | null;
    onSubmitted: () => void;
}) {
    const [rating, setRating] = useState<ClipRating | null>(null);
    const [comment, setComment] = useState('');
    const [capturedTime, setCapturedTime] = useState<number | null>(null);
    const [attachField, setAttachField] = useState(selectedField);

    useEffect(() => {
        setAttachField(selectedField);
    }, [selectedField]);

    const createFeedback = useCreateClipFeedback();

    const handleSubmit = () => {
        if (!rating) return;
        createFeedback.mutate(
            {
                deliveryId,
                clipId,
                data: {
                    clip_id: clipId,
                    delivery_id: deliveryId,
                    user_id: 0,
                    rating,
                    comment: comment || undefined,
                    timestamp: capturedTime ?? undefined,
                    metadata_field: attachField ?? undefined,
                },
            },
            {
                onSuccess: () => {
                    setRating(null);
                    setComment('');
                    setCapturedTime(null);
                    setAttachField(null);
                    onSubmitted();
                },
            }
        );
    };

    return (
        <div className="border rounded-lg p-4 space-y-3 bg-card">
            <h3 className="text-sm font-semibold">Add Feedback</h3>

            {/* Rating buttons */}
            <div className="flex gap-2">
                {(Object.entries(ratingConfig) as [ClipRating, typeof ratingConfig.good][]).map(
                    ([value, config]) => {
                        const Icon = config.icon;
                        return (
                            <Button
                                key={value}
                                variant="outline"
                                size="sm"
                                className={cn('flex-1', rating === value && config.color)}
                                onClick={() => setRating(value)}
                            >
                                <Icon className="h-4 w-4 mr-1" />
                                {config.label}
                            </Button>
                        );
                    }
                )}
            </div>

            {/* Timestamp capture */}
            <div className="flex items-center gap-2">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCapturedTime(currentTime)}
                    className="text-xs"
                >
                    <Clock className="h-3 w-3 mr-1" />
                    {capturedTime != null ? `@ ${formatTime(capturedTime)}` : 'Pin timestamp'}
                </Button>
                {capturedTime != null && (
                    <Button variant="ghost" size="sm" onClick={() => setCapturedTime(null)} className="text-xs h-7 px-2">
                        Clear
                    </Button>
                )}
            </div>

            {/* Metadata field selector */}
            <Select value={attachField ?? ''} onValueChange={(v) => setAttachField(v || null)}>
                <SelectTrigger className="text-xs h-8">
                    <SelectValue placeholder="Link to metadata field (optional)" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {METADATA_FIELDS.map(({ key, label }) => (
                        <SelectItem key={key} value={key}>{label}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Textarea
                placeholder="Describe the issue or observation..."
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
                {createFeedback.isPending ? 'Submitting...' : 'Submit'}
            </Button>
        </div>
    );
}

// --- Boundary Adjuster ---
function BoundaryAdjuster({
    startTime,
    endTime,
    onAdjust,
}: {
    startTime: number;
    endTime: number;
    onAdjust: (newStart: number, newEnd: number) => void;
}) {
    const [adjStart, setAdjStart] = useState(startTime);
    const [adjEnd, setAdjEnd] = useState(endTime);
    const [expanded, setExpanded] = useState(false);

    return (
        <div className="border rounded-lg overflow-hidden">
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between p-3 text-sm font-medium hover:bg-muted/50 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <GripHorizontal className="h-4 w-4 text-muted-foreground" />
                    Adjust Clip Boundaries
                </div>
                {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {expanded && (
                <div className="p-3 pt-0 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs text-muted-foreground mb-1 block">Start Time (s)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={adjStart}
                                onChange={(e) => setAdjStart(parseFloat(e.target.value))}
                                className="w-full rounded border px-2 py-1 text-sm font-mono"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-muted-foreground mb-1 block">End Time (s)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={adjEnd}
                                onChange={(e) => setAdjEnd(parseFloat(e.target.value))}
                                className="w-full rounded border px-2 py-1 text-sm font-mono"
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Duration: {(adjEnd - adjStart).toFixed(2)}s</span>
                        <span className="text-muted-foreground/50">|</span>
                        <span>
                            Delta: {adjStart !== startTime ? `start ${(adjStart - startTime).toFixed(1)}s` : ''}
                            {adjEnd !== endTime ? ` end ${(adjEnd - endTime).toFixed(1)}s` : ''}
                            {adjStart === startTime && adjEnd === endTime ? 'no change' : ''}
                        </span>
                    </div>
                    <Button
                        size="sm"
                        variant="outline"
                        className="w-full"
                        disabled={adjStart === startTime && adjEnd === endTime}
                        onClick={() => onAdjust(adjStart, adjEnd)}
                    >
                        Save Boundary Change
                    </Button>
                </div>
            )}
        </div>
    );
}

// --- Version Selector ---
function VersionSelector({
    versions,
    currentVersionId,
    onSelect,
}: {
    versions: DatasetVersion[];
    currentVersionId: number;
    onSelect: (versionId: number) => void;
}) {
    if (versions.length <= 1) return null;

    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Version:</span>
            <div className="flex gap-1">
                {versions.map((v) => (
                    <Button
                        key={v.id}
                        variant={v.id === currentVersionId ? 'default' : 'outline'}
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => onSelect(v.id)}
                    >
                        v{v.version_number}
                    </Button>
                ))}
            </div>
        </div>
    );
}

// --- Main Page ---
export default function ClipViewerPage() {
    const { deliveryId, clipId } = useParams<{ deliveryId: string; clipId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const videoRef = useRef<HTMLVideoElement>(null);

    const dId = Number(deliveryId);
    const cId = Number(clipId);

    const [currentTime, setCurrentTime] = useState(0);
    const [highlightedField, setHighlightedField] = useState<string | null>(null);
    const [showResolved, setShowResolved] = useState(false);

    const { data: delivery } = useGetDelivery(dId);
    const { data: clip } = useGetClip(cId);

    // Fetch versions for the dataset this clip belongs to
    // useSearchDatasetVersions takes datasetId as first param
    const { data: versionsResponse } = useSearchDatasetVersions(
        clip?.dataset_version_id ?? 0,
        { query: { enabled: !!clip } }
    );
    const versions = (versionsResponse as { entities: DatasetVersion[] } | undefined)?.entities ?? [];

    // Feedback for this clip in this delivery
    const { data: feedbackResponse } = useSearchClipFeedback(dId, cId);
    const allFeedback = (feedbackResponse as { entities: ClipFeedback[] } | undefined)?.entities ?? [];
    const filteredFeedback = showResolved ? allFeedback : allFeedback.filter((f) => !f.is_resolved);

    const updateFeedback = useUpdateClipFeedback();

    // Track video time
    const handleTimeUpdate = useCallback(() => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    }, []);

    const seekTo = useCallback((time: number) => {
        if (videoRef.current) {
            videoRef.current.currentTime = time;
            setCurrentTime(time);
        }
    }, []);

    const handleResolve = (feedbackId: number) => {
        updateFeedback.mutate(
            {
                deliveryId: dId,
                clipId: cId,
                feedbackId,
                data: {
                    id: feedbackId,
                    is_resolved: true,
                    resolved_in_version_id: clip?.dataset_version_id ?? undefined,
                },
            },
            {
                onSuccess: () => {
                    queryClient.invalidateQueries({ queryKey: getSearchClipFeedbackQueryKey(dId, cId) });
                },
            }
        );
    };

    const handleFieldClick = (field: string) => {
        setHighlightedField((prev) => (prev === field ? null : field));
    };

    const invalidateFeedback = () => {
        queryClient.invalidateQueries({ queryKey: getSearchClipFeedbackQueryKey(dId, cId) });
    };

    const unresolvedCount = allFeedback.filter((f) => !f.is_resolved).length;
    const resolvedCount = allFeedback.filter((f) => f.is_resolved).length;

    if (!clip) {
        return (
            <AppSidebar>
                <div className="flex items-center justify-center h-full text-muted-foreground">
                    Loading clip...
                </div>
            </AppSidebar>
        );
    }

    return (
        <AppSidebar>
            <div className="h-full flex flex-col">
                {/* Header */}
                <div className="border-b px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => navigate(`/delivery/${deliveryId}`)}
                        >
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                        <div>
                            <h1 className="text-lg font-semibold">Clip #{clipId}</h1>
                            <p className="text-xs text-muted-foreground">
                                Delivery #{deliveryId}
                                {delivery?.customer_request_description && ` — ${delivery.customer_request_description}`}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <VersionSelector
                            versions={versions}
                            currentVersionId={clip.dataset_version_id}
                            onSelect={() => {/* TODO: navigate to same clip in different version */}}
                        />
                        <div className="flex items-center gap-2 text-xs">
                            <span className="text-muted-foreground">{unresolvedCount} open</span>
                            <span className="text-muted-foreground/50">|</span>
                            <span className="text-green-600">{resolvedCount} resolved</span>
                        </div>
                    </div>
                </div>

                {/* Main content: 3-column layout */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Left: Metadata panel */}
                    <div className="w-72 border-r overflow-y-auto p-4 space-y-4">
                        <MetadataPanel
                            clip={clip}
                            currentTime={currentTime}
                            clipStartTime={clip.start_time}
                            onFieldClick={handleFieldClick}
                            highlightedField={highlightedField}
                        />

                        <Separator />

                        <BoundaryAdjuster
                            startTime={clip.start_time}
                            endTime={clip.end_time}
                            onAdjust={(newStart, newEnd) => {
                                // TODO: create a new clip version with adjusted boundaries
                                console.log('Adjust boundaries:', newStart, newEnd);
                            }}
                        />
                    </div>

                    {/* Center: Video player */}
                    <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center">
                        <div className="w-full max-w-4xl space-y-4">
                            {/* Video */}
                            <div className="aspect-video bg-black rounded-lg overflow-hidden">
                                <video
                                    ref={videoRef}
                                    src={clip.uri}
                                    controls
                                    className="w-full h-full"
                                    onTimeUpdate={handleTimeUpdate}
                                >
                                    <track kind="captions" />
                                </video>
                            </div>

                            {/* Feedback timeline visualization */}
                            {allFeedback.length > 0 && clip.duration > 0 && (
                                <div className="space-y-1">
                                    <p className="text-xs text-muted-foreground">Feedback markers</p>
                                    <div className="relative h-6 bg-muted rounded-full overflow-hidden">
                                        {/* Current time indicator */}
                                        <div
                                            className="absolute top-0 bottom-0 w-0.5 bg-primary z-10"
                                            style={{ left: `${(currentTime / clip.duration) * 100}%` }}
                                        />
                                        {/* Feedback markers */}
                                        {allFeedback
                                            .filter((f) => f.timestamp != null)
                                            .map((f) => {
                                                const pos = ((f.timestamp! - clip.start_time) / clip.duration) * 100;
                                                const config = ratingConfig[f.rating];
                                                return (
                                                    <button
                                                        key={f.id}
                                                        onClick={() => seekTo(f.timestamp! - clip.start_time)}
                                                        className={cn(
                                                            'absolute top-1 w-4 h-4 rounded-full border-2 -translate-x-1/2 transition-transform hover:scale-125',
                                                            f.is_resolved ? 'bg-gray-200 border-gray-300' : config.color
                                                        )}
                                                        style={{ left: `${Math.max(2, Math.min(pos, 98))}%` }}
                                                        title={f.comment ?? config.label}
                                                    />
                                                );
                                            })}
                                    </div>
                                </div>
                            )}

                            {/* Inline feedback form */}
                            <FeedbackForm
                                deliveryId={dId}
                                clipId={cId}
                                currentTime={currentTime + clip.start_time}
                                selectedField={highlightedField}
                                onSubmitted={invalidateFeedback}
                            />
                        </div>
                    </div>

                    {/* Right: Feedback list */}
                    <div className="w-80 border-l overflow-y-auto p-4 space-y-3">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold">Issues ({allFeedback.length})</h2>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="text-xs h-7"
                                onClick={() => setShowResolved(!showResolved)}
                            >
                                {showResolved ? 'Hide resolved' : 'Show resolved'}
                            </Button>
                        </div>

                        {filteredFeedback.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4">
                                {allFeedback.length === 0 ? 'No feedback yet' : 'All issues resolved'}
                            </p>
                        ) : (
                            <div className="space-y-2">
                                {filteredFeedback.map((fb) => (
                                    <FeedbackItem
                                        key={fb.id}
                                        feedback={fb}
                                        onResolve={handleResolve}
                                        onSeek={(t) => seekTo(t - clip.start_time)}
                                        isResolving={updateFeedback.isPending}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AppSidebar>
    );
}
