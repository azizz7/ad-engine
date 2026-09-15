import { Card } from '@/components/ui/card';

export default function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-pulse">
      <div className="lg:col-span-8 space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="h-24" />
          ))}
        </div>
        <Card className="h-72" />
      </div>
      <div className="lg:col-span-4 space-y-6">
        <Card className="h-96" />
      </div>
    </div>
  );
}
