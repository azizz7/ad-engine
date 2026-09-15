'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, Check, Plus, Trash2, Database } from 'lucide-react';
import { api } from '@/lib/api';
import { useOnClickOutside } from '@/lib/hooks';
import { cn } from '@/lib/utils';
import { formatNumber } from '@/lib/format';

interface Dataset {
  id: number;
  name: string;
  row_count: number;
}

interface DatasetSwitcherProps {
  selectedDatasetId: number | null;
  onSelect: (id: number) => void;
  onUploadNew: () => void;
  onDeleted: (id: number) => void;
  /** Bump to force a re-fetch (e.g. right after a new upload). */
  refreshToken: number;
}

/**
 * Combines what used to be a separate "New Upload" button and a
 * standalone dataset-history card into a single control: one thing to
 * look at that answers "what am I viewing, and what else can I view."
 */
export default function DatasetSwitcher({
  selectedDatasetId,
  onSelect,
  onUploadNew,
  onDeleted,
  refreshToken,
}: DatasetSwitcherProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useOnClickOutside<HTMLDivElement>(() => setOpen(false));

  useEffect(() => {
    let cancelled = false;
    api
      .get('/api/datasets')
      .then((res) => {
        if (!cancelled) setDatasets(res.data);
      })
      .catch(() => {
        /* Surfaced via the dashboard's own error banner when this data is needed elsewhere. */
      });
    return () => {
      cancelled = true;
    };
  }, [refreshToken]);

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this dataset? This cannot be undone.')) return;
    try {
      await api.delete(`/api/datasets/${id}`);
      setDatasets((prev) => prev.filter((d) => d.id !== id));
      onDeleted(id);
    } catch {
      // A failed delete just leaves the dataset in the list - no separate error UI needed here.
    }
  };

  const current = datasets.find((d) => d.id === selectedDatasetId);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-lg border border-border/50 bg-secondary/40 px-3 py-2 text-sm font-medium hover:bg-secondary/70 transition-colors max-w-xs"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <Database className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
        <span className="truncate">{current?.name ?? 'Select dataset'}</span>
        <ChevronDown className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
      </button>

      {open && (
        <div className="absolute left-0 z-20 mt-2 w-80 rounded-lg border border-border bg-popover shadow-lg overflow-hidden">
          <div className="max-h-72 overflow-y-auto py-1">
            {datasets.length === 0 && (
              <p className="px-3 py-3 text-sm text-muted-foreground">No datasets yet.</p>
            )}
            {datasets.map((d) => (
              <div
                key={d.id}
                onClick={() => {
                  onSelect(d.id);
                  setOpen(false);
                }}
                className={cn(
                  'flex items-center justify-between gap-2 px-3 py-2 text-sm cursor-pointer hover:bg-accent',
                  d.id === selectedDatasetId && 'bg-accent/60'
                )}
              >
                <div className="flex min-w-0 items-center gap-2">
                  {d.id === selectedDatasetId ? (
                    <Check className="h-4 w-4 flex-shrink-0 text-primary" />
                  ) : (
                    <span className="w-4" />
                  )}
                  <div className="min-w-0">
                    <p className="truncate font-medium">{d.name}</p>
                    <p className="text-xs text-muted-foreground">{formatNumber(d.row_count)} rows</p>
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(d.id, e)}
                  aria-label={`Delete ${d.name}`}
                  className="flex-shrink-0 text-muted-foreground hover:text-destructive p-1"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={() => {
              onUploadNew();
              setOpen(false);
            }}
            className="flex w-full items-center gap-2 border-t border-border px-3 py-2.5 text-sm font-medium text-primary hover:bg-accent"
          >
            <Plus className="h-4 w-4" />
            Upload new dataset
          </button>
        </div>
      )}
    </div>
  );
}
