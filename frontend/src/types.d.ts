interface Env {
    GOOGLE_CLIENT_ID: string;
    LOGIN_REDIRECT_URL: string;
}

interface Window {
    env: Env;
}
