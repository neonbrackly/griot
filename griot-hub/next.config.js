/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    REGISTRY_API_URL: process.env.REGISTRY_API_URL || 'http://localhost:8000/api/v1',
  },
};

module.exports = nextConfig;
