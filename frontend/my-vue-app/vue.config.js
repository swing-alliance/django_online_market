const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    proxy: {
      '^/ws': {
        target: 'http://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        cookieDomainRewrite: {      // 关键！改写 Cookie 域名
          'localhost': '127.0.0.1'
        },
        cookiePathRewrite: {
          '/': '/'
        },
        onProxyReqWs: (proxyReq, req) => {
          if (req.headers.cookie) {
            proxyReq.setHeader('Cookie', req.headers.cookie);
          }
        }
      },
      '^/(api|admin|media|static)': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 普通请求也加一下保险
        cookieDomainRewrite: { 'localhost': '127.0.0.1' }
      }
    }
  }
})