import { useState } from 'react'
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, CircularProgress, Tooltip, Drawer, IconButton,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import DownloadIcon from '@mui/icons-material/Download'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'

import { useListInstruments } from '../../api/instruments/instruments'
import { useListLabs } from '../../api/labs/labs'
import { useListInstrumentFiles, downloadInstrumentFile } from '../../api/instruments/files'
import type { InstrumentOut } from '../../api/benchpressAPI.schemas'

const STATUS_COLOR: Record<string, 'success' | 'default'> = {
  online: 'success',
  offline: 'default',
}

function formatBytes(bytes: number | null) {
  if (bytes == null) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function FilesDrawer({
  instrument,
  onClose,
}: {
  instrument: InstrumentOut | null
  onClose: () => void
}) {
  const { data: files, isLoading } = useListInstrumentFiles(
    instrument?.instrument_id ?? null
  )

  return (
    <Drawer
      anchor="right"
      open={!!instrument}
      onClose={onClose}
      PaperProps={{ sx: { width: 560 } }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', px: 2.5, py: 2, borderBottom: 1, borderColor: 'divider' }}>
        <FolderOpenIcon sx={{ mr: 1.5, color: 'text.secondary' }} />
        <Box sx={{ flex: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {instrument?.name}
          </Typography>
          <Typography variant="caption" fontFamily="monospace" color="text.secondary">
            {instrument?.instrument_id}
          </Typography>
        </Box>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </Box>

      <Box sx={{ p: 2.5, overflow: 'auto', flex: 1 }}>
        {isLoading ? (
          <CircularProgress size={24} />
        ) : !files?.length ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" mt={4}>
            No files uploaded yet.
          </Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Filename</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Uploaded</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Size</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                <TableCell width={40} />
              </TableRow>
            </TableHead>
            <TableBody>
              {files.map((f) => (
                <TableRow key={f.object_key} hover>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace" fontSize={12}>
                      {f.filename}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {f.uploaded_at ? new Date(f.uploaded_at).toLocaleString() : '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">{formatBytes(f.size_bytes)}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={f.content_type.split('/')[1] ?? f.content_type} size="small" variant="outlined" sx={{ fontSize: 10 }} />
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Download">
                      <IconButton
                        size="small"
                        onClick={() => downloadInstrumentFile(f.instrument_id, f.object_key, f.filename)}
                      >
                        <DownloadIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Box>
    </Drawer>
  )
}

export default function InstrumentsPage() {
  const [selected, setSelected] = useState<InstrumentOut | null>(null)

  const { data: instrumentsPage, isLoading } = useListInstruments()
  const instruments = instrumentsPage?.items ?? []
  const { data: labsPage } = useListLabs()
  const labs = labsPage?.items ?? []

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" fontWeight={600} mb={3}>
        Instruments
      </Typography>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <TableContainer component={Paper} elevation={1}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Instrument ID</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Lab</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Last Seen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {instruments.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6}>
                    <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                      No instruments registered yet.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
              {instruments.map((inst) => {
                const lab = labs.find((l) => l.id === inst.lab_id)
                return (
                  <TableRow
                    key={inst.id as string}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => setSelected(inst)}
                  >
                    <TableCell>{inst.name}</TableCell>
                    <TableCell>
                      <Tooltip title="Click to copy">
                        <Typography
                          variant="caption"
                          fontFamily="monospace"
                          sx={{ cursor: 'pointer', color: 'text.secondary' }}
                          onClick={(e) => {
                            e.stopPropagation()
                            navigator.clipboard.writeText(inst.id as string)
                          }}
                        >
                          {inst.id as string}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace">
                        {inst.instrument_id}
                      </Typography>
                    </TableCell>
                    <TableCell>{lab?.name ?? '—'}</TableCell>
                    <TableCell>
                      <Chip
                        label={inst.status}
                        size="small"
                        color={STATUS_COLOR[inst.status] ?? 'default'}
                        variant="outlined"
                        sx={{ fontSize: 11 }}
                      />
                    </TableCell>
                    <TableCell>{new Date(inst.last_seen_at).toLocaleString()}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <FilesDrawer instrument={selected} onClose={() => setSelected(null)} />
    </Box>
  )
}
