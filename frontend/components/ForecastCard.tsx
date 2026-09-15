import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatCurrency, formatNumber } from '@/lib/format';

interface ForecastPoint {
  predicted_value: number;
  lower_bound: number;
  upper_bound: number;
}

interface ForecastCardProps {
  predictions: { revenue?: ForecastPoint[]; conversions?: ForecastPoint[] } | null;
}

function sum(points: ForecastPoint[] | undefined, key: keyof ForecastPoint) {
  return (points || []).reduce((total, p) => total + p[key], 0);
}

function trendDirection(points: ForecastPoint[] | undefined) {
  if (!points || points.length < 2) return 'flat';
  const delta = points[points.length - 1].predicted_value - points[0].predicted_value;
  if (Math.abs(delta) < points[0].predicted_value * 0.01) return 'flat';
  return delta > 0 ? 'up' : 'down';
}

export default function ForecastCard({ predictions }: ForecastCardProps) {
  const revenue = predictions?.revenue;
  const conversions = predictions?.conversions;

  if (!revenue && !conversions) return null;

  const direction = trendDirection(revenue ?? conversions);
  const days = (revenue ?? conversions)?.length ?? 0;

  const DirectionIcon = direction === 'up' ? TrendingUp : direction === 'down' ? TrendingDown : Minus;
  const directionColor =
    direction === 'up' ? 'text-green-500' : direction === 'down' ? 'text-red-500' : 'text-muted-foreground';

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <DirectionIcon className={`h-4 w-4 ${directionColor}`} />
          Next {days}-Day Forecast
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {revenue && (
          <p>
            Revenue:{' '}
            <span className="font-semibold text-foreground">
              {formatCurrency(Math.round(sum(revenue, 'predicted_value')))}
            </span>
            <span className="text-muted-foreground">
              {' '}
              ({formatCurrency(Math.round(sum(revenue, 'lower_bound')))}–
              {formatCurrency(Math.round(sum(revenue, 'upper_bound')))})
            </span>
          </p>
        )}
        {conversions && (
          <p>
            Conversions:{' '}
            <span className="font-semibold text-foreground">
              {formatNumber(Math.round(sum(conversions, 'predicted_value')))}
            </span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}
