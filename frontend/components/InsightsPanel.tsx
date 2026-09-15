import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb, AlertTriangle, TrendingUp, Wallet, Sparkles } from 'lucide-react';

interface InsightsPanelProps {
  data: any;
}

export default function InsightsPanel({ data }: InsightsPanelProps) {
  if (!data?.insights) return null;

  const getIcon = (text: string) => {
    if (text.includes('⚠️')) return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    if (text.includes('💸')) return <Wallet className="h-5 w-5 text-red-500" />;
    if (text.includes('📈')) return <TrendingUp className="h-5 w-5 text-green-500" />;
    return <Lightbulb className="h-5 w-5 text-blue-500" />;
  };

  if (data.insights.length === 0 && !data.ai_summary) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Not enough data yet to generate insights for this dataset.
          </p>
        </CardContent>
      </Card>
    );
  }

  // Insights arrive pre-sorted, most actionable first. Showing a fixed,
  // small number keeps the card a predictable size and matches "most
  // important information first" instead of asking the user to scroll a
  // list within a list.
  const visibleInsights = data.insights.slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {data.ai_summary && (
          <div className="flex gap-3 rounded-lg border border-primary/30 bg-primary/5 p-4">
            <Sparkles className="h-5 w-5 flex-shrink-0 text-primary mt-0.5" />
            <p className="text-sm leading-relaxed">{data.ai_summary}</p>
          </div>
        )}
        {visibleInsights.map((insight: string, i: number) => (
          <div
            key={i}
            className="flex gap-4 p-4 rounded-lg bg-secondary/50 border border-secondary hover:bg-secondary/70 transition-colors"
          >
            <div className="flex-shrink-0 mt-0.5">
              {getIcon(insight)}
            </div>
            <p className="text-sm leading-relaxed">{insight}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
