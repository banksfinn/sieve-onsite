import * as React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, LogOut, Database, Shield, User, UserX, Wrench, type LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { clearUser, setUser, useCurrentUser } from '@/store/components/authSlice';
import { useAppDispatch } from '@/store/hooks';
import { useStopImpersonation } from '@/openapi/sieveOnsite';
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
function getNavGroups(role?: string, accessLevel?: string): NavGroup[] {
    const main: NavItem[] = [
        { title: 'Home', url: '/home', icon: Home },
    ];

    // GTM and researchers see datasets
    if (role === 'gtm' || role === 'researcher' || accessLevel === 'admin') {
        main.push({ title: 'Datasets', url: '/datasets', icon: Database });
    }

    main.push({ title: 'Profile', url: '/profile', icon: User });

    const groups: NavGroup[] = [{ label: 'Main', items: main }];

    if (accessLevel === 'admin') {
        groups.push({
            label: 'Admin',
            items: [
                { title: 'Admin Panel', url: '/admin', icon: Shield },
                { title: 'Seed Dataset', url: '/tools/seed-dataset', icon: Wrench },
            ],
        });
    }

    return groups;
}

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
    navGroups,
    header,
    footer,
    className,
    children,
}: AppSidebarProps) {
    const location = useLocation();
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const currentUser = useCurrentUser();
    const resolvedNavGroups = navGroups ?? getNavGroups(currentUser?.role, currentUser?.access_level);

    const isImpersonating = currentUser?.impersonated_by != null;

    const { mutate: stopImpersonation } = useStopImpersonation({
        mutation: {
            onSuccess: (data) => {
                dispatch(setUser(data));
                navigate('/home');
            },
        },
    });

    const handleLogout = () => {
        dispatch(clearUser());
        navigate('/login');
    };

    return (
        <SidebarProvider>
            <Sidebar collapsible="icon" className={cn(className)}>
                {header && <SidebarHeader>{header}</SidebarHeader>}

                <SidebarContent>
                    {resolvedNavGroups.map((group) => (
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
                        {isImpersonating && (
                            <SidebarMenuItem>
                                <SidebarMenuButton
                                    onClick={() => stopImpersonation()}
                                    tooltip="Stop Impersonating"
                                    className="text-amber-600 hover:text-amber-700 hover:bg-amber-50"
                                >
                                    <UserX className="h-4 w-4" />
                                    <span>Stop Impersonating</span>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        )}
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
