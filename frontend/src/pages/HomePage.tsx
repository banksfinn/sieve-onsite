import { AppSidebar } from '@/components/common';

export default function HomePage() {
    return (
        <AppSidebar>
            <div className="container mx-auto max-w-4xl py-8 px-4">
                <h1 className="text-2xl font-bold mb-6">Home</h1>
                <p className="text-muted-foreground">Welcome to Sieve Sample Review.</p>
            </div>
        </AppSidebar>
    );
}
