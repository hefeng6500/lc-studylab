import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 启用 standalone 输出模式，用于 Docker 部署
  output: 'standalone',
  
  // 其他配置保持不变
  // 如果需要其他配置，可以在这里添加
};

export default nextConfig;
