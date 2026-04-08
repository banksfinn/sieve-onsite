export const Routes = {
    HOME: '/home',
    DATASETS: '/datasets',
    DATASET_DETAIL: '/dataset/:datasetId',
    VERSION_EDITOR: '/dataset/:datasetId/version/:versionId/edit',
    CLIP_VIEWER: '/dataset/:datasetId/version/:versionId/clip/:clipId',
    SEED_DATASET: '/tools/seed-dataset',
    ADMIN: '/admin',
    LOGIN: '/login',
    REGISTER: '/register',
} as const;

export type RoutePath = (typeof Routes)[keyof typeof Routes];

export const PUBLIC_ROUTES: readonly RoutePath[] = [
    Routes.LOGIN,
    Routes.REGISTER,
] as const;

export const DEFAULT_AUTHENTICATED_ROUTE = Routes.HOME;

export const LOGIN_ROUTE = Routes.LOGIN;

export function isPublicRoute(path: string): boolean {
    return PUBLIC_ROUTES.some((route) => path === route || path.startsWith(`${route}/`));
}
