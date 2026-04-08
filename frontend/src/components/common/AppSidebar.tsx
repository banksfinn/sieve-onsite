import * as React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, LogOut, User, type LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { clearUser } from '@/store/components/authSlice';
import { useAppDispatch } from '@/store/hooks';
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarProvider,
    SidebarInset,
    SidebarTrigger,
    SidebarRail,
} from '@/components/ui/sidebar';

/** Navigation item configuration */
export interface NavItem {
    /** Display title for the nav item */
    title: string;
    /** URL path to navigate to */
    url: string;
    /** Lucide icon component */
    icon: LucideIcon;
}

/** Navigation group configuration */
export interface NavGroup {
    /** Group label displayed above items */
    label: string;
    /** Navigation items in this group */
    items: NavItem[];
}

/** Props for the AppSidebar component */
interface AppSidebarProps {
    /** Navigation groups to display in the sidebar */
    navGroups?: NavGroup[];
    /** Optional header content */
    header?: React.ReactNode;
    /** Optional footer content */
    footer?: React.ReactNode;
    /** Additional class names */
    className?: string;
    /** Child content to render in the main area */
    children?: React.ReactNode;
}

/** Default navigation groups if none provided */
const defaultNavGroups: NavGroup[] = [
    {
        label: 'Main',
        items: [
            { title: 'Home', url: '/home', icon: Home },
            { title: 'Profile', url: '/profile', icon: User },
        ],
    },
];

/**
 * Application sidebar component with navigation.
 *
 * Wraps content in a SidebarProvider and provides a responsive sidebar
 * with navigation groups. Supports mobile view with sheet-based drawer.
 *
 * @example
 * ```tsx
 * <AppSidebar
 *   navGroups={[
 *     {
 *       label: 'Main',
 *       items: [
 *         { title: 'Dashboard', url: '/dashboard', icon: Home }
 *       ]
 *     }
 *   ]}
 * >
 *   <YourPageContent />
 * </AppSidebar>
 * ```
 */
export function AppSidebar({
    navGroups = defaultNavGroups,
    header,
    footer,
    className,
    children,
}: AppSidebarProps) {
    const location = useLocation();
    const navigate = useNavigate();
    const dispatch = useAppDispatch();

    const handleLogout = () => {
        dispatch(clearUser());
        navigate('/login');
    };

    return (
        <SidebarProvider>
            <Sidebar collapsible="icon" className={cn(className)}>
                {header && <SidebarHeader>{header}</SidebarHeader>}

                <SidebarContent>
                    {navGroups.map((group) => (
                        <SidebarGroup key={group.label}>
                            <SidebarGroupLabel>{group.label}</SidebarGroupLabel>
                            <SidebarGroupContent>
                                <SidebarMenu>
                                    {group.items.map((item) => {
                                        const isActive = location.pathname === item.url;
                                        return (
                                            <SidebarMenuItem key={item.title}>
                                                <SidebarMenuButton
                                                    asChild
                                                    isActive={isActive}
                                                    tooltip={item.title}
                                                >
                                                    <Link to={item.url}>
                                                        <item.icon className="h-4 w-4" />
                                                        <span>{item.title}</span>
                                                    </Link>
                                                </SidebarMenuButton>
                                            </SidebarMenuItem>
                                        );
                                    })}
                                </SidebarMenu>
                            </SidebarGroupContent>
                        </SidebarGroup>
                    ))}
                </SidebarContent>

                <SidebarFooter>
                    {footer}
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <SidebarMenuButton onClick={handleLogout} tooltip="Logout">
                                <LogOut className="h-4 w-4" />
                                <span>Logout</span>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarFooter>
                <SidebarRail />
            </Sidebar>

            <SidebarInset>
                <header className="flex h-14 items-center gap-2 border-b px-4">
                    <SidebarTrigger />
                </header>
                <main className="flex-1 p-4">{children}</main>
            </SidebarInset>
        </SidebarProvider>
    );
}
