import { useState, useCallback } from 'react'
import {
  Box, Typography, Paper, MenuItem, TextField, CircularProgress,
  Divider, Alert, Chip,
} from '@mui/material'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Label,
} from 'recharts'
import Papa from 'papaparse'
import * as XLSX from 'xlsx'

import { useListInstruments } from '../../api/instruments/instruments'
import { useListInstrumentFiles, fetchInstrumentFileBuffer } from '../../api/instruments/files'

type Row = Record<string, unknown>

const PARSEABLE = ['.csv', '.xlsx', '.xls']

function isParseable(filename: string) {
  return PARSEABLE.some((ext) => filename.toLowerCase().endsWith(ext))
}

async function parseFile(instrumentId: string, objectKey: string, filename: string): Promise<Row[]> {
  const buf = await fetchInstrumentFileBuffer(instrumentId, objectKey)

  if (filename.toLowerCase().endsWith('.csv')) {
    const text = new TextDecoder().decode(buf)
    const result = Papa.parse<Row>(text, { header: true, skipEmptyLines: true, dynamicTyping: true })
    return result.data
  }

  // XLSX / XLS
  const wb = XLSX.read(buf, { type: 'array' })
  const ws = wb.Sheets[wb.SheetNames[0]]
  return XLSX.utils.sheet_to_json<Row>(ws, { defval: null })
}

function toNumber(val: unknown): number | null {
  const n = Number(val)
  return isNaN(n) ? null : n
}

// ── Side panel ────────────────────────────────────────────────────────────────

function SidePanel({
  instrumentId, setInstrumentId,
  objectKey, setObjectKey,
  xCol, setXCol,
  yCol, setYCol,
  columns,
  loading,
  error,
}: {
  instrumentId: string; setInstrumentId: (v: string) => void
  objectKey: string;   setObjectKey:   (v: string) => void
  xCol: string;        setXCol:        (v: string) => void
  yCol: string;        setYCol:        (v: string) => void
  columns: string[]
  loading: boolean
  error: string | null
}) {
  const { data: instrumentsPage } = useListInstruments()
  const instruments = instrumentsPage?.items ?? []

  const { data: files } = useListInstrumentFiles(instrumentId || null)
  const parseableFiles = (files ?? []).filter((f) => isParseable(f.filename))

  return (
    <Box
      sx={{
        width: 260,
        flexShrink: 0,
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        gap: 0,
        overflow: 'auto',
      }}
    >
      {/* Data Source */}
      <Box sx={{ p: 2.5 }}>
        <Typography variant="overline" sx={{ fontSize: 10, color: 'text.disabled', letterSpacing: 1.5 }}>
          Data Source
        </Typography>

        <TextField
          select
          label="Instrument"
          value={instrumentId}
          onChange={(e) => { setInstrumentId(e.target.value); setObjectKey('') }}
          fullWidth
          size="small"
          sx={{ mt: 1.5 }}
        >
          {instruments.map((inst) => (
            <MenuItem key={inst.instrument_id} value={inst.instrument_id}>
              {inst.name}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          label="File"
          value={objectKey}
          onChange={(e) => setObjectKey(e.target.value)}
          fullWidth
          size="small"
          sx={{ mt: 1.5 }}
          disabled={!instrumentId}
        >
          {parseableFiles.length === 0 && instrumentId ? (
            <MenuItem disabled value="">No CSV/XLSX files</MenuItem>
          ) : (
            parseableFiles.map((f) => (
              <MenuItem key={f.object_key} value={f.object_key}>
                {f.filename}
              </MenuItem>
            ))
          )}
        </TextField>

        {loading && <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={14} />
          <Typography variant="caption" color="text.secondary">Parsing file…</Typography>
        </Box>}

        {error && <Alert severity="error" sx={{ mt: 1.5, fontSize: 12 }}>{error}</Alert>}
      </Box>

      {columns.length > 0 && (
        <>
          <Divider />
          <Box sx={{ p: 2.5 }}>
            <Typography variant="overline" sx={{ fontSize: 10, color: 'text.disabled', letterSpacing: 1.5 }}>
              Axes
            </Typography>

            <TextField
              select
              label="X Axis"
              value={xCol}
              onChange={(e) => setXCol(e.target.value)}
              fullWidth
              size="small"
              sx={{ mt: 1.5 }}
            >
              {columns.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>

            <TextField
              select
              label="Y Axis"
              value={yCol}
              onChange={(e) => setYCol(e.target.value)}
              fullWidth
              size="small"
              sx={{ mt: 1.5 }}
            >
              {columns.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Box>

          <Divider />
          <Box sx={{ p: 2.5 }}>
            <Typography variant="overline" sx={{ fontSize: 10, color: 'text.disabled', letterSpacing: 1.5 }}>
              Chart Type
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip label="Scatter" size="small" color="primary" variant="filled" />
            </Box>
          </Box>
        </>
      )}
    </Box>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function VisualizePage() {
  const [instrumentId, setInstrumentId] = useState('')
  const [objectKey, setObjectKey]       = useState('')
  const [rows, setRows]                 = useState<Row[]>([])
  const [columns, setColumns]           = useState<string[]>([])
  const [xCol, setXCol]                 = useState('')
  const [yCol, setYCol]                 = useState('')
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState<string | null>(null)

  // Whenever a file is selected, fetch + parse it
  const handleFileSelect = useCallback(async (instId: string, key: string) => {
    if (!key) return
    const filename = key.split('/').pop() ?? key
    setLoading(true)
    setError(null)
    setRows([])
    setColumns([])
    setXCol('')
    setYCol('')
    try {
      const data = await parseFile(instId, key, filename)
      if (data.length === 0) throw new Error('File is empty or could not be parsed.')
      const cols = Object.keys(data[0])
      setRows(data)
      setColumns(cols)
      setXCol(cols[0] ?? '')
      setYCol(cols[1] ?? '')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load file.')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSetObjectKey = useCallback((key: string) => {
    setObjectKey(key)
    if (key) handleFileSelect(instrumentId, key)
  }, [instrumentId, handleFileSelect])

  const handleSetInstrumentId = useCallback((id: string) => {
    setInstrumentId(id)
    setObjectKey('')
    setRows([])
    setColumns([])
    setXCol('')
    setYCol('')
    setError(null)
  }, [])

  // Build scatter data — only rows where both columns are numeric
  const chartData = (xCol && yCol && rows.length > 0)
    ? rows.flatMap((r) => {
        const x = toNumber(r[xCol])
        const y = toNumber(r[yCol])
        return x !== null && y !== null ? [{ x, y }] : []
      })
    : []

  const pointCount = chartData.length

  return (
    <Box sx={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      <SidePanel
        instrumentId={instrumentId}
        setInstrumentId={handleSetInstrumentId}
        objectKey={objectKey}
        setObjectKey={handleSetObjectKey}
        xCol={xCol}
        setXCol={setXCol}
        yCol={yCol}
        setYCol={setYCol}
        columns={columns}
        loading={loading}
        error={error}
      />

      {/* Chart area */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 3, overflow: 'hidden' }}>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 2, mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>Visualize</Typography>
          {pointCount > 0 && (
            <Typography variant="caption" color="text.secondary">
              {pointCount.toLocaleString()} points
            </Typography>
          )}
        </Box>

        {!objectKey && (
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.disabled" variant="body2">
              Select an instrument and file to begin.
            </Typography>
          </Box>
        )}

        {objectKey && !loading && xCol && yCol && chartData.length > 0 && (
          <Paper elevation={1} sx={{ flex: 1, p: 3, overflow: 'hidden' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 30, bottom: 30, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.15)" />
                <XAxis type="number" dataKey="x" name={xCol} tick={{ fontSize: 11 }}>
                  <Label value={xCol} position="insideBottom" offset={-15} fontSize={12} />
                </XAxis>
                <YAxis type="number" dataKey="y" name={yCol} tick={{ fontSize: 11 }}>
                  <Label value={yCol} angle={-90} position="insideLeft" offset={15} fontSize={12} />
                </YAxis>
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(val, name) => [val, name === 'x' ? xCol : yCol]}
                />
                <Scatter data={chartData} fill="#1976d2" opacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </Paper>
        )}

        {objectKey && !loading && xCol && yCol && chartData.length === 0 && !error && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            No numeric data found for columns "{xCol}" and "{yCol}".
          </Alert>
        )}
      </Box>
    </Box>
  )
}
