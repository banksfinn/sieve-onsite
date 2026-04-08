import { Link, useNavigate } from 'react-router-dom';
import { AuthCard, GoogleLoginButton } from '@/components/auth';
import { useAppDispatch } from '@/store/hooks';
import { addSnackbarMessage } from '@/store/components/snackbarSlice';

export default function RegisterPage() {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();

    const handleRegisterSuccess = () => {
        dispatch(addSnackbarMessage({
            message: 'Account created successfully!',
            severity: 'success',
            duration: 3000,
        }));
        navigate('/home');
    };

    const handleRegisterError = (error: string) => {
        dispatch(addSnackbarMessage({
            message: error,
            severity: 'error',
            duration: 5000,
        }));
    };

    return (
        <AuthCard>
            <AuthCard.Header
                title="Create an account"
                description="Get started with your new account"
            />
            <AuthCard.Content>
                <GoogleLoginButton
                    onSuccess={handleRegisterSuccess}
                    onError={handleRegisterError}
                />
            </AuthCard.Content>
            <AuthCard.Footer>
                <p className="text-sm text-muted-foreground">
                    Already have an account?{' '}
                    <Link
                        to="/login"
                        className="font-medium text-primary underline-offset-4 hover:underline"
                    >
                        Sign in
                    </Link>
                </p>
            </AuthCard.Footer>
        </AuthCard>
    );
}
