const { defineConfig } = require('@vue/cli-service');
const os = require('os');

/**
 * 自动获取本机局域网 IP 地址
 */
function getNetworkIp() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // 寻找 IPv4，非回路地址 (127.0.0.1) 且运行中的网卡
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1';
}

const localIp = getNetworkIp();
const openout = false; // 是否开启外部访问模式
const targetIp = `http://${localIp}:8000`;
const currentTarget = openout ? targetIp : 'http://127.0.0.1:8000';

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    // 📌 核心修复点：避免使用 'auto' 导致 URL 解析报错
    // 设置为具体地址或完全移除 client 配置
    client: {
      webSocketURL: `ws://${localIp}:8080/ws`,
      overlay: true, // 报错时在浏览器全屏显示
    },
    
    port: 8080,
    host: '0.0.0.0', // 允许通过 IP 访问（如手机、其他电脑）
    
    proxy: {
      // 1. 状态监控 WebSocket 代理
      '^/ws/status': {
        target: currentTarget,
        ws: true,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        // 动态重写 Cookie 域名，解决登录态失效问题
        cookieDomainRewrite: {
          'localhost': openout ? localIp : '127.0.0.1'
        },
        onProxyReqWs: (proxyReq, req) => {
          if (req.headers.cookie) {
            proxyReq.setHeader('Cookie', req.headers.cookie);
          }
        }
      },
      
      // 2. 普通 API 和 静态资源代理
      '^/(api|admin|media|static)': {
        target: currentTarget,
        changeOrigin: true,
        cookieDomainRewrite: {
          'localhost': openout ? localIp : '127.0.0.1'
        }
      }
    }
  }
});