import { Card, CardContent } from '@/components/ui/card';
import { DollarSign, TrendingUp, Eye, Target } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatCurrency, formatNumber } from '@/lib/format';
import { motion } from 'framer-motion';

interface MetricsOverviewProps {
  analytics: any;
}

export default function MetricsOverview({ analytics }: MetricsOverviewProps) {
  if (!analytics) return null;

  const { overall_metrics } = analytics;

  // `null` means "not available for this dataset" (e.g. no revenue column
  // was uploaded) and should read as N/A, not $0 - those mean very
  // different things to someone reading their ad performance.
  const money = (value: number | null | undefined) => (!value ? 'N/A' : formatCurrency(value));

  const metrics = [
    {
      title: "Total Spend",
      value: money(overall_metrics.total_spend),
      icon: DollarSign,
      color: "text-green-500",
      bg: "bg-green-500/10"
    },
    {
      title: "Total Revenue",
      value: money(overall_metrics.total_revenue),
      icon: TrendingUp,
      color: "text-blue-500",
      bg: "bg-blue-500/10"
    },
    {
      title: "ROAS",
      value: overall_metrics.roas == null ? 'N/A' : `${overall_metrics.roas.toFixed(2)}x`,
      icon: Target,
      color: "text-purple-500",
      bg: "bg-purple-500/10"
    },
    {
      title: "Impressions",
      value: formatNumber(overall_metrics.total_impressions ?? 0),
      icon: Eye,
      color: "text-yellow-500",
      bg: "bg-yellow-500/10"
    }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric, i) => (
        <motion.div
          key={metric.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <Card>
            <CardContent className="p-6 flex items-center space-x-4">
              <div className={cn("p-3 rounded-full", metric.bg)}>
                <metric.icon className={cn("h-6 w-6", metric.color)} />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">{metric.title}</p>
                <h3 className="text-2xl font-bold">{metric.value}</h3>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
