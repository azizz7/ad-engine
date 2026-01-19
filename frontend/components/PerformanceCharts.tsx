import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface PerformanceChartsProps {
  data: any[];
}

export default function PerformanceCharts({ data }: PerformanceChartsProps) {
  if (!data || data.length === 0) return null;

  // Sort by date
  const chartData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-popover border border-border p-3 rounded-lg shadow-lg">
          <p className="text-sm font-semibold mb-2">{new Date(label).toLocaleDateString()}</p>
          {payload.map((p: any) => (
            <p key={p.name} className="text-sm" style={{ color: p.color }}>
              {p.name}: {p.name.includes('Spend') || p.name.includes('Revenue') ? '$' : ''}{p.value.toLocaleString()}
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
          <CardTitle>Spend vs Revenue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.2} />
                <XAxis
                  dataKey="date"
                  tickFormatter={(str) => new Date(str).toLocaleDateString()}
                  stroke="#888"
                  fontSize={12}
                />
                <YAxis stroke="#888" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="spend"
                  name="Spend"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  name="Revenue"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>CTR & Conversion Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.2} />
                <XAxis
                  dataKey="date"
                  tickFormatter={(str) => new Date(str).toLocaleDateString()}
                  stroke="#888"
                  fontSize={12}
                />
                <YAxis yAxisId="left" stroke="#888" fontSize={12} />
                <YAxis yAxisId="right" orientation="right" stroke="#888" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="clicks"
                  name="Clicks"
                  stroke="#eab308"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="conversions"
                  name="Conversions"
                  stroke="#a855f7"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
