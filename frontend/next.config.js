/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    const cleanUrl = backendUrl.replace(/\/$/, '');
    return [
      {
        source: '/api/v1/:path*',
        destination: cleanUrl.endsWith('/api/v1') 
          ? `${cleanUrl}/:path*` 
          : `${cleanUrl}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

