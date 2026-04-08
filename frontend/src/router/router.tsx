import { Navigate, Route, Routes } from 'react-router-dom';
import AdminPage from '@/pages/AdminPage';
import ClipViewerPage from '@/pages/ClipViewerPage';
import DatasetDetailPage from '@/pages/DatasetDetailPage';
import DatasetsPage from '@/pages/DatasetsPage';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
import RegisterPage from '@/pages/RegisterPage';
import SeedDatasetPage from '@/pages/SeedDatasetPage';
import VersionEditorPage from '@/pages/VersionEditorPage';

export default function Router() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/datasets" element={<DatasetsPage />} />
            <Route path="/dataset/:datasetId" element={<DatasetDetailPage />} />
            <Route path="/dataset/:datasetId/version/:versionId/edit" element={<VersionEditorPage />} />
            <Route path="/dataset/:datasetId/version/:versionId/clip/:clipId" element={<ClipViewerPage />} />
            <Route path="/tools/seed-dataset" element={<SeedDatasetPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/register" element={<RegisterPage />} />
        </Routes>
    );
}
