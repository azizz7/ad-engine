'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Activity, LogOut, Plus, Facebook, Chrome } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import MetricsOverview from '@/components/MetricsOverview';
import PerformanceCharts from '@/components/PerformanceCharts';
import TopPerformers from '@/components/TopPerformers';
import InsightsPanel from '@/components/InsightsPanel';

import { cn } from '@/lib/utils';

export default function Dashboard() {
  // Extract token
  const { logout, isAuthenticated, token } = useAuth();
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock Connection States
  const [isFacebookConnected, setIsFacebookConnected] = useState(false);
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);

  // Demo Mode State
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Auth Config
  const authConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    // If we have a dataset, load its data
    if (datasetId && token) {
      loadDashboardData(datasetId);
    } else if (token) {
      // Try to load latest dataset
      fetchLatestDataset();
    }
  }, [datasetId, token]);

  const fetchLatestDataset = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/datasets', authConfig);
      if (response.data && response.data.length > 0) {
        setDatasetId(response.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch datasets', err);
    }
  };

  const loadDashboardData = async (id: number) => {
    setLoading(true);
    try {
      const [analyticsRes, insightsRes, dataRes] = await Promise.all([
        axios.get(`http://localhost:8000/api/analytics?dataset_id=${id}`, authConfig),
        axios.get(`http://localhost:8000/api/insights?dataset_id=${id}`, authConfig),
        axios.get(`http://localhost:8000/api/data?dataset_id=${id}`, authConfig)
      ]);

      setAnalytics(analyticsRes.data);
      setInsights(insightsRes.data);
      setChartData(dataRes.data);
    } catch (err) {
      console.error('Error loading dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleIntegration = async (platform: 'facebook' | 'google') => {
    setLoading(true);
    try {
      // 1. Connect
      await axios.post(`http://localhost:8000/api/integrations/${platform}/connect`, {}, authConfig);

      if (platform === 'facebook') setIsFacebookConnected(true);
      if (platform === 'google') setIsGoogleConnected(true);

      // 2. Sync Data
      const syncRes = await axios.post(`http://localhost:8000/api/integrations/${platform}/sync?use_mock=${isDemoMode}`, {}, authConfig);

      // 3. Handle Result
      if (syncRes.data.rows === 0) {
        alert(syncRes.data.message);
      } else if (syncRes.data.dataset_id) {
        setDatasetId(syncRes.data.dataset_id);
      }

    } catch (err) {
      console.error(`Failed to connect ${platform}`, err);
    } finally {
      setLoading(false);
    }
  };





  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen p-6 space-y-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8 text-primary" />
            Ad Intelligence Engine
          </h1>
          <p className="text-muted-foreground mt-1">
            Real-time analytics and predictive insights for your campaigns.
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Demo Mode Toggle */}
          <div className="flex items-center space-x-2 bg-secondary/50 p-2 rounded-lg border border-border/50">
            <span className={cn("text-xs font-medium", !isDemoMode ? "text-primary" : "text-muted-foreground")}>Real Data</span>
            <button
              onClick={() => setIsDemoMode(!isDemoMode)}
              className={cn(
                "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                isDemoMode ? "bg-primary" : "bg-input"
              )}
            >
              <span className={cn("translate-x-0 inline-block h-3 w-3 transform rounded-full bg-white transition transition-transform", isDemoMode ? "translate-x-5" : "translate-x-1")} />
            </button>
            <span className={cn("text-xs font-medium", isDemoMode ? "text-primary" : "text-muted-foreground")}>Simulation</span>
          </div>

          {/* Functional Integrations */}
          <Button
            variant={isFacebookConnected ? "secondary" : "outline"}
            size="sm"
            className="hidden lg:flex gap-2 transition-all relative overflow-hidden"
            onClick={() => handleIntegration('facebook')}
            disabled={loading}
          >
            <div className="absolute inset-0 bg-blue-500/10 pointer-events-none" style={{ opacity: isFacebookConnected ? 1 : 0 }} />
            <Facebook className={cn("h-4 w-4 relative z-10", isFacebookConnected ? "text-blue-500 fill-current" : "text-blue-600")} />
            <span className="relative z-10">{isFacebookConnected ? "Facebook Synced" : "Connect Facebook"}</span>
          </Button>
          <Button
            variant={isGoogleConnected ? "secondary" : "outline"}
            size="sm"
            className="hidden lg:flex gap-2 transition-all relative overflow-hidden"
            onClick={() => handleIntegration('google')}
            disabled={loading}
          >
            <div className="absolute inset-0 bg-red-500/10 pointer-events-none" style={{ opacity: isGoogleConnected ? 1 : 0 }} />
            <Chrome className={cn("h-4 w-4 relative z-10", isGoogleConnected ? "text-red-500 fill-current" : "text-red-500")} />
            <span className="relative z-10">{isGoogleConnected ? "Google Synced" : "Connect Google"}</span>
          </Button>

          <Button variant="ghost" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Col: Upload & Stats */}
        <div className="lg:col-span-8 space-y-6">
          {!datasetId && (
            <div className="mb-6">
              <FileUpload onUploadSuccess={setDatasetId} />
            </div>
          )}

          {datasetId && (
            <MetricsOverview analytics={analytics} />
          )}

          {chartData.length > 0 && (
            <PerformanceCharts data={chartData} />
          )}
        </div>

        {/* Right Col: Insights & Top Ads */}
        <div className="lg:col-span-4 space-y-6">
          {datasetId && (
            <>
              <div className="flex justify-between items-center mb-2">
                <Button variant="outline" size="sm" onClick={() => setDatasetId(null)}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Upload
                </Button>
              </div>
              <InsightsPanel data={insights} />
              <TopPerformers analytics={analytics} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
