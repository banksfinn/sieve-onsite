import { useState, useRef, useCallback, useEffect, useMemo, memo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
    useGetDataset,
    useSearchDatasetVersions,
    useGetVersionClips,
    useSearchReviews,
    useCreateReview,
    batchSignedUrls,
    DatasetReview,
    DatasetVersion,
    Clip,
    ReviewType,
    getSearchReviewsQueryKey,
} from '@/openapi/sieveOnsite';
import {
    ArrowLeft,
    MessageSquare,
    Trash2,
    Clock,
    CheckCircle2,
    Circle,
    Send,
    Pin,
    ChevronLeft,
    ChevronRight,
    Keyboard,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// --- Helpers ---

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
}

function clipReviewStatus(clipId: number, reviews: DatasetReview[]): 'none' | 'open' | 'resolved' {
    const clipReviews = reviews.filter((r) => r.clip_id === clipId);
    if (clipReviews.length === 0) return 'none';
    if (clipReviews.some((r) => r.status === 'open')) return 'open';
    return 'resolved';
}

// --- Version Chip with commit message tooltip ---

function VersionChip({
    version,
    allVersions,
}: {
    version: DatasetVersion | undefined;
    allVersions: DatasetVersion[];
}) {
    if (!version) return null;

    const commitMessages = allVersions
        .filter((v) => v.version_number >= version.version_number && v.commit_message)
        .sort((a, b) => a.version_number - b.version_number)
        .map((v) => `v${v.version_number}: ${v.commit_message}`);

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Badge variant="outline" className="text-xs cursor-help">
                        v{version.version_number}
                    </Badge>
                </TooltipTrigger>
                {commitMessages.length > 0 && (
                    <TooltipContent side="bottom" className="max-w-sm">
                        <div className="space-y-1 text-xs">
                            {commitMessages.map((msg, i) => (
                                <p key={i}>{msg}</p>
                            ))}
                        </div>
                    </TooltipContent>
                )}
            </Tooltip>
        </TooltipProvider>
    );
}

// --- Review Item ---

const ReviewItem = memo(function ReviewItem({
    review,
    allVersions,
    onSeek,
}: {
    review: DatasetReview;
    allVersions: DatasetVersion[];
    onSeek?: (time: number) => void;
}) {
    const version = allVersions.find((v) => v.id === review.dataset_version_id);
    const isOpen = review.status === 'open';

    return (
        <div
            className={cn(
                'border rounded-lg p-3 space-y-2',
                !isOpen && 'opacity-50',
            )}
        >
            <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                    {review.review_type === 'request_for_deletion' ? (
                        <Trash2 className="h-3.5 w-3.5 text-red-500 shrink-0" />
                    ) : (
                        <MessageSquare className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    )}
                    <Badge
                        variant="outline"
                        className={cn(
                            'text-xs',
                            review.review_type === 'request_for_deletion'
                                ? 'bg-red-50 text-red-700'
                                : 'bg-blue-50 text-blue-700',
                        )}
                    >
                        {review.review_type === 'request_for_deletion' ? 'Delete' : 'Review'}
                    </Badge>
                    <VersionChip version={version} allVersions={allVersions} />
                </div>
                {isOpen ? (
                    <Circle className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                ) : (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
                )}
            </div>
            <p className="text-sm">{review.comment}</p>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                {review.clip_timestamp != null && (
                    <button
                        onClick={() => onSeek?.(review.clip_timestamp!)}
                        className="flex items-center gap-1 hover:text-primary transition-colors"
                    >
                        <Clock className="h-3 w-3" />
                        {formatTime(review.clip_timestamp)}
                    </button>
                )}
                <span>{new Date(review.created_at).toLocaleString()}</span>
            </div>
        </div>
    );
});

// --- Review Form ---

function ReviewForm({
    datasetId,
    versionId,
    clipId,
    currentTime,
    onSubmitted,
    textareaRef,
    pinnedTime: externalPinnedTime,
    onPinnedTimeChange,
    reviewType: externalReviewType,
    onReviewTypeChange,
}: {
    datasetId: number;
    versionId: number;
    clipId?: number;
    currentTime?: number;
    onSubmitted: () => void;
    textareaRef?: React.Ref<HTMLTextAreaElement>;
    pinnedTime?: number | null;
    onPinnedTimeChange?: (time: number | null) => void;
    reviewType?: ReviewType;
    onReviewTypeChange?: (type: ReviewType) => void;
}) {
    const [internalReviewType, setInternalReviewType] = useState<ReviewType>('review');
    const [comment, setComment] = useState('');
    const [internalPinnedTime, setInternalPinnedTime] = useState<number | null>(null);

    const reviewType = externalReviewType ?? internalReviewType;
    const setReviewType = (type: ReviewType) => {
        if (onReviewTypeChange) onReviewTypeChange(type);
        else setInternalReviewType(type);
    };

    const pinnedTime = externalPinnedTime !== undefined ? externalPinnedTime : internalPinnedTime;
    const setPinnedTime = (time: number | null) => {
        if (onPinnedTimeChange) onPinnedTimeChange(time);
        else setInternalPinnedTime(time);
    };

    const createReview = useCreateReview();

    const handleSubmit = () => {
        if (!comment.trim()) return;
        createReview.mutate(
            {
                datasetId,
                versionId,
                data: {
                    dataset_id: datasetId,
                    dataset_version_id: versionId,
                    user_id: 0,
                    review_type: reviewType,
                    clip_id: clipId ?? undefined,
                    clip_timestamp: pinnedTime ?? undefined,
                    comment: comment.trim(),
                },
            },
            {
                onSuccess: () => {
                    setComment('');
                    setPinnedTime(null);
                    onSubmitted();
                },
            },
        );
    };

    return (
        <div className="space-y-3">
            <div className="flex gap-2">
                <Button
                    variant="outline"
                    size="sm"
                    className={cn('flex-1', reviewType === 'review' && 'bg-blue-50 text-blue-700 border-blue-200')}
                    onClick={() => setReviewType('review')}
                >
                    <MessageSquare className="h-3.5 w-3.5 mr-1" />
                    Review
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    className={cn('flex-1', reviewType === 'request_for_deletion' && 'bg-red-50 text-red-700 border-red-200')}
                    onClick={() => setReviewType('request_for_deletion')}
                >
                    <Trash2 className="h-3.5 w-3.5 mr-1" />
                    Delete
                </Button>
            </div>

            {clipId != null && currentTime != null && (
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => setPinnedTime(currentTime)}
                    >
                        <Pin className="h-3 w-3 mr-1" />
                        {pinnedTime != null ? `@ ${formatTime(pinnedTime)}` : 'Pin timestamp'}
                    </Button>
                    {pinnedTime != null && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs h-7 px-2"
                            onClick={() => setPinnedTime(null)}
                        >
                            Clear
                        </Button>
                    )}
                </div>
            )}

            <Textarea
                ref={textareaRef as React.Ref<HTMLTextAreaElement>}
                placeholder={
                    clipId != null
                        ? reviewType === 'request_for_deletion'
                            ? 'Why should this clip be removed?'
                            : 'What needs to change in this clip?'
                        : 'Overall feedback on this dataset version...'
                }
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                    }
                }}
                rows={2}
                className="text-sm"
            />

            <Button
                size="sm"
                className="w-full"
                disabled={!comment.trim() || createReview.isPending}
                onClick={handleSubmit}
            >
                <Send className="h-3.5 w-3.5 mr-1" />
                {createReview.isPending ? 'Submitting...' : 'Submit'}
            </Button>
        </div>
    );
}

// --- Keyboard shortcut legend ---

function Kbd({ children }: { children: React.ReactNode }) {
    return (
        <kbd className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded border bg-muted text-[10px] font-mono font-medium text-muted-foreground">
            {children}
        </kbd>
    );
}

const DETAIL_SHORTCUTS = [
    { keys: ['Space'], label: 'Play / pause' },
    { keys: ['\u2190', '\u2192'], label: 'Prev / next clip' },
    { keys: [',', '.'], label: 'Back / forward 5s' },
    { keys: ['<', '>'], label: 'Back / forward 1s' },
    { keys: ['R'], label: 'Review' },
    { keys: ['D'], label: 'Request deletion' },
    { keys: ['T'], label: 'Pin timestamp' },
    { keys: ['\u21B5'], label: 'Submit + next clip' },
    { keys: ['Esc'], label: 'Back to list' },
] as const;

// --- Clip Filmstrip Thumbnail ---

const FilmstripItem = memo(function FilmstripItem({
    clip,
    isActive,
    reviewStatus,
    onSelect,
}: {
    clip: Clip;
    isActive: boolean;
    reviewStatus: 'none' | 'open' | 'resolved';
    onSelect: (clipId: number) => void;
}) {
    const meta = clip.extra_metadata as Record<string, unknown> | null;

    return (
        <button
            onClick={() => onSelect(clip.id)}
            className={cn(
                'shrink-0 w-40 rounded-lg border p-2 text-left transition-all',
                isActive
                    ? 'ring-2 ring-primary border-primary bg-primary/5'
                    : 'hover:bg-muted/50 border-border',
            )}
        >
            <div className="flex items-center gap-1.5 mb-1">
                {reviewStatus === 'open' && (
                    <span className="w-2 h-2 rounded-full bg-yellow-500 shrink-0" />
                )}
                {reviewStatus === 'resolved' && (
                    <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                )}
                <span className="text-xs font-mono truncate">{clip.uri.split('/').pop()}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <span>{clip.duration.toFixed(1)}s</span>
                {meta && Object.keys(meta).length > 0 && (
                    <span className="truncate">
                        · {Object.entries(meta).slice(0, 1).map(([k, v]) =>
                            `${k.replace(/_/g, ' ')}: ${typeof v === 'number' ? v.toFixed(1) : String(v)}`
                        ).join('')}
                    </span>
                )}
            </div>
        </button>
    );
});

// --- Main Page ---

export default function VersionReviewPage() {
    const { datasetId, versionId } = useParams<{ datasetId: string; versionId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const videoRef = useRef<HTMLVideoElement>(null);
    const filmstripRef = useRef<HTMLDivElement>(null);
    const reviewTextareaRef = useRef<HTMLTextAreaElement>(null);

    const dsId = Number(datasetId);
    const verIdNum = Number(versionId);

    const [selectedClipId, setSelectedClipId] = useState<number | null>(null);
    const [currentTime, setCurrentTime] = useState(0);
    const [showShortcuts, setShowShortcuts] = useState(false);
    const [reviewPinnedTime, setReviewPinnedTime] = useState<number | null>(null);
    const [reviewType, setReviewType] = useState<ReviewType>('review');

    const { data: dataset } = useGetDataset(dsId);
    const { data: versionsResponse } = useSearchDatasetVersions(dsId);
    const versions = (versionsResponse as { entities: DatasetVersion[] } | undefined)?.entities ?? [];
    const currentVersion = versions.find((v) => v.id === verIdNum);

    const { data: clipsResponse } = useGetVersionClips(dsId, verIdNum);
    const clips = (clipsResponse as { entities: Clip[] } | undefined)?.entities ?? [];

    const { data: allReviewsResponse } = useSearchReviews(dsId);
    const allReviews = (allReviewsResponse as { entities: DatasetReview[] } | undefined)?.entities ?? [];

    // Pre-compute review status and open counts per clip to avoid O(clips × reviews) in render
    const { reviewStatusMap, clipOpenCountMap } = useMemo(() => {
        const statusMap: Record<number, 'none' | 'open' | 'resolved'> = {};
        const openMap: Record<number, number> = {};
        for (const clip of clips) {
            statusMap[clip.id] = clipReviewStatus(clip.id, allReviews);
            openMap[clip.id] = allReviews.filter((r) => r.clip_id === clip.id && r.status === 'open').length;
        }
        return { reviewStatusMap: statusMap, clipOpenCountMap: openMap };
    }, [clips, allReviews]);

    const selectedClipIndex = selectedClipId != null ? clips.findIndex((c) => c.id === selectedClipId) : -1;
    const selectedClip = selectedClipIndex >= 0 ? clips[selectedClipIndex] : null;

    // Batch-fetch signed URLs for all clips when clip list loads
    const [signedUrls, setSignedUrls] = useState<Record<string, string>>({});
    useEffect(() => {
        if (clips.length === 0) return;
        const clipIds = clips.map((c) => c.id);
        batchSignedUrls({ clip_ids: clipIds }).then((res) => {
            setSignedUrls(res.urls);
        });
    }, [clips]);

    const videoSrc = selectedClipId != null ? signedUrls[String(selectedClipId)] : undefined;

    // Reviews for the right sidebar — global or clip-scoped
    const sidebarReviews = selectedClipId != null
        ? allReviews.filter((r) => r.clip_id === selectedClipId)
        : allReviews.filter((r) => r.clip_id == null);

    const openCount = allReviews.filter((r) => r.status === 'open').length;
    const resolvedCount = allReviews.filter((r) => r.status !== 'open').length;

    const invalidateReviews = () => {
        queryClient.invalidateQueries({ queryKey: getSearchReviewsQueryKey(dsId) });
    };

    const handleTimeUpdate = useCallback(() => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    }, []);

    const seekTo = useCallback((time: number) => {
        if (videoRef.current && selectedClip) {
            const seekTime = time - selectedClip.start_time;
            videoRef.current.currentTime = Math.max(0, seekTime);
            setCurrentTime(seekTime);
        }
    }, [selectedClip]);

    const goToClip = useCallback((clipId: number) => {
        setSelectedClipId(clipId);
        setCurrentTime(0);
        setReviewPinnedTime(null);
        setReviewType('review');
    }, []);

    const goNext = useCallback(() => {
        if (selectedClipIndex < clips.length - 1) {
            goToClip(clips[selectedClipIndex + 1].id);
        }
    }, [selectedClipIndex, clips, goToClip]);

    const goPrev = useCallback(() => {
        if (selectedClipIndex > 0) {
            goToClip(clips[selectedClipIndex - 1].id);
        }
    }, [selectedClipIndex, clips, goToClip]);

    // Scroll filmstrip to center the active clip
    useEffect(() => {
        if (filmstripRef.current && selectedClipIndex >= 0) {
            const container = filmstripRef.current;
            const activeChild = container.children[selectedClipIndex] as HTMLElement | undefined;
            if (activeChild) {
                const scrollTarget = activeChild.offsetLeft - container.offsetWidth / 2 + activeChild.offsetWidth / 2;
                container.scrollTo({ left: scrollTarget, behavior: 'smooth' });
            }
        }
    }, [selectedClipIndex]);

    // Keyboard navigation in detail view
    useEffect(() => {
        if (selectedClipId == null) return;
        const handler = (e: KeyboardEvent) => {
            const inTextInput = e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement;

            // Escape always works
            if (e.key === 'Escape') {
                if (inTextInput) {
                    (e.target as HTMLElement).blur();
                } else {
                    setSelectedClipId(null);
                }
                e.preventDefault();
                return;
            }

            // All other shortcuts are disabled when typing
            if (inTextInput) return;

            const video = videoRef.current;

            switch (e.key) {
                case 'ArrowRight':
                    goNext();
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                    goPrev();
                    e.preventDefault();
                    break;
                case ' ':
                    if (video) {
                        if (video.paused) video.play();
                        else video.pause();
                    }
                    e.preventDefault();
                    break;
                case ',':
                    if (video) video.currentTime = Math.max(0, video.currentTime - 5);
                    e.preventDefault();
                    break;
                case '.':
                    if (video) video.currentTime = Math.min(video.duration, video.currentTime + 5);
                    e.preventDefault();
                    break;
                case '<':
                    if (video) video.currentTime = Math.max(0, video.currentTime - 1);
                    e.preventDefault();
                    break;
                case '>':
                    if (video) video.currentTime = Math.min(video.duration, video.currentTime + 1);
                    e.preventDefault();
                    break;
                case 'r':
                case 'R':
                    reviewTextareaRef.current?.focus();
                    e.preventDefault();
                    break;
                case 't':
                case 'T':
                    if (video && selectedClip) {
                        const sourceTime = video.currentTime + selectedClip.start_time;
                        setReviewPinnedTime(sourceTime);
                    }
                    e.preventDefault();
                    break;
                case 'd':
                case 'D':
                    setReviewType((prev) => prev === 'request_for_deletion' ? 'review' : 'request_for_deletion');
                    reviewTextareaRef.current?.focus();
                    e.preventDefault();
                    break;
                case '?':
                    setShowShortcuts((s) => !s);
                    e.preventDefault();
                    break;
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [selectedClipId, selectedClip, goNext, goPrev]);

    const statusDot = (status: 'none' | 'open' | 'resolved') => {
        if (status === 'none') return null;
        if (status === 'open')
            return <span className="w-2 h-2 rounded-full bg-yellow-500 inline-block shrink-0" />;
        return <span className="w-2 h-2 rounded-full bg-green-500 inline-block shrink-0" />;
    };

    // =====================================================
    // DETAIL VIEW — clip selected, full-screen takeover
    // =====================================================
    if (selectedClip) {
        const meta = selectedClip.extra_metadata as Record<string, unknown> | null;
        const hasMetadata = meta && Object.keys(meta).length > 0;

        return (
            <AppSidebar>
                <div className="h-full flex flex-col overflow-hidden -m-4">
                    {/* Detail header */}
                    <div className="border-b px-4 py-2 flex items-center justify-between shrink-0 min-w-0">
                        <div className="flex items-center gap-3 min-w-0 flex-1">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="shrink-0"
                                onClick={() => setSelectedClipId(null)}
                            >
                                <ArrowLeft className="h-4 w-4 mr-1" />
                                Back to list
                            </Button>
                            <Separator orientation="vertical" className="h-5 shrink-0" />
                            <span className="text-sm font-mono truncate min-w-0">
                                {selectedClip.uri.split('/').pop()}
                            </span>
                            <span className="text-xs text-muted-foreground shrink-0">
                                {selectedClipIndex + 1} / {clips.length}
                            </span>
                        </div>
                        <div className="flex items-center gap-2 shrink-0 ml-2">
                            <Button
                                variant="ghost"
                                size="sm"
                                className={cn('h-7 px-2 text-xs gap-1', showShortcuts && 'bg-muted')}
                                onClick={() => setShowShortcuts((s) => !s)}
                            >
                                <Keyboard className="h-3.5 w-3.5" />
                                <Kbd>?</Kbd>
                            </Button>
                            <span className="text-xs text-muted-foreground font-mono">
                                {formatTime(currentTime + selectedClip.start_time)} in source
                            </span>
                            <div className="flex gap-1">
                                <Button
                                    variant="outline"
                                    size="icon"
                                    className="h-8 w-8"
                                    disabled={selectedClipIndex <= 0}
                                    onClick={goPrev}
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    className="h-8 w-8"
                                    disabled={selectedClipIndex >= clips.length - 1}
                                    onClick={goNext}
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>

                    {/* Shortcuts legend */}
                    {showShortcuts && (
                        <div className="border-b px-4 py-1.5 bg-muted/30 shrink-0 flex items-center gap-3 text-xs text-muted-foreground overflow-x-auto">
                            {DETAIL_SHORTCUTS.map(({ keys, label }) => (
                                <span key={label} className="flex items-center gap-1 shrink-0">
                                    {keys.map((k, i) => (
                                        <span key={k} className="flex items-center gap-0.5">
                                            {i > 0 && <span className="text-muted-foreground/50">/</span>}
                                            <Kbd>{k}</Kbd>
                                        </span>
                                    ))}
                                    <span className="ml-0.5">{label}</span>
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Preload adjacent clips */}
                    <div className="hidden">
                        {selectedClipIndex > 0 && signedUrls[String(clips[selectedClipIndex - 1].id)] && (
                            <video
                                key={`preload-prev-${clips[selectedClipIndex - 1].id}`}
                                src={signedUrls[String(clips[selectedClipIndex - 1].id)]}
                                preload="auto"
                            />
                        )}
                        {selectedClipIndex < clips.length - 1 && signedUrls[String(clips[selectedClipIndex + 1].id)] && (
                            <video
                                key={`preload-next-${clips[selectedClipIndex + 1].id}`}
                                src={signedUrls[String(clips[selectedClipIndex + 1].id)]}
                                preload="auto"
                            />
                        )}
                    </div>

                    {/* Main content area */}
                    <div className="flex-1 flex overflow-hidden min-w-0">
                        {/* Center: video + timeline + metadata */}
                        <div className="flex-1 min-w-0 overflow-y-auto p-4">
                            <div className="space-y-3 max-w-3xl mx-auto">
                                {/* Video player */}
                                <div className="aspect-video bg-black rounded-lg overflow-hidden max-h-[50vh]">
                                    {videoSrc ? (
                                        <video
                                            ref={videoRef}
                                            key={selectedClip.id}
                                            src={videoSrc}
                                            controls
                                            className="w-full h-full"
                                            onTimeUpdate={handleTimeUpdate}
                                        >
                                            <track kind="captions" />
                                        </video>
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                                            Loading video...
                                        </div>
                                    )}
                                </div>

                                {/* Timeline */}
                                {selectedClip.duration > 0 && (
                                    <div className="space-y-1">
                                        <div className="relative h-5 bg-muted rounded-full overflow-hidden">
                                            <div
                                                className="absolute top-0 bottom-0 w-0.5 bg-primary z-10"
                                                style={{ left: `${(currentTime / selectedClip.duration) * 100}%` }}
                                            />
                                            {sidebarReviews
                                                .filter((r) => r.clip_timestamp != null)
                                                .map((r) => {
                                                    const pos = ((r.clip_timestamp! - selectedClip.start_time) / selectedClip.duration) * 100;
                                                    return (
                                                        <button
                                                            key={r.id}
                                                            onClick={() => seekTo(r.clip_timestamp!)}
                                                            className={cn(
                                                                'absolute top-0.5 w-4 h-4 rounded-full border-2 -translate-x-1/2 hover:scale-125 transition-transform',
                                                                r.review_type === 'request_for_deletion'
                                                                    ? 'bg-red-100 border-red-400'
                                                                    : 'bg-blue-100 border-blue-400',
                                                            )}
                                                            style={{ left: `${Math.max(2, Math.min(pos, 98))}%` }}
                                                            title={r.comment}
                                                        />
                                                    );
                                                })}
                                        </div>
                                        <div className="flex justify-between text-xs text-muted-foreground font-mono">
                                            <span>{formatTime(selectedClip.start_time)}</span>
                                            <span>{selectedClip.duration.toFixed(1)}s</span>
                                            <span>{formatTime(selectedClip.end_time)}</span>
                                        </div>
                                    </div>
                                )}

                            </div>
                        </div>

                        {/* Right sidebar: reviews */}
                        <div className="w-80 border-l flex flex-col overflow-hidden shrink-0">
                            <div className="px-4 py-3 border-b shrink-0">
                                <h2 className="text-sm font-semibold">
                                    Clip Reviews
                                    <span className="text-muted-foreground font-normal ml-1">
                                        ({sidebarReviews.length})
                                    </span>
                                </h2>
                            </div>
                            <div className="px-4 py-3 border-b shrink-0">
                                <ReviewForm
                                    datasetId={dsId}
                                    versionId={verIdNum}
                                    clipId={selectedClipId ?? undefined}
                                    currentTime={currentTime + selectedClip.start_time}
                                    onSubmitted={() => { setReviewPinnedTime(null); setReviewType('review'); invalidateReviews(); goNext(); }}
                                    textareaRef={reviewTextareaRef}
                                    pinnedTime={reviewPinnedTime}
                                    onPinnedTimeChange={setReviewPinnedTime}
                                    reviewType={reviewType}
                                    onReviewTypeChange={setReviewType}
                                />
                            </div>
                            <Separator />
                            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                                {sidebarReviews.length === 0 ? (
                                    <p className="text-sm text-muted-foreground text-center py-8">
                                        No reviews on this clip yet
                                    </p>
                                ) : (
                                    sidebarReviews.map((r) => (
                                        <ReviewItem
                                            key={r.id}
                                            review={r}
                                            allVersions={versions}
                                            onSeek={seekTo}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Bottom: metadata + filmstrip */}
                    <div className="border-t bg-muted/30 px-4 py-2 shrink-0 space-y-2">
                        {/* Clip metadata */}
                        <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs">
                            <div className="flex gap-1.5">
                                <span className="text-muted-foreground">Start</span>
                                <span className="font-mono">{formatTime(selectedClip.start_time)}</span>
                            </div>
                            <div className="flex gap-1.5">
                                <span className="text-muted-foreground">End</span>
                                <span className="font-mono">{formatTime(selectedClip.end_time)}</span>
                            </div>
                            <div className="flex gap-1.5">
                                <span className="text-muted-foreground">Duration</span>
                                <span className="font-mono">{selectedClip.duration.toFixed(2)}s</span>
                            </div>
                            {hasMetadata && Object.entries(meta!).map(([key, value]) => (
                                <div key={key} className="flex gap-1.5">
                                    <span className="text-muted-foreground">{key.replace(/_/g, ' ')}</span>
                                    <span className="font-mono">
                                        {typeof value === 'boolean'
                                            ? (value ? 'Yes' : 'No')
                                            : typeof value === 'number'
                                                ? value.toFixed(2)
                                                : String(value)}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div
                            ref={filmstripRef}
                            className="flex gap-2 overflow-x-auto pb-1"
                        >
                            {clips.map((clip) => (
                                <FilmstripItem
                                    key={clip.id}
                                    clip={clip}
                                    isActive={clip.id === selectedClipId}
                                    reviewStatus={reviewStatusMap[clip.id] ?? 'none'}
                                    onSelect={goToClip}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </AppSidebar>
        );
    }

    // =====================================================
    // LIST VIEW — no clip selected
    // =====================================================
    return (
        <AppSidebar>
            <div className="h-full flex flex-col overflow-hidden -m-4">
                {/* Header */}
                <div className="border-b px-4 py-3 flex items-center justify-between shrink-0">
                    <div className="flex items-center gap-3 min-w-0">
                        <Button variant="ghost" size="icon" className="shrink-0" onClick={() => navigate(`/dataset/${dsId}`)}>
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                        <div className="min-w-0">
                            <h1 className="text-lg font-semibold truncate">
                                Review — {dataset?.name ?? 'Loading...'}
                            </h1>
                            <p className="text-xs text-muted-foreground">
                                v{currentVersion?.version_number ?? '?'}
                                {currentVersion?.commit_message && ` — ${currentVersion.commit_message}`}
                                {' · '}
                                {clips.length} clips
                                {' · '}
                                <span className="text-yellow-600">{openCount} open</span>
                                {' · '}
                                <span className="text-green-600">{resolvedCount} resolved</span>
                            </p>
                        </div>
                    </div>
                </div>

                {/* Two-panel list layout */}
                <div className="flex-1 flex overflow-hidden min-w-0">
                    {/* Left: scrollable clip list */}
                    <div className="flex-1 min-w-0 overflow-y-auto p-4">
                        <div className="space-y-1">
                            {clips.map((clip) => {
                                const status = reviewStatusMap[clip.id] ?? 'none';
                                const clipOpenCount = clipOpenCountMap[clip.id] ?? 0;
                                const meta = clip.extra_metadata as Record<string, unknown> | null;

                                return (
                                    <div
                                        key={clip.id}
                                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors hover:bg-muted/50"
                                        onClick={() => goToClip(clip.id)}
                                    >
                                        {statusDot(status)}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-mono truncate">
                                                    {clip.uri.split('/').pop()}
                                                </span>
                                                <Badge variant="outline" className="text-xs shrink-0">
                                                    {clip.duration}s
                                                </Badge>
                                            </div>
                                            {meta && Object.keys(meta).length > 0 && (
                                                <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-0.5">
                                                    {Object.entries(meta).map(([key, value]) => (
                                                        <span
                                                            key={key}
                                                            className="text-xs text-muted-foreground"
                                                        >
                                                            {key.replace(/_/g, ' ')}: {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                        {clipOpenCount > 0 && (
                                            <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 shrink-0">
                                                {clipOpenCount}
                                            </Badge>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right sidebar: dataset-level reviews */}
                    <div className="w-80 border-l flex flex-col overflow-hidden shrink-0">
                        <div className="px-4 py-3 border-b shrink-0">
                            <h2 className="text-sm font-semibold">
                                Dataset Reviews
                                <span className="text-muted-foreground font-normal ml-1">
                                    ({sidebarReviews.length})
                                </span>
                            </h2>
                            <p className="text-xs text-muted-foreground mt-0.5">
                                Select a clip to see clip-level reviews
                            </p>
                        </div>
                        <div className="px-4 py-3 border-b shrink-0">
                            <ReviewForm
                                datasetId={dsId}
                                versionId={verIdNum}
                                onSubmitted={invalidateReviews}
                            />
                        </div>
                        <Separator />
                        <div className="flex-1 overflow-y-auto p-4 space-y-2">
                            {sidebarReviews.length === 0 ? (
                                <p className="text-sm text-muted-foreground text-center py-8">
                                    No dataset-level reviews yet
                                </p>
                            ) : (
                                sidebarReviews.map((r) => (
                                    <ReviewItem
                                        key={r.id}
                                        review={r}
                                        allVersions={versions}
                                    />
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AppSidebar>
    );
}
