FROM node:20-slim AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install dependencies (including devDependencies for build)
# Try npm ci first (faster and more reliable), fall back to npm install if it fails
# Use --legacy-peer-deps to handle peer dependency conflicts
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy configuration files first
COPY tsconfig.json next.config.mjs package.json ./
COPY components.json postcss.config.js tailwind.config.ts ./

# Explicitly copy source directories to ensure they're included
COPY src/ ./src/
COPY public/ ./public/

# Verify what files are actually copied (debug)
RUN echo "=== File Verification ===" && \
    echo "Current directory:" && pwd && \
    echo "" && echo "Does src directory exist?" && test -d src && echo "YES - Contents:" && ls -la src/ | head -10 || echo "NO" && \
    echo "" && echo "Does src/lib exist?" && test -d src/lib && echo "YES" || echo "NO" && \
    echo "" && echo "Hook files check:" && \
    (test -f src/lib/hooks/mutations/useAuth.ts && echo "✓ useAuth.ts found" || echo "✗ useAuth.ts NOT found") && \
    (test -f src/lib/hooks/queries/useClients.ts && echo "✓ useClients.ts found" || echo "✗ useClients.ts NOT found") && \
    (test -f src/lib/hooks/ui/useToast.ts && echo "✓ useToast.ts found" || echo "✗ useToast.ts NOT found") && \
    echo "" && echo "Directory structure:" && find src/lib/hooks -type f 2>/dev/null | head -10 || echo "src/lib/hooks not found"

# Set environment variables for build
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_CRM_URL
ARG NEXT_PUBLIC_TASK_URL
ARG NEXT_PUBLIC_EMAIL_URL
ARG NEXT_PUBLIC_ANALYTICS_URL

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_CRM_URL=$NEXT_PUBLIC_CRM_URL
ENV NEXT_PUBLIC_TASK_URL=$NEXT_PUBLIC_TASK_URL
ENV NEXT_PUBLIC_EMAIL_URL=$NEXT_PUBLIC_EMAIL_URL
ENV NEXT_PUBLIC_ANALYTICS_URL=$NEXT_PUBLIC_ANALYTICS_URL

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Change ownership
RUN chown -R nextjs:nodejs /app

USER nextjs

# Expose port (Azure Web App uses PORT environment variable)
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the application
CMD ["node", "server.js"]
