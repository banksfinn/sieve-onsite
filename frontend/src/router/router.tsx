import { Navigate, Route, Routes } from 'react-router-dom';
import ClipViewerPage from '@/pages/ClipViewerPage';
import DeliveriesPage from '@/pages/DeliveriesPage';
import DeliveryDetailPage from '@/pages/DeliveryDetailPage';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
import RegisterPage from '@/pages/RegisterPage';

export default function Router() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/deliveries" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/deliveries" element={<DeliveriesPage />} />
            <Route path="/delivery/:deliveryId" element={<DeliveryDetailPage />} />
            <Route path="/delivery/:deliveryId/clip/:clipId" element={<ClipViewerPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/register" element={<RegisterPage />} />
        </Routes>
    );
}
