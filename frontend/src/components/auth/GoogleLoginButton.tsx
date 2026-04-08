/**
 * GoogleLoginButton - A button that triggers Google OAuth login flow.
 *
 * Uses Google One Tap / Sign-In which returns a JWT ID token for authentication.
 * Handles the OAuth callback and calls the backend API to authenticate.
 * After successful login, fetches user data and stores it in Redux.
 *
 * @example
 * ```tsx
 * <GoogleLoginButton
 *     onSuccess={() => navigate('/dashboard')}
 *     onError={(error) => showSnackbar(error)}
 * />
 * ```
 */

import { useGoogleLogin, useRefreshToken } from '@/openapi/fullstackBase';
import { setUser } from '@/store/components/authSlice';
import { useAppDispatch } from '@/store/hooks';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

interface GoogleLoginButtonProps {
    /** Callback when login succeeds */
    onSuccess?: () => void;
    /** Callback when login fails */
    onError?: (error: string) => void;
    /** Additional classes */
    className?: string;
}

export function GoogleLoginButton({ onSuccess, onError, className }: GoogleLoginButtonProps) {
    const dispatch = useAppDispatch();
    const googleLoginMutation = useGoogleLogin();
    const refreshMutation = useRefreshToken();

    const handleCredentialResponse = async (credentialResponse: CredentialResponse) => {
        if (!credentialResponse.credential) {
            onError?.('No credential received from Google');
            return;
        }

        try {
            const result = await googleLoginMutation.mutateAsync({
                data: { credential: credentialResponse.credential },
            });

            if (result.success) {
                // Fetch user data and store in Redux
                const user = await refreshMutation.mutateAsync();
                dispatch(setUser(user));
                onSuccess?.();
            } else {
                onError?.(result.message || 'Login failed');
            }
        } catch (error) {
            onError?.(error instanceof Error ? error.message : 'Login failed');
        }
    };

    return (
        <div className={className}>
            <GoogleLogin
                onSuccess={handleCredentialResponse}
                onError={() => onError?.('Google login failed')}
                useOneTap={false}
                theme="outline"
                size="large"
                width={300}
            />
        </div>
    );
}
