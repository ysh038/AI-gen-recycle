// frontend-migration/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'http',
          hostname: 'localhost',
          port: '9000',  // MinIO 포트
          pathname: '/**',
        },
        // 프로덕션에서는 S3 도메인 추가
        // {
        //   protocol: 'https',
        //   hostname: 's3.amazonaws.com',
        //   pathname: '/**',
        // },
      ],
    },
  }
  
  module.exports = nextConfig