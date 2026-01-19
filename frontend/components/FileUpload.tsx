import { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onUploadSuccess: (datasetId: number) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess(response.data.dataset_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <Card className={cn(
      "relative border-2 border-dashed transition-all duration-200",
      isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25",
      "hover:border-primary/50"
    )}>
      <CardContent
        className="flex flex-col items-center justify-center py-10 px-4 text-center cursor-pointer"
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".csv"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        <div className="mb-4 rounded-full bg-secondary p-4">
          {uploading ? (
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          ) : error ? (
            <AlertCircle className="h-8 w-8 text-destructive" />
          ) : (
            <Upload className="h-8 w-8 text-primary" />
          )}
        </div>

        <h3 className="text-lg font-semibold">
          {uploading ? 'Uploading...' : 'Upload Ad Data'}
        </h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-xs">
          Drag and drop your CSV file here, or click to select a file.
        </p>

        {error && (
          <p className="mt-4 text-sm font-medium text-destructive">{error}</p>
        )}
      </CardContent>
    </Card>
  );
}
