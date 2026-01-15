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

// Combine all handlers
export const handlers = [
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
]
