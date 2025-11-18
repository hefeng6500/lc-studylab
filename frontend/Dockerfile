# 构建阶段
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制项目文件
COPY . .

# 构建应用（standalone 模式）
RUN pnpm build

# 生产阶段
FROM node:20-alpine AS runner

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 从构建阶段复制必要文件
# Next.js standalone 模式会生成 .next/standalone 目录
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# 切换到非 root 用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 设置环境变量
ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

# 启动命令（standalone 模式下的启动文件）
CMD ["node", "server.js"]

