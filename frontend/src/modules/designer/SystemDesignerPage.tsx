import { Box } from '@mui/material'
import DesignList from './sidebar/DesignList'
import FlowCanvas from './canvas/FlowCanvas'
import AIChat from './sidebar/AIChat'

export default function SystemDesignerPage() {
  return (
    <Box sx={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      <DesignList />
      <FlowCanvas />
      <AIChat />
    </Box>
  )
}
