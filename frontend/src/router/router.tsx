import { Navigate, Route, Routes } from 'react-router-dom';
import ChatPage from '@/pages/ChatPage';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
import RegisterPage from '@/pages/RegisterPage';
import TagsPage from '@/pages/TagsPage';
import TodoPage from '@/pages/TodoPage';

export default function Router() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/tags" element={<TagsPage />} />
            <Route path="/todos" element={<TodoPage />} />
        </Routes>
    );
}
