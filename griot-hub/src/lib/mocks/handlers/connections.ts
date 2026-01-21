import { http, HttpResponse, delay } from 'msw'
import { mockConnections } from '../data/mock-data'

export const connectionHandlers = [
  // List connections
  http.get('/api/connections', async () => {
    await delay(200)
    return HttpResponse.json(mockConnections)
  }),

  // Get single connection
  http.get('/api/connections/:id', async ({ params }) => {
    await delay(150)

    const connection = mockConnections.find((c) => c.id === params.id)
    if (!connection) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(connection)
  }),

  // Test connection
  http.post('/api/connections/:id/test', async ({ params }) => {
    await delay(2000) // Simulate connection test

    const connection = mockConnections.find((c) => c.id === params.id)
    if (!connection) {
      return new HttpResponse(null, { status: 404 })
    }

    // Randomly succeed or fail for demo
    const success = Math.random() > 0.2

    if (success) {
      return HttpResponse.json({
        success: true,
        message: 'Connection successful',
        latencyMs: Math.floor(Math.random() * 500) + 100,
      })
    }

    return HttpResponse.json(
      {
        success: false,
        message: 'Connection failed: Unable to authenticate',
        code: 'AUTH_ERROR',
      },
      { status: 400 }
    )
  }),

  // Browse connection (get database structure)
  http.get('/api/connections/:id/browse', async ({ params }) => {
    await delay(500)

    const connection = mockConnections.find((c) => c.id === params.id)
    if (!connection) {
      return new HttpResponse(null, { status: 404 })
    }

    // Mock database structure
    return HttpResponse.json({
      schemas: [
        {
          name: 'CUSTOMER',
          tables: [
            {
              name: 'customers',
              columns: [
                { name: 'customer_id', type: 'VARCHAR', nullable: false },
                { name: 'email', type: 'VARCHAR', nullable: false },
                { name: 'first_name', type: 'VARCHAR', nullable: true },
                { name: 'last_name', type: 'VARCHAR', nullable: true },
                { name: 'created_at', type: 'TIMESTAMP', nullable: false },
              ],
              rowCount: 1234567,
            },
            {
              name: 'addresses',
              columns: [
                { name: 'address_id', type: 'VARCHAR', nullable: false },
                { name: 'customer_id', type: 'VARCHAR', nullable: false },
                { name: 'street', type: 'VARCHAR', nullable: true },
                { name: 'city', type: 'VARCHAR', nullable: true },
                { name: 'country', type: 'VARCHAR', nullable: true },
              ],
              rowCount: 2456789,
            },
          ],
        },
        {
          name: 'FINANCE',
          tables: [
            {
              name: 'transactions',
              columns: [
                { name: 'transaction_id', type: 'VARCHAR', nullable: false },
                { name: 'amount', type: 'DECIMAL', nullable: false },
                { name: 'currency', type: 'VARCHAR', nullable: false },
                { name: 'timestamp', type: 'TIMESTAMP', nullable: false },
              ],
              rowCount: 50000000,
            },
          ],
        },
      ],
    })
  }),

  // Create connection
  http.post('/api/connections', async ({ request }) => {
    await delay(500)

    const body = (await request.json()) as Record<string, unknown>
    const newConnection = {
      id: `conn-${Date.now()}`,
      ...body,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    return HttpResponse.json(newConnection, { status: 201 })
  }),
]
