import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 读取 .env.[mode] 注入的变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    server: {
      port: 5173,
      open: true,
      proxy: {
        // ---------- ① 普通 REST 接口 ----------
        '/api': {
          target: env.VITE_API_BASEURL || 'http://127.0.0.1:5000',
          changeOrigin: true,
          // 保留 /api 前缀，后端蓝图即写 /api/...
        },
        
        // ---------- ② ChatGPT / 流式 LLM ----------
        '/llm': {
          target: env.VITE_LLM_GATEWAY || 'https://chat.ecnu.edu.cn/open/api/v1',
          changeOrigin: true,
          secure: false,
          // 透传自定义 header 指定真实目标
          configure(proxy) {
            proxy.on('proxyReq', (proxyReq, req) => {
              const realTarget = req.headers['x-target-url']
              if (realTarget) {
                proxyReq.setHeader('host', new URL(realTarget).host)
              }
            })
          },
          bypass(req, res) {
            if (!req.headers['x-target-url']) {
              res.statusCode = 400
              res.end('Missing x-target-url header')
              return true
            }
            return false
          },
          rewrite: path => path.replace(/^\/llm/, ''),
        },
      },
    },
  }
})
