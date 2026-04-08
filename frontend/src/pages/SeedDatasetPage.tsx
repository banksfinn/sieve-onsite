import { useState } from 'react';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { usePreviewMetadata, PreviewMetadataResponse } from '@/openapi/sieveOnsite';
import { Database, Copy, Download, RefreshCw } from 'lucide-react';

export default function SeedDatasetPage() {
    const { showSuccess, showError } = useSnackbar();

    const [bucketPath, setBucketPath] = useState('gs://product-onsite/sample2/');
    const [maxClips, setMaxClips] = useState(50);
    const [preview, setPreview] = useState<PreviewMetadataResponse | null>(null);

    const previewMutation = usePreviewMetadata();

    const handleFetch = () => {
        previewMutation.mutate(
            { data: { bucket_path: bucketPath, max_clips: maxClips || undefined } },
            {
                onSuccess: (data) => {
                    setPreview(data);
                    showSuccess(`Loaded ${data.clips.length} clips (of ${data.total_clips} total)`);
                },
                onError: (err) => {
                    showError(err instanceof Error ? err.message : 'Failed to fetch metadata');
                },
            },
        );
    };

    const clipJsonl = preview
        ? preview.clips.map((c) => JSON.stringify(c)).join('\n')
        : '';
    const videoJsonl = preview
        ? preview.videos.map((v) => JSON.stringify(v)).join('\n')
        : '';

    const handleCopy = async (text: string, label: string) => {
        await navigator.clipboard.writeText(text);
        showSuccess(`${label} copied to clipboard`);
    };

    const handleDownload = (text: string, filename: string) => {
        const blob = new Blob([text + '\n'], { type: 'application/jsonl' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <div className="flex items-center gap-2 mb-6">
                    <Database className="h-6 w-6" />
                    <h1 className="text-2xl font-bold">Preview Bucket Metadata</h1>
                    <Badge variant="outline" className="text-xs">
                        Dev Tool
                    </Badge>
                </div>

                {/* Controls */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="text-base">GCS Bucket</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="col-span-2">
                                <Label htmlFor="bucketPath">Bucket Path</Label>
                                <Input
                                    id="bucketPath"
                                    value={bucketPath}
                                    onChange={(e) => setBucketPath(e.target.value)}
                                    className="font-mono text-sm"
                                    placeholder="gs://bucket-name/prefix/"
                                />
                            </div>
                            <div>
                                <Label htmlFor="maxClips">Max Clips</Label>
                                <Input
                                    id="maxClips"
                                    type="number"
                                    min={1}
                                    max={50000}
                                    value={maxClips}
                                    onChange={(e) => setMaxClips(Number(e.target.value) || 50)}
                                />
                            </div>
                        </div>
                        <div className="flex items-center gap-3 mt-4">
                            <Button
                                onClick={handleFetch}
                                disabled={!bucketPath.trim() || previewMutation.isPending}
                            >
                                <RefreshCw className={`h-4 w-4 mr-2 ${previewMutation.isPending ? 'animate-spin' : ''}`} />
                                {previewMutation.isPending ? 'Loading...' : 'Fetch from GCS'}
                            </Button>
                            {preview && (
                                <span className="text-sm text-muted-foreground">
                                    Showing {preview.clips.length} of {preview.total_clips} clips
                                    {' · '}
                                    {preview.videos.length} of {preview.total_videos} videos
                                </span>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {preview && (
                    <>
                        {/* Clip metadata output */}
                        <Card className="mb-4">
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-mono">
                                    clip_metadata.jsonl
                                </CardTitle>
                                <div className="flex gap-1">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => handleCopy(clipJsonl, 'Clip metadata')}
                                    >
                                        <Copy className="h-3 w-3 mr-1" />
                                        Copy
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() =>
                                            handleDownload(clipJsonl, 'clip_metadata.jsonl')
                                        }
                                    >
                                        <Download className="h-3 w-3 mr-1" />
                                        Download
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <pre className="bg-muted rounded p-3 text-xs font-mono overflow-auto max-h-64 whitespace-pre">
                                    {clipJsonl}
                                </pre>
                            </CardContent>
                        </Card>

                        {/* Video metadata output */}
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-mono">
                                    video_metadata.jsonl
                                </CardTitle>
                                <div className="flex gap-1">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => handleCopy(videoJsonl, 'Video metadata')}
                                    >
                                        <Copy className="h-3 w-3 mr-1" />
                                        Copy
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() =>
                                            handleDownload(videoJsonl, 'video_metadata.jsonl')
                                        }
                                    >
                                        <Download className="h-3 w-3 mr-1" />
                                        Download
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <pre className="bg-muted rounded p-3 text-xs font-mono overflow-auto max-h-64 whitespace-pre">
                                    {videoJsonl}
                                </pre>
                            </CardContent>
                        </Card>
                    </>
                )}
            </div>
        </AppSidebar>
    );
}
