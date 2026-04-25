/** @type {import('next').NextConfig} */
const nextConfig = {
  // Em produção o frontend chama NEXT_PUBLIC_API_URL diretamente (sem proxy).
  // Em dev, redireciona /api/* para o backend local para evitar CORS.
  async rewrites() {
    if (process.env.NODE_ENV === "production") return [];
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/health",
        destination: "http://127.0.0.1:8000/health",
      },
    ];
  },
};

module.exports = nextConfig;
