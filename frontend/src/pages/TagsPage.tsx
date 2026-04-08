import { AppSidebar } from '@/components/common';
import { TagManager } from '@/components/tags';

export default function TagsPage() {
    return (
        <AppSidebar>
            <div className="container mx-auto max-w-2xl py-8 px-4">
                <TagManager />
            </div>
        </AppSidebar>
    );
}
