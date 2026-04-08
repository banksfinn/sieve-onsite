import { ReactNode, useCallback, useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { clearSnackbarMessage, useActiveSnackbarMessage } from '@/store/components/snackbarSlice'
import { useAppDispatch } from '@/store/hooks'

interface SnackbarProviderProps {
    children: ReactNode
}

const severityStyles = {
    error: 'bg-destructive text-destructive-foreground',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white',
    success: 'bg-green-600 text-white',
}

export default function SnackbarProvider({ children }: SnackbarProviderProps) {
    const dispatch = useAppDispatch()
    const message = useActiveSnackbarMessage()
    const [isVisible, setIsVisible] = useState(false)

    const handleClose = useCallback(() => {
        setIsVisible(false)
        // Wait for exit animation before clearing
        setTimeout(() => {
            dispatch(clearSnackbarMessage())
        }, 150)
    }, [dispatch])

    useEffect(() => {
        if (message) {
            // Trigger enter animation
            requestAnimationFrame(() => setIsVisible(true))

            const timer = setTimeout(handleClose, message.duration)
            return () => clearTimeout(timer)
        } else {
            setIsVisible(false)
        }
    }, [message, handleClose])

    return (
        <>
            {children}
            {message && (
                <div className="fixed inset-x-0 bottom-4 z-50 flex justify-center">
                    <div
                        className={cn(
                            'flex items-center gap-2 rounded-md px-4 py-3 shadow-lg transition-all duration-150',
                            severityStyles[message.severity],
                            isVisible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                        )}
                        role="alert"
                    >
                        <span className="text-sm font-medium">{message.message}</span>
                        <button
                            onClick={handleClose}
                            className="ml-2 rounded-sm opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-white/50"
                            aria-label="Dismiss"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}
        </>
    )
}
