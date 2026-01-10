# Deployment

Options for deploying Griot Hub to production.

---

## Build for Production

```bash
# Build the application
npm run build

# The output is in .next/ directory
```

---

## Deployment Options

### Option 1: Vercel (Recommended)

Vercel is the company behind Next.js and provides the best deployment experience.

#### Setup

1. Push your code to GitHub/GitLab/Bitbucket
2. Import your repository in [Vercel](https://vercel.com)
3. Configure environment variables
4. Deploy

#### Environment Variables

In Vercel dashboard, add:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_REGISTRY_API_URL` | `https://registry.your-domain.com/api/v1` |

#### Automatic Deployments

- Push to `main` → Production deployment
- Push to feature branch → Preview deployment

#### vercel.json (Optional)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

---

### Option 2: Docker

#### Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built application
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

#### next.config.js for Docker

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};

module.exports = nextConfig;
```

#### Build and Run

```bash
# Build image
docker build -t griot-hub .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_REGISTRY_API_URL=https://registry.example.com/api/v1 \
  griot-hub
```

#### Docker Compose

```yaml
version: '3.8'

services:
  griot-hub:
    build: ./griot-hub
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_REGISTRY_API_URL=http://griot-registry:8000/api/v1
    depends_on:
      - griot-registry

  griot-registry:
    build: ./griot-registry
    ports:
      - "8000:8000"
    environment:
      - GRIOT_STORAGE_BACKEND=filesystem
      - GRIOT_STORAGE_PATH=/data
    volumes:
      - registry-data:/data

volumes:
  registry-data:
```

---

### Option 3: Static Export

For hosting on any static file server (S3, Nginx, Apache, GitHub Pages).

#### Configure Static Export

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  // Required for static export
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
```

#### Build Static Files

```bash
npm run build
```

Output will be in the `out/` directory.

#### Deploy to S3

```bash
# Install AWS CLI
aws s3 sync out/ s3://your-bucket-name --delete

# Configure CloudFront (recommended for HTTPS)
```

#### Deploy to GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci
        working-directory: griot-hub

      - name: Build
        run: npm run build
        working-directory: griot-hub
        env:
          NEXT_PUBLIC_REGISTRY_API_URL: ${{ vars.REGISTRY_API_URL }}

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: griot-hub/out
```

#### Limitations of Static Export

- No server-side rendering
- No API routes
- No image optimization
- All data fetched client-side

---

### Option 4: Node.js Server

Run Next.js as a Node.js application.

#### Production Start

```bash
npm run build
npm run start
```

#### PM2 Process Manager

```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start npm --name "griot-hub" -- start

# Save process list
pm2 save

# Auto-start on boot
pm2 startup
```

#### ecosystem.config.js

```javascript
module.exports = {
  apps: [{
    name: 'griot-hub',
    script: 'npm',
    args: 'start',
    cwd: '/path/to/griot-hub',
    env: {
      NODE_ENV: 'production',
      NEXT_PUBLIC_REGISTRY_API_URL: 'https://registry.example.com/api/v1',
    },
  }],
};
```

---

### Option 5: Kubernetes

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: griot-hub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: griot-hub
  template:
    metadata:
      labels:
        app: griot-hub
    spec:
      containers:
        - name: griot-hub
          image: your-registry/griot-hub:latest
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_REGISTRY_API_URL
              valueFrom:
                configMapKeyRef:
                  name: griot-config
                  key: registry-api-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: griot-hub
spec:
  selector:
    app: griot-hub
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP
```

#### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: griot-hub
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - hub.griot.example.com
      secretName: griot-hub-tls
  rules:
    - host: hub.griot.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: griot-hub
                port:
                  number: 80
```

---

## Environment Configuration

### Production Checklist

- [ ] Set `NEXT_PUBLIC_REGISTRY_API_URL` to production registry
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring/logging
- [ ] Configure CDN for static assets
- [ ] Set appropriate caching headers
- [ ] Enable compression (gzip/brotli)
- [ ] Configure CORS if needed

### Security Headers

Add security headers via your reverse proxy or `next.config.js`:

```javascript
// next.config.js
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin'
  }
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## Monitoring

### Health Check Endpoint

The Hub checks Registry health at `/`. For a dedicated health endpoint, add:

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ status: 'healthy' });
}
```

### Logging

In production, use structured logging:

```typescript
// Use console for Next.js
console.log(JSON.stringify({
  level: 'info',
  message: 'Page loaded',
  page: '/contracts',
  timestamp: new Date().toISOString()
}));
```

### Error Tracking

Integrate error tracking (Sentry, DataDog, etc.):

```bash
npm install @sentry/nextjs
```

```javascript
// sentry.client.config.js
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
});
```

---

## Performance Optimization

### Build Analysis

```bash
# Analyze bundle size
ANALYZE=true npm run build
```

### Caching Strategy

Configure caching in your CDN/reverse proxy:

| Path | Cache | Duration |
|------|-------|----------|
| `/_next/static/*` | Yes | 1 year (immutable) |
| `/` | No | - |
| `/api/*` | No | - |
| `/*.json` | No | - |

### Image Optimization

For static export, use optimized images or a CDN:

```bash
# Install sharp for local optimization
npm install sharp
```

---

## Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

### Runtime Errors

1. Check environment variables are set
2. Verify Registry API is accessible
3. Check browser console for errors
4. Review server logs

### Performance Issues

1. Enable production mode (`NODE_ENV=production`)
2. Use CDN for static assets
3. Enable compression
4. Review network waterfall in DevTools

---

## Next Steps

- [Getting Started](./getting-started.md) - Development setup
- [Architecture](./architecture.md) - Understanding the codebase
