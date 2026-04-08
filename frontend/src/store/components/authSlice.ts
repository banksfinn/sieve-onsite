import { PayloadAction, createSlice } from '@reduxjs/toolkit';
import { User } from '@/openapi/sieveOnsite';
import { useAppSelector } from '@/store/hooks';
import { RootState } from '@/store/store';

export interface UserAuthState {
    user: User | null;
    isInitialized: boolean;
}

const AUTH_STORAGE_KEY = 'userState';

const loadUserState = (): UserAuthState => {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    if (data === null) {
        return {
            user: null,
            isInitialized: false,
        };
    }
    try {
        const parsed = JSON.parse(data);
        return {
            user: parsed.user ?? null,
            isInitialized: false, // Always re-verify on app load
        };
    } catch (error) {
        console.error('Error parsing user state:', error);
        return {
            user: null,
            isInitialized: false,
        };
    }
};

const saveUserState = (state: UserAuthState) => {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ user: state.user }));
};

const initialState: UserAuthState = loadUserState();

export const authSlice = createSlice({
    name: 'authSlice',
    initialState,
    reducers: {
        setUser: (state, action: PayloadAction<User>) => {
            state.user = action.payload;
            state.isInitialized = true;
            saveUserState(state);
        },
        clearUser: (state) => {
            state.user = null;
            state.isInitialized = true;
            saveUserState(state);
        },
        setInitialized: (state) => {
            state.isInitialized = true;
        },
    },
});

export const { setUser, clearUser, setInitialized } = authSlice.actions;

export const getAuthState = (state: RootState) => state.authSlice;

export const useAuthState = (): UserAuthState => {
    return useAppSelector(getAuthState);
};

export const useCurrentUser = (): User | null => {
    return useAppSelector((state) => state.authSlice.user);
};

export const useIsAuthenticated = (): boolean => {
    return useAppSelector((state) => state.authSlice.user !== null);
};

export default authSlice.reducer;
