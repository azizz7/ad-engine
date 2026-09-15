import { Button } from '@/components/ui/button';
import { Facebook, Chrome } from 'lucide-react';
import { cn } from '@/lib/utils';

interface IntegrationButtonsProps {
  isDemoMode: boolean;
  onToggleDemoMode: () => void;
  onConnect: (platform: 'facebook' | 'google') => void;
  isFacebookConnected: boolean;
  isGoogleConnected: boolean;
  loading: boolean;
  /** Compact = icon-forward, used inside the header menu. Default = used in the empty state. */
  compact?: boolean;
}

export default function IntegrationButtons({
  isDemoMode,
  onToggleDemoMode,
  onConnect,
  isFacebookConnected,
  isGoogleConnected,
  loading,
  compact = false,
}: IntegrationButtonsProps) {
  return (
    <div className={cn('flex flex-col gap-3', compact ? 'items-stretch' : 'items-center')}>
      <div className={cn('flex gap-2', compact ? 'flex-col' : 'flex-row')}>
        <Button
          variant={isFacebookConnected ? 'secondary' : 'outline'}
          size="sm"
          className="gap-2 justify-start"
          onClick={() => onConnect('facebook')}
          disabled={loading}
        >
          <Facebook className="h-4 w-4 text-blue-600" />
          {isFacebookConnected ? 'Facebook connected' : 'Connect Facebook'}
        </Button>
        <Button
          variant={isGoogleConnected ? 'secondary' : 'outline'}
          size="sm"
          className="gap-2 justify-start"
          onClick={() => onConnect('google')}
          disabled={loading}
        >
          <Chrome className="h-4 w-4 text-red-500" />
          {isGoogleConnected ? 'Google connected' : 'Connect Google'}
        </Button>
      </div>

      <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
        <button
          onClick={onToggleDemoMode}
          role="switch"
          aria-checked={isDemoMode}
          aria-label="Use simulated demo data for connections"
          className={cn(
            'relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1',
            isDemoMode ? 'bg-primary' : 'bg-input'
          )}
        >
          <span
            className={cn(
              'inline-block h-2.5 w-2.5 transform rounded-full bg-white transition-transform',
              isDemoMode ? 'translate-x-3.5' : 'translate-x-0.5'
            )}
          />
        </button>
        Use simulated demo data
      </label>
    </div>
  );
}
