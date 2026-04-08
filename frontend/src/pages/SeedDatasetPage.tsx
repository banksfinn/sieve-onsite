import { useState, useMemo } from 'react';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useSnackbar } from '@/store/components/snackbarSlice';
import {
    Database,
    Copy,
    Download,
    Shuffle,
} from 'lucide-react';

// --- Generator logic (matches backend/tools/gcs/generate_sample_metadata.py) ---

const FPS_OPTIONS = [24, 25, 29.97, 30, 30.03003, 60];
const RESOLUTION_OPTIONS: [number, number][] = [[1920, 1080], [1280, 720], [3840, 2160], [2560, 1440]];

function pick<T>(arr: T[]): T {
    return arr[Math.floor(Math.random() * arr.length)];
}

function randomFraction(): number {
    const r = Math.random();
    if (r < 0.4) return 0;
    if (r < 0.7) return 1;
    return parseFloat(Math.random().toFixed(8));
}

function randomHex(): string {
    return Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
}

function randomVideoId(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
    const len = 20 + Math.floor(Math.random() * 24);
    return Array.from({ length: len }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

interface ClipMeta {
    video_id: string;
    uri: string;
    clip_start_time: string;
    clip_end_time: string;
    clip_duration: number;
    one_hand_presence_fraction: string | number;
    two_hands_presence_fraction: number;
    phone_screen_presence_fraction: string;
    pc_screen_presence_fraction: string;
    other_screen_presence_fraction: string;
    is_egocentric_fraction: string;
    waist_visible_fraction: number;
    well_lit_fraction: string;
    has_overlay_fraction: string;
}

interface VideoMeta {
    width: string;
    height: string;
    fps: number;
    has_black_bars: boolean;
    is_upright: boolean;
    video_id: string;
}

function generateSample(
    numVideos: number,
    clipsPerVideo: number,
    bucketPrefix: string,
): { clips: ClipMeta[]; videos: VideoMeta[] } {
    const clips: ClipMeta[] = [];
    const videos: VideoMeta[] = [];

    for (let v = 0; v < numVideos; v++) {
        const videoId = randomVideoId();
        const [w, h] = pick(RESOLUTION_OPTIONS);

        videos.push({
            width: String(w),
            height: String(h),
            fps: pick(FPS_OPTIONS),
            has_black_bars: Math.random() < 0.2,
            is_upright: Math.random() < 0.8,
            video_id: videoId,
        });

        let cursor = 0;
        for (let c = 0; c < clipsPerVideo; c++) {
            const gap = 1 + Math.floor(Math.random() * 60);
            const start = cursor + gap;
            const duration = 3 + Math.floor(Math.random() * 417);
            const end = start + duration;

            clips.push({
                video_id: videoId,
                uri: `gs://${bucketPrefix}clips/${videoId}_${randomHex()}.mp4`,
                clip_start_time: String(start),
                clip_end_time: String(end),
                clip_duration: duration,
                one_hand_presence_fraction: String(randomFraction()),
                two_hands_presence_fraction: randomFraction(),
                phone_screen_presence_fraction: String(randomFraction()),
                pc_screen_presence_fraction: String(randomFraction()),
                other_screen_presence_fraction: String(randomFraction()),
                is_egocentric_fraction: String(randomFraction()),
                waist_visible_fraction: randomFraction(),
                well_lit_fraction: String(randomFraction()),
                has_overlay_fraction: String(randomFraction()),
            });
            cursor = end;
        }
    }

    return { clips, videos };
}

// --- Page ---

export default function SeedDatasetPage() {
    const { showSuccess } = useSnackbar();

    const [numVideos, setNumVideos] = useState(10);
    const [clipsPerVideo, setClipsPerVideo] = useState(5);
    const [bucketPrefix, setBucketPrefix] = useState('product-onsite/sample2/');
    const [seed, setSeed] = useState(0); // bump to regenerate

    const { clips, videos } = useMemo(
        () => generateSample(numVideos, clipsPerVideo, bucketPrefix),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [numVideos, clipsPerVideo, bucketPrefix, seed],
    );

    const clipJsonl = clips.map((c) => JSON.stringify(c)).join('\n');
    const videoJsonl = videos.map((v) => JSON.stringify(v)).join('\n');

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
                    <h1 className="text-2xl font-bold">Generate Sample Metadata</h1>
                    <Badge variant="outline" className="text-xs">Dev Tool</Badge>
                </div>

                {/* Controls */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="text-base">Parameters</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div>
                                <Label htmlFor="numVideos">Videos</Label>
                                <Input
                                    id="numVideos"
                                    type="number"
                                    min={1}
                                    max={500}
                                    value={numVideos}
                                    onChange={(e) => setNumVideos(Number(e.target.value) || 1)}
                                />
                            </div>
                            <div>
                                <Label htmlFor="clipsPerVideo">Clips per Video</Label>
                                <Input
                                    id="clipsPerVideo"
                                    type="number"
                                    min={1}
                                    max={50}
                                    value={clipsPerVideo}
                                    onChange={(e) => setClipsPerVideo(Number(e.target.value) || 1)}
                                />
                            </div>
                            <div className="col-span-2">
                                <Label htmlFor="bucket">Bucket Prefix</Label>
                                <Input
                                    id="bucket"
                                    value={bucketPrefix}
                                    onChange={(e) => setBucketPrefix(e.target.value)}
                                    className="font-mono text-sm"
                                />
                            </div>
                        </div>
                        <div className="flex items-center gap-3 mt-4">
                            <Button variant="outline" onClick={() => setSeed((s) => s + 1)}>
                                <Shuffle className="h-4 w-4 mr-2" />
                                Regenerate
                            </Button>
                            <span className="text-sm text-muted-foreground">
                                {clips.length} clips across {videos.length} videos
                            </span>
                        </div>
                    </CardContent>
                </Card>

                {/* Clip metadata output */}
                <Card className="mb-4">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-mono">clip_metadata.jsonl</CardTitle>
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
                                onClick={() => handleDownload(clipJsonl, 'clip_metadata.jsonl')}
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
                        <CardTitle className="text-sm font-mono">video_metadata.jsonl</CardTitle>
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
                                onClick={() => handleDownload(videoJsonl, 'video_metadata.jsonl')}
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
            </div>
        </AppSidebar>
    );
}
