import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Trophy } from 'lucide-react';
import { formatCurrency } from '@/lib/format';

interface TopPerformersProps {
  analytics: any;
}

export default function TopPerformers({ analytics }: TopPerformersProps) {
  if (!analytics?.best_performing || analytics.best_performing.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Trophy className="h-5 w-5 text-yellow-500" />
          Top Performers
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="py-3 text-left font-medium text-muted-foreground">Ad Name</th>
                <th className="py-3 text-right font-medium text-muted-foreground">Spend</th>
                <th className="py-3 text-right font-medium text-muted-foreground">Revenue</th>
                <th className="py-3 text-right font-medium text-muted-foreground">ROAS</th>
              </tr>
            </thead>
            <tbody>
              {analytics.best_performing.map((ad: any, i: number) => (
                <tr key={i} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                  <td className="py-3 font-medium truncate max-w-[200px]">
                    {ad.ad_name || ad.campaign_name || 'Unknown'}
                  </td>
                  <td className="py-3 text-right">{formatCurrency(ad.spend || 0)}</td>
                  <td className="py-3 text-right text-green-500">{formatCurrency(ad.revenue || 0)}</td>
                  <td className="py-3 text-right font-bold">{(ad.metric_value || 0).toFixed(2)}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
