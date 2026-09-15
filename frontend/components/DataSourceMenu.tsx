'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import IntegrationButtons from '@/components/IntegrationButtons';
import { useOnClickOutside } from '@/lib/hooks';

interface DataSourceMenuProps {
  isDemoMode: boolean;
  onToggleDemoMode: () => void;
  onConnect: (platform: 'facebook' | 'google') => void;
  isFacebookConnected: boolean;
  isGoogleConnected: boolean;
  loading: boolean;
}

/**
 * Tucks the secondary "connect a platform" actions behind one button
 * instead of leaving 2-3 buttons and a toggle permanently visible in the
 * header - most sessions are about reading an already-loaded dataset, not
 * connecting a new source.
 */
export default function DataSourceMenu(props: DataSourceMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useOnClickOutside<HTMLDivElement>(() => setOpen(false));

  return (
    <div className="relative" ref={ref}>
      <Button variant="outline" size="sm" className="gap-2" onClick={() => setOpen((v) => !v)}>
        <Plus className="h-4 w-4" />
        Add data
      </Button>

      {open && (
        <div className="absolute right-0 z-20 mt-2 w-64 rounded-lg border border-border bg-popover p-4 shadow-lg">
          <p className="mb-3 text-xs font-medium text-muted-foreground">Connect an ad platform</p>
          <IntegrationButtons {...props} compact />
        </div>
      )}
    </div>
  );
}
