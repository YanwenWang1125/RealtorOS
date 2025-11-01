# RealtorOS Frontend

Next.js 14 frontend application for RealtorOS CRM system.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages and layouts
│   │   ├── (auth)/            # Authentication routes (login, register)
│   │   ├── (dashboard)/       # Dashboard routes (protected)
│   │   └── layout.tsx         # Root layout
│   ├── components/            # React components
│   │   ├── layout/             # Layout components (Header, Sidebar, Footer)
│   │   └── ui/               # Base UI components (Button, Input, Card, etc.)
│   ├── lib/                   # Core library code
│   │   ├── api/              # API client and endpoints
│   │   │   ├── client.ts    # Axios client configuration
│   │   │   └── endpoints/    # API endpoint functions
│   │   ├── constants/        # Application constants
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── providers/            # React context providers
│   ├── store/                # State management (if needed)
│   └── styles/               # Global styles
├── public/                    # Static assets
├── .eslintrc.json            # ESLint configuration
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Getting Started

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Key Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Axios** for API calls
- **Type-safe API client** matching backend schemas
- **Reusable UI components**
- **Custom hooks** for API interactions

## Configuration

### API Client

The API client is configured in `src/lib/api/client.ts` and uses Axios with:
- Request/response interceptors
- Error handling
- Base URL configuration from environment variables

### Type Definitions

Type definitions in `src/lib/types/` match the backend Pydantic schemas:
- `client.types.ts` - Client entities
- `task.types.ts` - Task entities
- `email.types.ts` - Email entities
- `dashboard.types.ts` - Dashboard data
- `api.types.ts` - API-related types

### Constants

Application constants are organized in `src/lib/constants/`:
- `api.endpoints.ts` - API endpoint URLs
- `client.constants.ts` - Client-related constants
- `task.constants.ts` - Task-related constants
- `email.constants.ts` - Email-related constants
- `pagination.constants.ts` - Pagination defaults

## Project Status

This is the foundational structure. Feature components and pages are to be implemented in subsequent steps.

