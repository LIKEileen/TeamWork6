import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')  // 让 @ 代表 src 目录
    }
  },
  server: {
    proxy: {
      '/llm': {
        target: 'https://chat.ecnu.edu.cn/open/api/v1', // 占位，真实地址由 header 指定
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            const realTarget = req.headers['x-target-url']
            if (realTarget) {
              const host = new URL(realTarget).host
              proxyReq.setHeader('host', host)
            }
          })
        },
        bypass(req, res) {
          if (!req.headers['x-target-url']) {
            res.statusCode = 400
            res.end('Missing x-target-url header')
            return true // 阻止继续代理
          }
          return false // 继续代理
        },
        rewrite: path => path.replace(/^\/llm/, ''),
      }
    }
  }
})
