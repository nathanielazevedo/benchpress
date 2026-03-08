import { describe, it, expect } from 'vitest'
import { hasRole } from '.'

describe('hasRole', () => {
  it('returns true when user meets the minimum role', () => {
    expect(hasRole('super_admin', 'member')).toBe(true)
    expect(hasRole('super_admin', 'super_admin')).toBe(true)
    expect(hasRole('company_admin', 'lab_admin')).toBe(true)
    expect(hasRole('lab_admin', 'lab_admin')).toBe(true)
    expect(hasRole('lab_admin', 'member')).toBe(true)
  })

  it('returns false when user is below the minimum role', () => {
    expect(hasRole('member', 'lab_admin')).toBe(false)
    expect(hasRole('member', 'super_admin')).toBe(false)
    expect(hasRole('lab_admin', 'company_admin')).toBe(false)
    expect(hasRole('company_admin', 'super_admin')).toBe(false)
  })
})
