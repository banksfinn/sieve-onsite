import { Navigate, Route, Routes } from 'react-router-dom';
import AdminPage from '@/pages/AdminPage';
import ClipViewerPage from '@/pages/ClipViewerPage';
import DatasetDetailPage from '@/pages/DatasetDetailPage';
import DatasetsPage from '@/pages/DatasetsPage';
import DeliveriesPage from '@/pages/DeliveriesPage';
import DeliveryDetailPage from '@/pages/DeliveryDetailPage';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
import RegisterPage from '@/pages/RegisterPage';

export default function Router() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/datasets" element={<DatasetsPage />} />
            <Route path="/dataset/:datasetId" element={<DatasetDetailPage />} />
            <Route path="/deliveries" element={<DeliveriesPage />} />
            <Route path="/delivery/:deliveryId" element={<DeliveryDetailPage />} />
            <Route path="/delivery/:deliveryId/clip/:clipId" element={<ClipViewerPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/register" element={<RegisterPage />} />
        </Routes>
    );
}
