import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { useCallback } from 'react';
import { RootState } from '@/store/store';
import { useAppDispatch, useAppSelector } from '@/store/hooks';

/** Severity levels for snackbar messages, ordered by priority */
export type SnackbarSeverity = 'error' | 'warning' | 'success' | 'info';

/** Configuration for a snackbar message */
export interface SnackbarMessage {
    /** The message text to display */
    message: string;
    /** Severity level affecting styling and priority */
    severity: SnackbarSeverity;
    /** Duration in milliseconds before auto-dismissing */
    duration: number;
}

/** Options for showing a snackbar (duration is optional with default) */
export type ShowSnackbarOptions = Omit<SnackbarMessage, 'duration'> & {
    duration?: number;
};

const DEFAULT_DURATION = 5000;

/** Priority order for message severity (lower = higher priority) */
const SEVERITY_PRIORITY: Record<SnackbarSeverity, number> = {
    error: 1,
    warning: 2,
    success: 3,
    info: 4,
};

const sortByPriority = (messages: SnackbarMessage[]): SnackbarMessage[] => {
    return [...messages].sort(
        (a, b) => SEVERITY_PRIORITY[a.severity] - SEVERITY_PRIORITY[b.severity]
    );
};

interface SnackbarState {
    messages: SnackbarMessage[];
}

const initialState: SnackbarState = {
    messages: [],
};

export const snackbarSlice = createSlice({
    name: 'snackbar',
    initialState,
    reducers: {
        addSnackbarMessage: (state, action: PayloadAction<SnackbarMessage>) => {
            state.messages = sortByPriority([...state.messages, action.payload]);
        },
        clearSnackbarMessage: (state) => {
            state.messages.shift();
        },
        clearAllSnackbarMessages: (state) => {
            state.messages = [];
        },
    },
});

export const { addSnackbarMessage, clearSnackbarMessage, clearAllSnackbarMessages } =
    snackbarSlice.actions;

// Selectors
export const selectSnackbarState = (state: RootState) => state.snackbarSlice;
export const selectActiveSnackbarMessage = (state: RootState): SnackbarMessage | null =>
    state.snackbarSlice.messages[0] ?? null;

// Hooks
export const useSnackbarState = () => useAppSelector(selectSnackbarState);
export const useActiveSnackbarMessage = () => useAppSelector(selectActiveSnackbarMessage);

/**
 * Hook to show snackbar messages.
 *
 * @example
 * ```tsx
 * const { showSnackbar, showError, showSuccess } = useSnackbar()
 *
 * showSuccess('Item saved!')
 * showError('Something went wrong')
 * showSnackbar({ message: 'Info', severity: 'info' })
 * ```
 */
export const useSnackbar = () => {
    const dispatch = useAppDispatch();

    const showSnackbar = useCallback(
        (options: ShowSnackbarOptions) => {
            dispatch(
                addSnackbarMessage({
                    ...options,
                    duration: options.duration ?? DEFAULT_DURATION,
                })
            );
        },
        [dispatch]
    );

    const showError = useCallback(
        (message: string, duration?: number) => {
            showSnackbar({ message, severity: 'error', duration });
        },
        [showSnackbar]
    );

    const showWarning = useCallback(
        (message: string, duration?: number) => {
            showSnackbar({ message, severity: 'warning', duration });
        },
        [showSnackbar]
    );

    const showSuccess = useCallback(
        (message: string, duration?: number) => {
            showSnackbar({ message, severity: 'success', duration });
        },
        [showSnackbar]
    );

    const showInfo = useCallback(
        (message: string, duration?: number) => {
            showSnackbar({ message, severity: 'info', duration });
        },
        [showSnackbar]
    );

    const clearAll = useCallback(() => {
        dispatch(clearAllSnackbarMessages());
    }, [dispatch]);

    return {
        showSnackbar,
        showError,
        showWarning,
        showSuccess,
        showInfo,
        clearAll,
    };
};

export default snackbarSlice.reducer;
