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
  async headers() {
    return [
      {
        // Apply headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'unsafe-none', // Allows postMessage for Google OAuth (required for @react-oauth/google)
          },
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'unsafe-none', // Allows embedding content from other origins
          },
        ],
      },
    ];
  },
};

export default nextConfig;

