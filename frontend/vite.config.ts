import react from '@vitejs/plugin-react-swc';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [react()],
    css: {
        postcss: './postcss.config.js',
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    define: {
        'process.env': {},
    },
    // This is for local development!
    server: {
        host: true,
        proxy: {
            '/api/gateway/': {
                target: process.env.FULLSTACK_API_URL || 'http://localhost:1301',
                changeOrigin: true,
                secure: false,
            },
        },
        port: 1300,
    },
});
