import { contractHandlers } from './contracts'
import { assetHandlers } from './assets'
import { connectionHandlers } from './connections'
import { dashboardHandlers } from './dashboard'
import { issueHandlers } from './issues'
import { teamHandlers } from './teams'
import { runHandlers } from './runs'
import { taskHandlers } from './tasks'
import { userHandlers } from './users'
import { notificationHandlers } from './notifications'
import { searchHandlers } from './search'
import { authHandlers } from './auth'
import { roleHandlers } from './roles'

// Combine all handlers
export const handlers = [
  ...authHandlers,
  ...contractHandlers,
  ...assetHandlers,
  ...connectionHandlers,
  ...dashboardHandlers,
  ...issueHandlers,
  ...teamHandlers,
  ...runHandlers,
  ...taskHandlers,
  ...userHandlers,
  ...notificationHandlers,
  ...searchHandlers,
  ...roleHandlers,
]
