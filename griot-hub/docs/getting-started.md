# Getting Started

This guide covers installation, configuration, and running Griot Hub locally.

---

## Prerequisites

- **Node.js** 18.x or later
- **npm** 9.x or later (or yarn/pnpm)
- **griot-registry** running locally or accessible via network

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/griot.git
cd griot/griot-hub
```

### 2. Install Dependencies

```bash
npm install
```

Or with yarn:
```bash
yarn install
```

Or with pnpm:
```bash
pnpm install
```

### 3. Configure Environment

Create a `.env.local` file in the `griot-hub` directory:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Registry API URL
NEXT_PUBLIC_REGISTRY_API_URL=http://localhost:8000/api/v1

# Optional: Enable debug mode
NEXT_PUBLIC_DEBUG=false
```

#### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_REGISTRY_API_URL` | Yes | `/api/v1` | Base URL for the Registry API |
| `NEXT_PUBLIC_DEBUG` | No | `false` | Enable debug logging |

---

## Running the Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### Development Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |

---

## Project Structure

```
griot-hub/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── globals.css         # Global styles
│   │   └── [routes]/           # Route directories
│   ├── components/             # React components
│   └── lib/                    # Utilities
│       ├── api.ts              # API client
│       └── types.ts            # TypeScript types
├── public/                     # Static files
├── docs/                       # Documentation
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── .env.local                  # Local environment (not committed)
```

---

## Connecting to the Registry

Griot Hub requires a running instance of `griot-registry` to function.

### Option 1: Local Registry

Start the registry locally:

```bash
cd ../griot-registry
pip install -e .
griot-registry serve --port 8000
```

Then set in `.env.local`:
```env
NEXT_PUBLIC_REGISTRY_API_URL=http://localhost:8000/api/v1
```

### Option 2: Remote Registry

Point to a deployed registry:
```env
NEXT_PUBLIC_REGISTRY_API_URL=https://registry.your-domain.com/api/v1
```

### Option 3: Mock Mode (Development)

For development without a registry, you can use mock data by creating API route handlers in `src/app/api/`.

---

## Verifying Installation

1. Start the development server: `npm run dev`
2. Open [http://localhost:3000](http://localhost:3000)
3. You should see the Griot Hub dashboard
4. Check the health indicator in the top navigation

If the registry is not available, you'll see warning messages but the UI will still load.

---

## IDE Setup

### VS Code (Recommended)

Install these extensions:
- **ESLint** - Linting
- **Prettier** - Code formatting
- **Tailwind CSS IntelliSense** - Tailwind autocomplete
- **TypeScript Vue Plugin (Volar)** - Enhanced TypeScript support

Recommended settings (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.experimental.classRegex": [
    ["className\\s*=\\s*[\"']([^\"']*)[\"']", "([^\"']*)"]
  ]
}
```

---

## Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
# Use a different port
npm run dev -- --port 3001
```

**TypeScript errors after install:**
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

**API connection failed:**
- Verify `NEXT_PUBLIC_REGISTRY_API_URL` is correct
- Check that the registry is running
- Check for CORS issues if using a remote registry

**Styles not loading:**
```bash
# Rebuild Tailwind
npm run build
```

---

## Next Steps

- [Architecture](./architecture.md) - Understand the project structure
- [API Client](./api-client.md) - Learn how to use the Registry API
- [Components](./components.md) - Explore reusable components
