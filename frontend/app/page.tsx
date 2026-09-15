'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Activity, LogOut } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import DatasetSwitcher from '@/components/DatasetSwitcher';
import DataSourceMenu from '@/components/DataSourceMenu';
import IntegrationButtons from '@/components/IntegrationButtons';
import MetricsOverview from '@/components/MetricsOverview';
import PerformanceCharts from '@/components/PerformanceCharts';
import TopPerformers from '@/components/TopPerformers';
import InsightsPanel from '@/components/InsightsPanel';
import ForecastCard from '@/components/ForecastCard';
import ErrorBanner from '@/components/ErrorBanner';
import DashboardSkeleton from '@/components/DashboardSkeleton';

export default function Dashboard() {
  const { logout, isAuthenticated, token } = useAuth();
  const [datasetId, setDatasetId] = useState<number | null>(null);
  // Explicit "show the upload form" intent, kept separate from datasetId so
  // "Upload new dataset" can't be silently undone by the auto-select-latest
  // effect below re-populating datasetId from the datasets list.
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [hasAutoSelected, setHasAutoSelected] = useState(false);
  const [datasetsRefreshToken, setDatasetsRefreshToken] = useState(0);

  const [analytics, setAnalytics] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [predictions, setPredictions] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isFacebookConnected, setIsFacebookConnected] = useState(false);
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // On first load with a valid session, select the most recently uploaded
  // dataset (if any). Runs once per session, so it can never fight with a
  // user-initiated action like "Upload new dataset" or "Delete".
  useEffect(() => {
    if (!token || hasAutoSelected) return;

    api
      .get('/api/datasets')
      .then((res) => {
        if (res.data?.length > 0) setDatasetId(res.data[0].id);
      })
      .catch((err) => console.error('Failed to fetch datasets', err))
      .finally(() => setHasAutoSelected(true));
  }, [token, hasAutoSelected]);

  useEffect(() => {
    if (!datasetId || !token) return;

    setLoading(true);
    setError(null);

    Promise.all([
      api.get(`/api/analytics?dataset_id=${datasetId}`),
      api.get(`/api/insights?dataset_id=${datasetId}`),
      api.get(`/api/data?dataset_id=${datasetId}`),
      api.get(`/api/predictions?dataset_id=${datasetId}`).catch(() => ({ data: null })),
    ])
      .then(([analyticsRes, insightsRes, dataRes, predictionsRes]) => {
        setAnalytics(analyticsRes.data);
        setInsights(insightsRes.data);
        setChartData(dataRes.data);
        setPredictions(predictionsRes.data);
      })
      .catch((err) => {
        console.error('Error loading dashboard data', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data. Please try again.');
      })
      .finally(() => setLoading(false));
  }, [datasetId, token]);

  const handleUploadSuccess = (newDatasetId: number) => {
    setDatasetId(newDatasetId);
    setShowUploadForm(false);
    setHasAutoSelected(true);
    setDatasetsRefreshToken((n) => n + 1);
  };

  const handleDatasetDeleted = (deletedId: number) => {
    setDatasetsRefreshToken((n) => n + 1);
    if (deletedId === datasetId) {
      setDatasetId(null);
      setAnalytics(null);
      setInsights(null);
      setChartData([]);
      setPredictions(null);
      setShowUploadForm(true);
    }
  };

  const handleIntegration = async (platform: 'facebook' | 'google') => {
    setLoading(true);
    setError(null);
    try {
      await api.post(`/api/integrations/${platform}/connect`, {});
      if (platform === 'facebook') setIsFacebookConnected(true);
      if (platform === 'google') setIsGoogleConnected(true);

      const syncRes = await api.post(`/api/integrations/${platform}/sync?use_mock=${isDemoMode}`, {});

      if (syncRes.data.rows === 0) {
        setError(syncRes.data.message);
      } else if (syncRes.data.dataset_id) {
        setShowUploadForm(false);
        setDatasetId(syncRes.data.dataset_id);
        setDatasetsRefreshToken((n) => n + 1);
      }
    } catch (err: any) {
      console.error(`Failed to connect ${platform}`, err);
      setError(err.response?.data?.detail || `Failed to connect to ${platform}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  const showUpload = showUploadForm || (!datasetId && hasAutoSelected);

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 space-y-6 max-w-7xl mx-auto">
      <header className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="font-semibold whitespace-nowrap">Ad Intelligence Engine</span>
          </div>
          {!showUpload && (
            <DatasetSwitcher
              selectedDatasetId={datasetId}
              onSelect={setDatasetId}
              onUploadNew={() => setShowUploadForm(true)}
              onDeleted={handleDatasetDeleted}
              refreshToken={datasetsRefreshToken}
            />
          )}
        </div>
        <div className="flex items-center gap-2">
          {!showUpload && (
            <DataSourceMenu
              isDemoMode={isDemoMode}
              onToggleDemoMode={() => setIsDemoMode(!isDemoMode)}
              onConnect={handleIntegration}
              isFacebookConnected={isFacebookConnected}
              isGoogleConnected={isGoogleConnected}
              loading={loading}
            />
          )}
          <Button variant="ghost" size="sm" onClick={() => logout()}>
            <LogOut className="h-4 w-4 mr-2" />
            Sign out
          </Button>
        </div>
      </header>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {showUpload ? (
        <div className="flex flex-col items-center gap-8 py-10">
          <div className="w-full max-w-lg text-center space-y-1">
            <h1 className="text-xl font-semibold">Upload your ad performance data</h1>
            <p className="text-sm text-muted-foreground">
              Get metrics, a 7-day forecast, and plain-English recommendations in seconds.
            </p>
          </div>
          <div className="w-full max-w-lg">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
          <div className="flex flex-col items-center gap-3">
            <p className="text-xs text-muted-foreground">or import from a connected platform</p>
            <IntegrationButtons
              isDemoMode={isDemoMode}
              onToggleDemoMode={() => setIsDemoMode(!isDemoMode)}
              onConnect={handleIntegration}
              isFacebookConnected={isFacebookConnected}
              isGoogleConnected={isGoogleConnected}
              loading={loading}
            />
          </div>
        </div>
      ) : (
        <>
          {loading && !analytics ? (
            <DashboardSkeleton />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-8 space-y-6">
                <MetricsOverview analytics={analytics} />
                <PerformanceCharts data={chartData} />
              </div>
              <div className="lg:col-span-4 space-y-6">
                <ForecastCard predictions={predictions} />
                <InsightsPanel data={insights} />
                <TopPerformers analytics={analytics} />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
