/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: '*.azurewebsites.net',
      },
      {
        protocol: 'https',
        hostname: '*.azurecontainerapps.io',
      },
    ],
  },
  async rewrites() {
    // Read API URL from environment variable at runtime (server startup)
    // This allows the URL to be set in the container app without rebuilding
    let apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000';
    
    // CRITICAL: Ensure HTTPS is used (not HTTP) to avoid CORS redirect issues
    // If the URL starts with http:// (and not localhost), convert to https://
    if (apiUrl.startsWith('http://') && !apiUrl.includes('localhost')) {
      apiUrl = apiUrl.replace('http://', 'https://');
      if (process.env.NODE_ENV !== 'production') {
        console.warn('⚠️  Converted HTTP to HTTPS:', apiUrl);
      }
    }
    
    // Log the API URL being used (only in development)
    if (process.env.NODE_ENV !== 'production') {
      console.log('🔗 Next.js API Rewrite Configuration:');
      console.log(`   Using API URL: ${apiUrl}`);
      console.log(`   Protocol: ${apiUrl.startsWith('https://') ? 'HTTPS ✅' : apiUrl.startsWith('http://') ? 'HTTP ⚠️' : 'UNKNOWN'}`);
      console.log(`   NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}`);
      console.log(`   API_URL: ${process.env.API_URL || 'NOT SET'}`);
      if (!process.env.NEXT_PUBLIC_API_URL && !process.env.API_URL) {
        console.warn('⚠️  WARNING: No API URL env var found, using fallback:', apiUrl);
      }
    }
    
    // Also handle /health endpoint
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${apiUrl}/health`,
      },
    ];
  },
};

export default nextConfig;

