// vue.config.js
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,

  devServer: {
    port: 8080,                    // 你的前端端口
    host: '0.0.0.0',
    proxy: {
      '^/ws': {
        target: 'http://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        // 💡 确保 Cookie 传递
        onProxyReq: (proxyReq, req) => {
          // 确保将浏览器的 Cookie 头复制到发送给后端的代理请求中
          if (req.headers.cookie) {
            proxyReq.setHeader('cookie', req.headers.cookie);
          }
        },
      },

      // 可选：把 Django 的 admin、api 也代理过来
      '^/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '^/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
