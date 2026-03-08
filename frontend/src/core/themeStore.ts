import { create } from 'zustand'

type ThemeMode = 'light' | 'dark'

interface ThemeState {
  mode: ThemeMode
  toggleMode: () => void
}

export const useThemeStore = create<ThemeState>((set) => ({
  mode: (localStorage.getItem('theme') as ThemeMode) ?? 'light',
  toggleMode: () =>
    set((s) => {
      const next: ThemeMode = s.mode === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', next)
      return { mode: next }
    }),
}))
