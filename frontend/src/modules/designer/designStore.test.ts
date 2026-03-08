import { describe, it, expect, beforeEach } from 'vitest'
import { useDesignStore } from './designStore'
import type { Node, Edge } from '@xyflow/react'
import type { SystemNodeData } from '../../types'

const makeNode = (id: string): Node<SystemNodeData> => ({
  id,
  type: 'systemNode',
  position: { x: 0, y: 0 },
  data: { label: id, nodeType: 'service' },
})

const makeEdge = (id: string, source: string, target: string): Edge => ({
  id,
  source,
  target,
})

beforeEach(() => {
  useDesignStore.setState({ nodes: [], edges: [], activeDesignId: null })
})

describe('applyAIActions', () => {
  it('add_node appends a node to the canvas', () => {
    useDesignStore.getState().applyAIActions([
      { type: 'add_node', node: makeNode('n1') as unknown as Record<string, unknown> },
    ])
    const { nodes } = useDesignStore.getState()
    expect(nodes).toHaveLength(1)
    expect(nodes[0].id).toBe('n1')
  })

  it('remove_node removes the node and its connected edges', () => {
    useDesignStore.setState({
      nodes: [makeNode('n1'), makeNode('n2')],
      edges: [makeEdge('e1', 'n1', 'n2'), makeEdge('e2', 'n2', 'n1')],
    })
    useDesignStore.getState().applyAIActions([{ type: 'remove_node', id: 'n1' }])
    const { nodes, edges } = useDesignStore.getState()
    expect(nodes).toHaveLength(1)
    expect(nodes[0].id).toBe('n2')
    expect(edges).toHaveLength(0)
  })

  it('add_edge appends an edge', () => {
    useDesignStore.setState({ nodes: [makeNode('n1'), makeNode('n2')], edges: [] })
    useDesignStore.getState().applyAIActions([
      { type: 'add_edge', edge: makeEdge('e1', 'n1', 'n2') as unknown as Record<string, unknown> },
    ])
    expect(useDesignStore.getState().edges).toHaveLength(1)
    expect(useDesignStore.getState().edges[0].id).toBe('e1')
  })

  it('remove_edge removes only that edge', () => {
    useDesignStore.setState({
      nodes: [makeNode('n1'), makeNode('n2'), makeNode('n3')],
      edges: [makeEdge('e1', 'n1', 'n2'), makeEdge('e2', 'n2', 'n3')],
    })
    useDesignStore.getState().applyAIActions([{ type: 'remove_edge', id: 'e1' }])
    const { edges } = useDesignStore.getState()
    expect(edges).toHaveLength(1)
    expect(edges[0].id).toBe('e2')
  })

  it('update_node merges data into the target node', () => {
    useDesignStore.setState({ nodes: [makeNode('n1')], edges: [] })
    useDesignStore.getState().applyAIActions([
      { type: 'update_node', id: 'n1', data: { label: 'Updated', description: 'new desc' } },
    ])
    const node = useDesignStore.getState().nodes[0]
    expect(node.data.label).toBe('Updated')
    expect(node.data.description).toBe('new desc')
    expect(node.data.nodeType).toBe('service') // unchanged field preserved
  })

  it('unknown action type is a no-op', () => {
    useDesignStore.setState({ nodes: [makeNode('n1')], edges: [] })
    useDesignStore.getState().applyAIActions([{ type: 'noop' as never }])
    expect(useDesignStore.getState().nodes).toHaveLength(1)
  })
})
