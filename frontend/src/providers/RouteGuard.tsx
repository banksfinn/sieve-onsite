/**
 * RouteGuard - Handles route protection and redirects.
 *
 * This component must be used inside a BrowserRouter context.
 * It redirects unauthenticated users from protected routes to login.
 *
 * @example
 * ```tsx
 * <BrowserRouter>
 *   <RouteGuard>
 *     <Router />
 *   </RouteGuard>
 * </BrowserRouter>
 * ```
 */

import { isPublicRoute, LOGIN_ROUTE } from '@/router/routes';
import { useAuthState } from '@/store/components/authSlice';
import { ReactNode, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface RouteGuardProps {
    children: ReactNode;
}

export default function RouteGuard({ children }: RouteGuardProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, isInitialized } = useAuthState();

    useEffect(() => {
        if (!isInitialized) {
            return;
        }

        const isPublic = isPublicRoute(location.pathname);

        if (!user && !isPublic) {
            // Redirect to login, preserving the intended destination
            navigate(LOGIN_ROUTE, {
                replace: true,
                state: { from: location.pathname },
            });
        }
    }, [isInitialized, user, location.pathname, navigate]);

    return <>{children}</>;
}
