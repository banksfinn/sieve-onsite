/**
 * AuthCard - A centered card layout for authentication pages (login, register, etc.).
 *
 * Uses composition pattern with sub-components for flexible content arrangement.
 *
 * @example
 * ```tsx
 * <AuthCard>
 *     <AuthCard.Header
 *         title="Welcome back"
 *         description="Sign in to your account"
 *     />
 *     <AuthCard.Content>
 *         <GoogleLoginButton onSuccess={handleSuccess} />
 *     </AuthCard.Content>
 *     <AuthCard.Footer>
 *         <Link to="/register">Create an account</Link>
 *     </AuthCard.Footer>
 * </AuthCard>
 * ```
 */

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface AuthCardProps {
    /** Additional classes for the outer container */
    className?: string;
    /** Card content (use AuthCard sub-components) */
    children: React.ReactNode;
}

interface AuthCardHeaderProps {
    /** Main heading text */
    title: string;
    /** Optional description below the title */
    description?: string;
    /** Additional classes */
    className?: string;
}

interface AuthCardContentProps {
    /** Content to render inside the card body */
    children: React.ReactNode;
    /** Additional classes */
    className?: string;
}

interface AuthCardFooterProps {
    /** Footer content (typically links or secondary actions) */
    children: React.ReactNode;
    /** Additional classes */
    className?: string;
}

function AuthCardRoot({ className, children }: AuthCardProps) {
    return (
        <div className={cn('flex min-h-screen items-center justify-center p-4', className)}>
            <Card className="w-full max-w-md">{children}</Card>
        </div>
    );
}

function AuthCardHeader({ title, description, className }: AuthCardHeaderProps) {
    return (
        <CardHeader className={cn('text-center', className)}>
            <CardTitle className="text-2xl">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
    );
}

function AuthCardContent({ children, className }: AuthCardContentProps) {
    return <CardContent className={cn('space-y-4', className)}>{children}</CardContent>;
}

function AuthCardFooter({ children, className }: AuthCardFooterProps) {
    return <CardFooter className={cn('flex justify-center', className)}>{children}</CardFooter>;
}

export const AuthCard = Object.assign(AuthCardRoot, {
    Header: AuthCardHeader,
    Content: AuthCardContent,
    Footer: AuthCardFooter,
});
