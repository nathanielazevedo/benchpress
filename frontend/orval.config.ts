import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: {
      // Backend must be running: docker compose up
      target: 'http://localhost:8000/openapi.json',
    },
    output: {
      // One file per router tag: src/api/designs/, src/api/auth/, src/api/ai/
      mode: 'tags-split',
      target: 'src/api',
      client: 'react-query',
      override: {
        // Use our axios instance so auth headers + proxy are applied automatically
        mutator: {
          path: './src/core/api.ts',
          name: 'apiClient',
        },
      },
    },
  },
})
