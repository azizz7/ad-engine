import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { formatDate, formatNumber, formatShortDate } from '@/lib/format';

interface PerformanceChartsProps {
  data: any[];
}

export default function PerformanceCharts({ data }: PerformanceChartsProps) {
  if (!data || data.length === 0) return null;

  const chartData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Cap the number of x-axis labels shown (~6) regardless of how many days
  // are in the dataset, so labels never overlap into an unreadable smear.
  const tickInterval = Math.max(0, Math.ceil(chartData.length / 6) - 1);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-popover border border-border p-3 rounded-lg shadow-lg">
          <p className="text-sm font-semibold mb-2">{formatDate(label)}</p>
          {payload.map((p: any) => (
            <p key={p.name} className="text-sm" style={{ color: p.color }}>
              {p.name}: {p.name.includes('Spend') || p.name.includes('Revenue') ? '$' : ''}
              {formatNumber(p.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Spend vs Revenue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ left: -12 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.2} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatShortDate}
                  interval={tickInterval}
                  stroke="#888"
                  fontSize={12}
                />
                <YAxis stroke="#888" fontSize={12} tickFormatter={(v) => formatNumber(v)} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="spend" name="Spend" stroke="#ef4444" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">CTR & Conversion Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ left: -12, right: -12 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.2} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatShortDate}
                  interval={tickInterval}
                  stroke="#888"
                  fontSize={12}
                />
                <YAxis yAxisId="left" stroke="#888" fontSize={12} tickFormatter={(v) => formatNumber(v)} />
                <YAxis yAxisId="right" orientation="right" stroke="#888" fontSize={12} tickFormatter={(v) => formatNumber(v)} />
                <Tooltip content={<CustomTooltip />} />
                <Line yAxisId="left" type="monotone" dataKey="clicks" name="Clicks" stroke="#eab308" strokeWidth={2} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="conversions" name="Conversions" stroke="#a855f7" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
