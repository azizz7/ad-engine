import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb, AlertTriangle, TrendingUp, Wallet } from 'lucide-react';
import { cn } from '@/lib/utils';

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

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          AI Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
        {data.insights.map((insight: string, i: number) => (
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
