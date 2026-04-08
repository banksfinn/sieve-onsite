import { AuthCard, GoogleLoginButton } from '@/components/auth';
import { addSnackbarMessage } from '@/store/components/snackbarSlice';
import { useAppDispatch } from '@/store/hooks';
import { Link, useNavigate } from 'react-router-dom';

export default function LoginPage() {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();

    const handleLoginSuccess = () => {
        dispatch(
            addSnackbarMessage({
                message: 'Successfully signed in!',
                severity: 'success',
                duration: 3000,
            })
        );
        navigate('/home');
    };

    const handleLoginError = (error: string) => {
        dispatch(
            addSnackbarMessage({
                message: error,
                severity: 'error',
                duration: 5000,
            })
        );
    };

    return (
        <AuthCard>
            <AuthCard.Header
                title="Welcome back"
                description="Sign in to your account to continue"
            />
            <AuthCard.Content>
                <GoogleLoginButton onSuccess={handleLoginSuccess} onError={handleLoginError} />
            </AuthCard.Content>
            <AuthCard.Footer>
                <p className="text-sm text-muted-foreground">
                    Don't have an account?{' '}
                    <Link
                        to="/register"
                        className="font-medium text-primary underline-offset-4 hover:underline"
                    >
                        Create one
                    </Link>
                </p>
            </AuthCard.Footer>
        </AuthCard>
    );
}
