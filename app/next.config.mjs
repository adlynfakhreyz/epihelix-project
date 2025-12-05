/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'upload.wikimedia.org',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'commons.wikimedia.org',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'commons.wikimedia.org',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'dbpedia.org',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'dbpedia.org',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
