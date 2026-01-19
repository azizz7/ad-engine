'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface Dataset {
  id: number
  name: string
  filename: string
  row_count: number
  date_range_start: string | null
  date_range_end: string | null
  created_at: string
}

interface DatasetSelectorProps {
  apiBase: string
  selectedDatasetId: number | null
  onDatasetSelect: (datasetId: number) => void
  onDatasetUploaded: () => void
}

export default function DatasetSelector({
  apiBase,
  selectedDatasetId,
  onDatasetSelect,
  onDatasetUploaded
}: DatasetSelectorProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDatasets = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${apiBase}/api/datasets`)
      setDatasets(response.data)
      setError(null)
      
      // Auto-select first dataset if none selected
      if (response.data.length > 0 && selectedDatasetId === null) {
        onDatasetSelect(response.data[0].id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load datasets')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDatasets()
  }, [])

  // Refresh datasets when a new one is uploaded
  useEffect(() => {
    fetchDatasets()
  }, [onDatasetUploaded])

  const handleDelete = async (datasetId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this dataset?')) {
      return
    }

    try {
      await axios.delete(`${apiBase}/api/datasets/${datasetId}`)
      await fetchDatasets()
      
      // If deleted dataset was selected, select first available
      if (selectedDatasetId === datasetId && datasets.length > 1) {
        const remaining = datasets.filter(d => d.id !== datasetId)
        if (remaining.length > 0) {
          onDatasetSelect(remaining[0].id)
        }
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete dataset')
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Datasets</h2>
        <p>Loading datasets...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h2>Datasets</h2>
        <p className="error">{error}</p>
      </div>
    )
  }

  if (datasets.length === 0) {
    return (
      <div className="card">
        <h2>Datasets</h2>
        <p style={{ color: '#666' }}>No datasets uploaded yet. Upload a CSV file to get started.</p>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Your Datasets</h2>
        <button
          onClick={fetchDatasets}
          style={{
            padding: '0.5rem 1rem',
            background: '#f0f0f0',
            border: '1px solid #ddd',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔄 Refresh
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {datasets.map((dataset) => (
          <div
            key={dataset.id}
            onClick={() => onDatasetSelect(dataset.id)}
            style={{
              padding: '1rem',
              border: selectedDatasetId === dataset.id ? '2px solid #0070f3' : '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              backgroundColor: selectedDatasetId === dataset.id ? '#f0f7ff' : 'white',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                {dataset.name}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#666' }}>
                {dataset.row_count.toLocaleString()} rows • {dataset.filename}
                {dataset.date_range_start && dataset.date_range_end && (
                  <span style={{ marginLeft: '0.5rem' }}>
                    • {new Date(dataset.date_range_start).toLocaleDateString()} - {new Date(dataset.date_range_end).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={(e) => handleDelete(dataset.id, e)}
              style={{
                padding: '0.25rem 0.5rem',
                background: '#fee',
                border: '1px solid #fcc',
                borderRadius: '4px',
                cursor: 'pointer',
                color: '#c00',
                fontSize: '0.85rem'
              }}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
