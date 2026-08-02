/** @type {import('next').NextConfig} */
const nextConfig = {
  // static files for nginx
  output: "export",
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
