import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Allow cross-origin requests in development (for network access)
  allowedDevOrigins: process.env.NODE_ENV === 'development' 
    ? ['10.5.137.35', 'localhost', '127.0.0.1'] 
    : [],
};

export default nextConfig;
