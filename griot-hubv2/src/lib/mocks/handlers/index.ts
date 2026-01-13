import { contractHandlers } from './contracts'
import { assetHandlers } from './assets'
import { connectionHandlers } from './connections'
import { dashboardHandlers } from './dashboard'
import { issueHandlers } from './issues'

// Combine all handlers
export const handlers = [
  ...contractHandlers,
  ...assetHandlers,
  ...connectionHandlers,
  ...dashboardHandlers,
  ...issueHandlers,
]
