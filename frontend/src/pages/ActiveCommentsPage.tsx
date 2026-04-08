import { useState, useCallback, memo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
    useGetDataset,
    useSearchDatasetVersions,
    useGetActiveComments,
    useUpdateReview,
    useCreateReply,
    useSearchReplies,
    ActiveComment,
    DatasetVersion,
    DatasetReviewReply,
    getGetActiveCommentsQueryKey,
    getSearchRepliesQueryKey,
} from '@/openapi/sieveOnsite';
import {
    ArrowLeft,
    MessageSquare,
    Trash2,
    Clock,
    CheckCircle2,
    Send,
    AlertTriangle,
    Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

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

function RepliesSection({
    datasetId,
    reviewId,
}: {
    datasetId: number;
    reviewId: number;
}) {
    const queryClient = useQueryClient();
    const [replyText, setReplyText] = useState('');
    const [showReplyForm, setShowReplyForm] = useState(false);

    const { data: repliesResponse } = useSearchReplies(datasetId, reviewId);
    const replies = (repliesResponse as { entities: DatasetReviewReply[] } | undefined)?.entities ?? [];

    const createReply = useCreateReply();

    const handleReply = () => {
        if (!replyText.trim()) return;
        createReply.mutate(
            {
                datasetId,
                reviewId,
                data: { review_id: reviewId, user_id: 0, comment: replyText.trim() },
            },
            {
                onSuccess: () => {
                    setReplyText('');
                    setShowReplyForm(false);
                    queryClient.invalidateQueries({
                        queryKey: getSearchRepliesQueryKey(datasetId, reviewId),
                    });
                },
            },
        );
    };

    return (
        <div className="pl-4 border-l-2 border-muted space-y-2">
            {replies.map((reply) => (
                <div key={reply.id} className="text-sm space-y-1">
                    <p>{reply.comment}</p>
                    <span className="text-xs text-muted-foreground">
                        {new Date(reply.created_at).toLocaleString()}
                    </span>
                </div>
            ))}
            {showReplyForm ? (
                <div className="space-y-2">
                    <Textarea
                        placeholder="Write a reply..."
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        rows={2}
                        className="text-sm"
                    />
                    <div className="flex gap-2">
                        <Button
                            size="sm"
                            disabled={!replyText.trim() || createReply.isPending}
                            onClick={handleReply}
                        >
                            <Send className="h-3 w-3 mr-1" />
                            Reply
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                                setShowReplyForm(false);
                                setReplyText('');
                            }}
                        >
                            Cancel
                        </Button>
                    </div>
                </div>
            ) : (
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs h-7"
                    onClick={() => setShowReplyForm(true)}
                >
                    Reply
                </Button>
            )}
        </div>
    );
}

const ActiveCommentCard = memo(function ActiveCommentCard({
    item,
    datasetId,
    allVersions,
    onClose,
}: {
    item: ActiveComment;
    datasetId: number;
    allVersions: DatasetVersion[];
    onClose: (reviewId: number) => void;
}) {
    const version = allVersions.find((v) => v.id === item.review.dataset_version_id);

    return (
        <Card
            className={cn(
                'transition-all',
                item.auto_completed && 'opacity-60 border-green-200 bg-green-50/30',
            )}
        >
            <CardContent className="p-4 space-y-3">
                <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                        {item.review.review_type === 'request_for_deletion' ? (
                            <Trash2 className="h-4 w-4 text-red-500" />
                        ) : (
                            <MessageSquare className="h-4 w-4 text-blue-500" />
                        )}
                        <Badge
                            variant="outline"
                            className={cn(
                                'text-xs',
                                item.review.review_type === 'request_for_deletion'
                                    ? 'bg-red-50 text-red-700'
                                    : 'bg-blue-50 text-blue-700',
                            )}
                        >
                            {item.review.review_type === 'request_for_deletion'
                                ? 'Deletion Request'
                                : 'Review'}
                        </Badge>
                        <VersionChip version={version} allVersions={allVersions} />
                        {item.clip_removed && (
                            <Badge variant="outline" className="text-xs bg-orange-50 text-orange-700">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                Clip Removed
                            </Badge>
                        )}
                        {item.auto_completed && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700">
                                <Sparkles className="h-3 w-3 mr-1" />
                                Auto-Completed
                            </Badge>
                        )}
                    </div>
                    {!item.auto_completed && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            onClick={() => onClose(item.review.id)}
                            title="Close this review"
                        >
                            <CheckCircle2 className="h-4 w-4 text-muted-foreground hover:text-green-500" />
                        </Button>
                    )}
                </div>

                <p className="text-sm">{item.review.comment}</p>

                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    {item.review.clip_timestamp != null && (
                        <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatTime(item.review.clip_timestamp)}
                        </span>
                    )}
                    <span>{new Date(item.review.created_at).toLocaleString()}</span>
                </div>

                {/* Replies */}
                <RepliesSection datasetId={datasetId} reviewId={item.review.id} />
            </CardContent>
        </Card>
    );
});

export default function ActiveCommentsPage() {
    const { datasetId, versionId } = useParams<{ datasetId: string; versionId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const dsId = Number(datasetId);
    const verIdNum = Number(versionId);

    const [view, setView] = useState<'comments' | 'clips'>('comments');

    const { data: dataset } = useGetDataset(dsId);
    const { data: versionsResponse } = useSearchDatasetVersions(dsId);
    const versions = (versionsResponse as { entities: DatasetVersion[] } | undefined)?.entities ?? [];
    const currentVersion = versions.find((v) => v.id === verIdNum);

    const { data: activeComments } = useGetActiveComments(dsId, verIdNum);

    const updateReview = useUpdateReview();

    const handleClose = useCallback((reviewId: number) => {
        updateReview.mutate(
            {
                datasetId: dsId,
                reviewId,
                data: {
                    id: reviewId,
                    status: 'closed',
                    resolved_in_version_id: verIdNum,
                },
            },
            {
                onSuccess: () => {
                    queryClient.invalidateQueries({
                        queryKey: getGetActiveCommentsQueryKey(dsId, verIdNum),
                    });
                },
            },
        );
    }, [dsId, verIdNum, updateReview, queryClient]);

    const topLevel = activeComments?.top_level ?? [];
    const byClip = activeComments?.by_clip ?? {};
    const autoCompletedCount = activeComments?.auto_completed_count ?? 0;
    const totalComments = topLevel.length + Object.values(byClip).reduce((sum, arr) => sum + arr.length, 0);

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-6">
                    <Button variant="ghost" size="icon" onClick={() => navigate(`/dataset/${dsId}`)}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div className="flex-1">
                        <h1 className="text-2xl font-bold">
                            Review Comments — {dataset?.name ?? 'Loading...'}
                        </h1>
                        <p className="text-muted-foreground text-sm">
                            v{currentVersion?.version_number ?? '?'}
                            {currentVersion?.commit_message && ` — ${currentVersion.commit_message}`}
                            {' · '}
                            {totalComments} comment{totalComments !== 1 ? 's' : ''} to address
                            {autoCompletedCount > 0 && (
                                <span className="text-green-600 ml-1">
                                    ({autoCompletedCount} auto-completed)
                                </span>
                            )}
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant={view === 'comments' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setView('comments')}
                        >
                            Comments
                        </Button>
                        <Button
                            variant={view === 'clips' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setView('clips')}
                        >
                            Clip by Clip
                        </Button>
                    </div>
                </div>

                {totalComments === 0 ? (
                    <div className="text-center py-12">
                        <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
                        <p className="text-muted-foreground">No open comments to address.</p>
                        <Button
                            variant="outline"
                            className="mt-4"
                            onClick={() => navigate(`/dataset/${dsId}`)}
                        >
                            Back to Dataset
                        </Button>
                    </div>
                ) : view === 'comments' ? (
                    <div className="space-y-6">
                        {/* Top-level comments */}
                        {topLevel.length > 0 && (
                            <div>
                                <h2 className="text-sm font-semibold mb-3">
                                    Top-Level Comments ({topLevel.length})
                                </h2>
                                <div className="space-y-3">
                                    {topLevel.map((item) => (
                                        <ActiveCommentCard
                                            key={item.review.id}
                                            item={item}
                                            datasetId={dsId}

                                            allVersions={versions}
                                            onClose={handleClose}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Clip-scoped comments */}
                        {Object.entries(byClip).map(([clipId, items]) => (
                            <div key={clipId}>
                                <div className="flex items-center gap-2 mb-3">
                                    <h2 className="text-sm font-semibold">
                                        Clip #{clipId}
                                    </h2>
                                    <Badge variant="outline" className="text-xs">
                                        {items.length} comment{items.length !== 1 ? 's' : ''}
                                    </Badge>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-7 px-2 text-xs ml-auto"
                                        onClick={() =>
                                            navigate(
                                                `/dataset/${dsId}/version/${verIdNum}/clip/${clipId}`,
                                            )
                                        }
                                    >
                                        View Clip
                                    </Button>
                                </div>
                                <div className="space-y-3">
                                    {items.map((item) => (
                                        <ActiveCommentCard
                                            key={item.review.id}
                                            item={item}
                                            datasetId={dsId}

                                            allVersions={versions}
                                            onClose={handleClose}
                                        />
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    /* Clip-by-clip view — show all clips with comments, grouped */
                    <div className="space-y-4">
                        {Object.entries(byClip).map(([clipId, items]) => (
                            <Card key={clipId}>
                                <CardHeader className="pb-3">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-base">Clip #{clipId}</CardTitle>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-7 px-2 text-xs"
                                            onClick={() =>
                                                navigate(
                                                    `/dataset/${dsId}/version/${verIdNum}/clip/${clipId}`,
                                                )
                                            }
                                        >
                                            View Clip
                                        </Button>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    {items.map((item) => (
                                        <ActiveCommentCard
                                            key={item.review.id}
                                            item={item}
                                            datasetId={dsId}

                                            allVersions={versions}
                                            onClose={handleClose}
                                        />
                                    ))}
                                </CardContent>
                            </Card>
                        ))}

                        {/* Top-level at the bottom in clip view */}
                        {topLevel.length > 0 && (
                            <Card>
                                <CardHeader className="pb-3">
                                    <CardTitle className="text-base">
                                        Dataset-Level Comments
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    {topLevel.map((item) => (
                                        <ActiveCommentCard
                                            key={item.review.id}
                                            item={item}
                                            datasetId={dsId}

                                            allVersions={versions}
                                            onClose={handleClose}
                                        />
                                    ))}
                                </CardContent>
                            </Card>
                        )}
                    </div>
                )}
            </div>
        </AppSidebar>
    );
}
