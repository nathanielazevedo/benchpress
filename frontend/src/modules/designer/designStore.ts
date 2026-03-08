import { create } from 'zustand'
import { Node, Edge } from '@xyflow/react'
import { AIAction, SystemNodeData } from '../../types'

// Server state (designs list, CRUD) is handled by React Query generated hooks.
// This store owns only local canvas state and active design tracking.
interface DesignState {
  activeDesignId: string | null
  setActiveDesignId: (id: string | null) => void
  nodes: Node<SystemNodeData>[]
  edges: Edge[]
  setNodes: (nodes: Node<SystemNodeData>[]) => void
  setEdges: (edges: Edge[]) => void
  applyAIActions: (actions: AIAction[]) => void
}

export const useDesignStore = create<DesignState>((set) => ({
  activeDesignId: null,
  setActiveDesignId: (id) => set({ activeDesignId: id }),
  nodes: [],
  edges: [],
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  applyAIActions: (actions) => {
    set((s) => {
      let nodes = [...s.nodes]
      let edges = [...s.edges]

      for (const action of actions) {
        if (action.type === 'add_node' && action.node) {
          nodes = [...nodes, action.node as unknown as Node<SystemNodeData>]
        } else if (action.type === 'remove_node' && action.id) {
          nodes = nodes.filter((n) => n.id !== action.id)
          edges = edges.filter((e) => e.source !== action.id && e.target !== action.id)
        } else if (action.type === 'add_edge' && action.edge) {
          edges = [...edges, action.edge as unknown as Edge]
        } else if (action.type === 'remove_edge' && action.id) {
          edges = edges.filter((e) => e.id !== action.id)
        } else if (action.type === 'update_node' && action.id && action.data) {
          nodes = nodes.map((n) =>
            n.id === action.id ? { ...n, data: { ...n.data, ...action.data } } : n
          )
        }
      }

      return { nodes, edges }
    })
  },
}))
