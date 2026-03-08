// ── Auth / User ───────────────────────────────────────────────────────────────

export type UserRole = 'super_admin' | 'company_admin' | 'lab_admin' | 'member'

export interface CompanyInfo {
  id: string
  name: string
}

export interface LabInfo {
  id: string
  name: string
  company: CompanyInfo
}

export interface UserProfile {
  id: string
  username: string
  role: UserRole
  lab: LabInfo | null
}

// ── Canvas ────────────────────────────────────────────────────────────────────

export type NodeType =
  | 'client'
  | 'api_gateway'
  | 'load_balancer'
  | 'service'
  | 'database'
  | 'cache'
  | 'queue'

export interface SystemNodeData extends Record<string, unknown> {
  label: string
  nodeType: NodeType
  description?: string
}

// ── Designs ───────────────────────────────────────────────────────────────────

export interface DesignSummary {
  id: string
  name: string
  description?: string | null
  lab_id: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface Design extends DesignSummary {
  nodes: unknown[]
  edges: unknown[]
}

// ── AI ────────────────────────────────────────────────────────────────────────

export interface AIAction {
  type: 'add_node' | 'remove_node' | 'add_edge' | 'remove_edge' | 'update_node'
  node?: Record<string, unknown>
  edge?: Record<string, unknown>
  id?: string
  data?: Partial<SystemNodeData>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// ── Role helpers ──────────────────────────────────────────────────────────────

const ROLE_RANK: Record<UserRole, number> = {
  member: 0,
  lab_admin: 1,
  company_admin: 2,
  super_admin: 3,
}

export const hasRole = (userRole: UserRole, minRole: UserRole): boolean =>
  ROLE_RANK[userRole] >= ROLE_RANK[minRole]
