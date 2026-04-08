/**
 * Centralized route configuration for the application.
 *
 * This module defines all page routes and categorizes them by authentication requirements.
 * Use these constants throughout the app to avoid hardcoded route strings.
 */

/**
 * All application routes.
 */
export const Routes = {
    HOME: '/home',
    DELIVERIES: '/deliveries',
    DELIVERY_DETAIL: '/delivery/:deliveryId',
    LOGIN: '/login',
    REGISTER: '/register',
} as const;

export type RoutePath = (typeof Routes)[keyof typeof Routes];

/**
 * Routes that do not require authentication.
 * Users can access these pages without being logged in.
 */
export const PUBLIC_ROUTES: readonly RoutePath[] = [
    Routes.LOGIN,
    Routes.REGISTER,
] as const;

/**
 * The default route to redirect to after successful login.
 */
export const DEFAULT_AUTHENTICATED_ROUTE = Routes.DELIVERIES;

/**
 * The route to redirect to when authentication is required.
 */
export const LOGIN_ROUTE = Routes.LOGIN;

/**
 * Check if a given path is a public route (does not require authentication).
 */
export function isPublicRoute(path: string): boolean {
    return PUBLIC_ROUTES.some((route) => path === route || path.startsWith(`${route}/`));
}
