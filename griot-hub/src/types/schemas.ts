// Zod Schemas for validation
import { z } from 'zod'

// Connection schemas
export const connectionConfigSchema = z.object({
  host: z.string().optional(),
  port: z.number().optional(),
  database: z.string().optional(),
  schema: z.string().optional(),
  account: z.string().optional(),
  warehouse: z.string().optional(),
  projectId: z.string().optional(),
  dataset: z.string().optional(),
  workspace: z.string().optional(),
  cluster: z.string().optional(),
})

export const createConnectionSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name is too long'),
  type: z.enum(['snowflake', 'bigquery', 'databricks', 'postgres', 'redshift']),
  config: connectionConfigSchema,
})

// Asset schemas
export const assetSlaSchema = z.object({
  freshnessHours: z.number().min(1).max(720),
  availabilityPercent: z.number().min(90).max(100),
})

export const createAssetSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  description: z.string().min(20, 'Description must be at least 20 characters'),
  domain: z.string().min(1, 'Domain is required'),
  connectionId: z.string().min(1, 'Connection is required'),
  ownerTeamId: z.string().min(1, 'Owner team is required'),
  tags: z.array(z.string()).default([]),
  tables: z.array(z.object({
    id: z.string(),
    name: z.string(),
    schema: z.string(),
    columns: z.array(z.object({
      name: z.string(),
      type: z.string(),
      nullable: z.boolean(),
    })),
  })),
  sla: assetSlaSchema,
})

// Contract schemas
export const contractFieldSchema = z.object({
  name: z.string().min(1, 'Field name is required'),
  logicalType: z.string().min(1, 'Logical type is required'),
  physicalType: z.string().optional(),
  description: z.string().optional(),
  required: z.boolean().default(false),
  unique: z.boolean().default(false),
  primaryKey: z.boolean().default(false),
  piiClassification: z.string().optional(),
  businessName: z.string().optional(),
  example: z.string().optional(),
})

export const contractTableSchema = z.object({
  name: z.string().min(1, 'Table name is required'),
  physicalName: z.string().optional(),
  description: z.string().optional(),
  fields: z.array(contractFieldSchema),
})

export const qualityRuleSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Rule name is required'),
  type: z.enum(['completeness', 'uniqueness', 'validity', 'custom']),
  field: z.string().optional(),
  table: z.string().optional(),
  expression: z.string().optional(),
  threshold: z.number().optional(),
  enabled: z.boolean().default(true),
})

export const contractSlaSchema = z.object({
  freshnessHours: z.number().min(1).max(720),
  availabilityPercent: z.number().min(90).max(100),
  responseTimeMs: z.number().optional(),
})

export const createContractSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  version: z.string().regex(/^\d+\.\d+(\.\d+)?$/, 'Version must be in format X.Y or X.Y.Z'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  domain: z.string().min(1, 'Domain is required'),
  assetId: z.string().optional(),
  ownerTeamId: z.string().min(1, 'Owner team is required'),
  tags: z.array(z.string()).default([]),
  schema: z.object({
    tables: z.array(contractTableSchema),
  }),
  qualityRules: z.array(qualityRuleSchema).default([]),
  sla: contractSlaSchema,
})

// Issue schemas
export const updateIssueSchema = z.object({
  status: z.enum(['open', 'in_progress', 'resolved', 'ignored']).optional(),
  assignedTeamId: z.string().optional(),
})

// Search/filter schemas
export const listQuerySchema = z.object({
  page: z.number().min(1).default(1),
  pageSize: z.number().min(1).max(100).default(20),
  search: z.string().optional(),
  status: z.string().optional(),
  domain: z.string().optional(),
  ownerId: z.string().optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
})

// Type exports for form usage
export type CreateConnectionInput = z.infer<typeof createConnectionSchema>
export type CreateAssetInput = z.infer<typeof createAssetSchema>
export type CreateContractInput = z.infer<typeof createContractSchema>
export type UpdateIssueInput = z.infer<typeof updateIssueSchema>
export type ListQueryInput = z.infer<typeof listQuerySchema>
