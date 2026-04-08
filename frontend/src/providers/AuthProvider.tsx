/**
 * AuthProvider - Manages authentication state initialization.
 *
 * This provider wraps the application at the top level and handles:
 * - Initial authentication check on app load (via refresh endpoint)
 * - Storing user state in Redux
 * - Blocking render until auth state is initialized
 *
 * Note: This provider has no router dependency and can wrap BrowserRouter.
 * Route protection/redirects are handled by RouteGuard inside the router.
 *
 * @example
 * ```tsx
 * // In App.tsx
 * <Provider store={store}>
 *   <AuthProvider>
 *     <BrowserRouter>
 *       <RouteGuard>
 *         <Router />
 *       </RouteGuard>
 *     </BrowserRouter>
 *   </AuthProvider>
 * </Provider>
 * ```
 */

import { refreshToken } from '@/openapi/fullstackBase';
import { clearUser, setUser, useAuthState } from '@/store/components/authSlice';
import { useAppDispatch } from '@/store/hooks';
import { ReactNode, useEffect, useRef } from 'react';

interface AuthProviderProps {
    children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
    const dispatch = useAppDispatch();
    const { isInitialized } = useAuthState();

    // Track if we've already attempted refresh to prevent loops
    const hasAttemptedRefresh = useRef(false);

    // On mount, attempt to refresh the user's session
    useEffect(() => {
        if (hasAttemptedRefresh.current) {
            return;
        }
        hasAttemptedRefresh.current = true;

        // Use the raw function instead of the hook to avoid QueryClient dependency issues
        refreshToken()
            .then((data) => {
                dispatch(setUser(data));
            })
            .catch(() => {
                dispatch(clearUser());
            });
    }, [dispatch]);

    // Show nothing while initializing to prevent flash of protected content
    if (!isInitialized) {
        return null;
    }

    return <>{children}</>;
}
