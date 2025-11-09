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
    const isProduction = process.env.NODE_ENV === 'production';
    let apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
    
    // In production, require API URL to be set - don't fall back to localhost
    if (!apiUrl) {
      if (isProduction) {
        const errorMsg = '❌ ERROR: NEXT_PUBLIC_API_URL or API_URL environment variable is required in production. Please set it in your container app configuration.';
        console.error(errorMsg);
        console.error('   Current environment variables:');
        console.error(`   NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}`);
        console.error(`   API_URL: ${process.env.API_URL || 'NOT SET'}`);
        console.error(`   NODE_ENV: ${process.env.NODE_ENV || 'NOT SET'}`);
        console.error('   All env vars with API/URL:', Object.keys(process.env).filter(k => k.includes('API') || k.includes('URL')).join(', '));
        throw new Error(errorMsg);
      }
      // Only use localhost fallback in development
      apiUrl = 'http://localhost:8000';
      console.warn('⚠️  WARNING: No API URL env var found, using localhost fallback (development only):', apiUrl);
    }
    
    // CRITICAL: Ensure HTTPS is used (not HTTP) to avoid CORS redirect issues
    // If the URL starts with http:// (and not localhost), convert to https://
    if (apiUrl.startsWith('http://') && !apiUrl.includes('localhost')) {
      apiUrl = apiUrl.replace('http://', 'https://');
      console.warn('⚠️  Converted HTTP to HTTPS:', apiUrl);
    }
    
    // Log the API URL being used (always log for debugging)
    console.log('🔗 Next.js API Rewrite Configuration:');
    console.log(`   Using API URL: ${apiUrl}`);
    console.log(`   Protocol: ${apiUrl.startsWith('https://') ? 'HTTPS ✅' : apiUrl.startsWith('http://') ? 'HTTP ⚠️' : 'UNKNOWN'}`);
    console.log(`   NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}`);
    console.log(`   API_URL: ${process.env.API_URL || 'NOT SET'}`);
    console.log(`   NODE_ENV: ${process.env.NODE_ENV || 'NOT SET'}`);
    
    // Validate that apiUrl is a valid URL
    try {
      new URL(apiUrl);
    } catch (e) {
      const errorMsg = `❌ ERROR: Invalid API URL: ${apiUrl}. Please set NEXT_PUBLIC_API_URL or API_URL environment variable with a valid URL.`;
      console.error(errorMsg);
      throw new Error(errorMsg);
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

