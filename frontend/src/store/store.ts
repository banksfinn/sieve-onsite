import { Action, configureStore, ThunkAction } from '@reduxjs/toolkit';
import authSlice from '@/store/components/authSlice';
import snackbarSlice from '@/store/components/snackbarSlice';

export const store = configureStore({
    reducer: {
        authSlice: authSlice,
        snackbarSlice: snackbarSlice,
    },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
    ReturnType,
    RootState,
    unknown,
    Action<string>
>;
