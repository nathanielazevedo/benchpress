import { Handle, Position, NodeProps, Node } from '@xyflow/react'
import { Paper, Typography, Box } from '@mui/material'
import { useTheme } from '@mui/material/styles'
import { SystemNodeData, NodeType } from '../../../types'

const NODE_ACCENT: Record<NodeType, string> = {
  client:        '#3b82f6',
  api_gateway:   '#8b5cf6',
  load_balancer: '#6366f1',
  service:       '#22c55e',
  database:      '#f97316',
  cache:         '#ef4444',
  queue:         '#eab308',
}

const NODE_ICON: Record<NodeType, string> = {
  client:        '💻',
  api_gateway:   '🔀',
  load_balancer: '⚖️',
  service:       '⚙️',
  database:      '🗄️',
  cache:         '⚡',
  queue:         '📨',
}

type SystemNodeType = Node<SystemNodeData>

export default function SystemNode({ data, selected }: NodeProps<SystemNodeType>) {
  const theme = useTheme()
  const accent = NODE_ACCENT[data.nodeType] ?? NODE_ACCENT.service
  const icon = NODE_ICON[data.nodeType] ?? NODE_ICON.service

  return (
    <Paper
      elevation={selected ? 6 : 1}
      sx={{
        px: 1.5,
        py: 1,
        minWidth: 130,
        border: '2px solid',
        borderColor: selected ? 'primary.main' : accent,
        borderRadius: 2,
        bgcolor: 'background.paper',
        transition: 'box-shadow 0.15s, border-color 0.15s',
        outline: selected
          ? `3px solid ${theme.palette.primary.main}44`
          : 'none',
        outlineOffset: 2,
      }}
    >
      <Handle type="target" position={Position.Top} id="top" style={{ background: accent }} />
      <Handle type="target" position={Position.Left} id="left" style={{ background: accent }} />

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <span style={{ fontSize: 20, lineHeight: 1, flexShrink: 0 }}>{icon}</span>
        <Box sx={{ minWidth: 0 }}>
          <Typography
            variant="caption"
            fontWeight={600}
            sx={{ display: 'block', color: 'text.primary', lineHeight: 1.3 }}
            noWrap
          >
            {data.label}
          </Typography>
          {data.description && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', fontSize: 10, lineHeight: 1.3, mt: 0.25 }}
            >
              {data.description}
            </Typography>
          )}
        </Box>
      </Box>

      <Handle type="source" position={Position.Bottom} id="bottom" style={{ background: accent }} />
      <Handle type="source" position={Position.Right} id="right" style={{ background: accent }} />
    </Paper>
  )
}
