import AuthProvider from '@/providers/AuthProvider';
import RouteGuard from '@/providers/RouteGuard';
import SnackbarProvider from '@/providers/SnackbarProvider';
import Router from '@/router/router';
import { store } from '@/store/store';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: Infinity,
        },
    },
});

const googleClientId = window.env?.GOOGLE_CLIENT_ID || '';

export default function App() {
    return (
        <Provider store={store}>
            <AuthProvider>
                <GoogleOAuthProvider clientId={googleClientId}>
                    <QueryClientProvider client={queryClient}>
                        <SnackbarProvider>
                            <BrowserRouter>
                                <RouteGuard>
                                    <Router />
                                </RouteGuard>
                            </BrowserRouter>
                        </SnackbarProvider>
                    </QueryClientProvider>
                </GoogleOAuthProvider>
            </AuthProvider>
        </Provider>
    );
}
