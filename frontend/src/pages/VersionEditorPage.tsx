import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import {
    useGetDataset,
    useGetVersionClips,
    useSearchDatasetVersions,
    useForkVersion,
    getGetVersionClipsQueryKey,
    getSearchDatasetVersionsQueryKey,
    Clip,
    DatasetVersion,
} from '@/openapi/sieveOnsite';
import {
    ArrowLeft,
    GitFork,
    Download,
    CheckSquare,
    Square,
    Search,
    Filter,
    Eye,
} from 'lucide-react';

export default function VersionEditorPage() {
    const { datasetId, versionId } = useParams<{ datasetId: string; versionId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const dsId = Number(datasetId);
    const verIdNum = Number(versionId);

    const [excludedIds, setExcludedIds] = useState<Set<number>>(new Set());
    const [searchTerm, setSearchTerm] = useState('');
    const [metadataFilter, setMetadataFilter] = useState('');

    const { data: dataset } = useGetDataset(dsId);
    const { data: clipsResponse } = useGetVersionClips(dsId, verIdNum);
    const clips = (clipsResponse as { entities: Clip[] } | undefined)?.entities ?? [];

    const { data: versionsResponse } = useSearchDatasetVersions(dsId);
    const versions = (versionsResponse as { entities: DatasetVersion[] } | undefined)?.entities ?? [];
    const currentVersion = versions.find((v) => v.id === verIdNum);

    const forkVersion = useForkVersion();

    // Filter clips by search/metadata
    const filteredClips = useMemo(() => {
        return clips.filter((clip) => {
            if (searchTerm) {
                const term = searchTerm.toLowerCase();
                const matchesUri = clip.uri.toLowerCase().includes(term);
                const matchesId = String(clip.id).includes(term);
                if (!matchesUri && !matchesId) return false;
            }
            if (metadataFilter) {
                const meta = clip.extra_metadata;
                if (!meta) return false;
                const term = metadataFilter.toLowerCase();
                const matchesKey = Object.keys(meta).some((k) => k.toLowerCase().includes(term));
                const matchesValue = Object.values(meta).some((v) =>
                    String(v).toLowerCase().includes(term)
                );
                if (!matchesKey && !matchesValue) return false;
            }
            return true;
        });
    }, [clips, searchTerm, metadataFilter]);

    const includedClips = clips.filter((c) => !excludedIds.has(c.id));
    const filteredIncludedCount = filteredClips.filter((c) => !excludedIds.has(c.id)).length;

    const toggleClip = (clipId: number) => {
        setExcludedIds((prev) => {
            const next = new Set(prev);
            if (next.has(clipId)) {
                next.delete(clipId);
            } else {
                next.add(clipId);
            }
            return next;
        });
    };

    const toggleAll = () => {
        const allFilteredIds = filteredClips.map((c) => c.id);
        const allExcluded = allFilteredIds.every((id) => excludedIds.has(id));

        setExcludedIds((prev) => {
            const next = new Set(prev);
            if (allExcluded) {
                allFilteredIds.forEach((id) => next.delete(id));
            } else {
                allFilteredIds.forEach((id) => next.add(id));
            }
            return next;
        });
    };

    const handleFork = async () => {
        const clipIds = includedClips.map((c) => c.id);
        await forkVersion.mutateAsync({ datasetId: dsId, versionId: verIdNum, data: { clip_ids: clipIds } });
        queryClient.invalidateQueries({ queryKey: getGetVersionClipsQueryKey(dsId, verIdNum) });
        queryClient.invalidateQueries({ queryKey: getSearchDatasetVersionsQueryKey(dsId) });
        navigate(`/dataset/${dsId}`);
    };

    const handleExportJson = () => {
        const exportData = includedClips.map((clip) => ({
            video_id: clip.uri.split('/').pop()?.split('_').slice(0, -1).join('_') ?? '',
            uri: clip.uri,
            clip_start_time: String(clip.start_time),
            clip_end_time: String(clip.end_time),
            clip_duration: clip.duration,
            ...(clip.extra_metadata ?? {}),
        }));

        const jsonl = exportData.map((row) => JSON.stringify(row)).join('\n');
        const blob = new Blob([jsonl], { type: 'application/jsonl' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `clip_metadata_v${currentVersion?.version_number ?? 'new'}.jsonl`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const allFilteredExcluded = filteredClips.length > 0 && filteredClips.every((c) => excludedIds.has(c.id));

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-5xl py-8 px-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-6">
                    <Button variant="ghost" size="icon" onClick={() => navigate(`/dataset/${dsId}`)}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div className="flex-1">
                        <h1 className="text-2xl font-bold">
                            Edit Clips — {dataset?.name ?? 'Loading...'}
                        </h1>
                        <p className="text-muted-foreground text-sm">
                            v{currentVersion?.version_number ?? '?'} · {clips.length} clips ·{' '}
                            <span className="font-medium text-foreground">{includedClips.length} included</span>
                            {excludedIds.size > 0 && (
                                <span className="text-red-500 ml-1">({excludedIds.size} removed)</span>
                            )}
                        </p>
                    </div>
                    <Button variant="outline" onClick={handleExportJson} disabled={includedClips.length === 0}>
                        <Download className="h-4 w-4 mr-2" />
                        Export JSONL
                    </Button>
                    <Button onClick={handleFork} disabled={forkVersion.isPending || includedClips.length === 0}>
                        <GitFork className="h-4 w-4 mr-2" />
                        {forkVersion.isPending ? 'Creating...' : `Fork as v${(currentVersion?.version_number ?? 0) + 1}`}
                    </Button>
                </div>

                {/* Filters */}
                <div className="flex gap-3 mb-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search by URI or clip ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                    <div className="relative flex-1">
                        <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Filter by metadata key or value..."
                            value={metadataFilter}
                            onChange={(e) => setMetadataFilter(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                </div>

                {/* Bulk actions */}
                <div className="flex items-center gap-3 mb-3 text-sm text-muted-foreground">
                    <button onClick={toggleAll} className="flex items-center gap-1.5 hover:text-foreground transition-colors">
                        {allFilteredExcluded ? (
                            <Square className="h-4 w-4" />
                        ) : (
                            <CheckSquare className="h-4 w-4" />
                        )}
                        {allFilteredExcluded ? 'Include' : 'Exclude'} all {filteredClips.length} visible
                    </button>
                    <span>·</span>
                    <span>{filteredIncludedCount} of {filteredClips.length} visible clips included</span>
                    {excludedIds.size > 0 && (
                        <>
                            <span>·</span>
                            <button
                                onClick={() => setExcludedIds(new Set())}
                                className="text-blue-500 hover:underline"
                            >
                                Reset all
                            </button>
                        </>
                    )}
                </div>

                {/* Clip list */}
                <div className="space-y-2">
                    {filteredClips.map((clip) => {
                        const isExcluded = excludedIds.has(clip.id);
                        const meta = clip.extra_metadata as Record<string, unknown> | null;

                        return (
                            <Card
                                key={clip.id}
                                className={`transition-all ${isExcluded ? 'opacity-40 border-red-200' : 'hover:border-primary/30'}`}
                            >
                                <CardContent className="py-3 px-4">
                                    <div className="flex items-start gap-3">
                                        <Checkbox
                                            checked={!isExcluded}
                                            className="mt-0.5"
                                            onCheckedChange={() => toggleClip(clip.id)}
                                        />
                                        <div
                                            className="flex-1 min-w-0 cursor-pointer"
                                            onClick={() => navigate(`/dataset/${dsId}/version/${verIdNum}/clip/${clip.id}`)}
                                        >
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-sm font-mono truncate">
                                                    {clip.uri.split('/').pop()}
                                                </span>
                                                <Badge variant="outline" className="text-xs shrink-0">
                                                    {clip.duration}s
                                                </Badge>
                                                <span className="text-xs text-muted-foreground shrink-0">
                                                    {clip.start_time}s — {clip.end_time}s
                                                </span>
                                            </div>
                                            {meta && Object.keys(meta).length > 0 && (
                                                <div className="flex flex-wrap gap-1.5 mt-1">
                                                    {Object.entries(meta).map(([key, value]) => {
                                                        const numVal = Number(value);
                                                        const isHighFraction = !isNaN(numVal) && numVal >= 0.5 && numVal <= 1;
                                                        return (
                                                            <Badge
                                                                key={key}
                                                                variant="secondary"
                                                                className={`text-xs font-normal ${isHighFraction ? 'bg-green-50 text-green-700' : ''}`}
                                                            >
                                                                {key.replace(/_/g, ' ')}: {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                                            </Badge>
                                                        );
                                                    })}
                                                </div>
                                            )}
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-7 w-7 shrink-0"
                                            onClick={() => navigate(`/dataset/${dsId}/version/${verIdNum}/clip/${clip.id}`)}
                                        >
                                            <Eye className="h-3.5 w-3.5" />
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>

                {filteredClips.length === 0 && clips.length > 0 && (
                    <p className="text-center text-muted-foreground py-12">No clips match your filters.</p>
                )}
                {clips.length === 0 && (
                    <p className="text-center text-muted-foreground py-12">No clips in this version.</p>
                )}
            </div>
        </AppSidebar>
    );
}
