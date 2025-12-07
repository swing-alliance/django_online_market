<template>
  <div class="ws-test">
    <h2>WebSocket 状态测试</h2>
    
    <!-- 连接状态显示 -->
    <div class="status">
      <span :class="connectionStatus === 'connected' ? 'connected' : 'disconnected'">
        {{ connectionStatus === 'connected' ? '🟢 已连接' : '🔴 未连接' }}
      </span>
      <span v-if="connectionStatus === 'connecting'" class="connecting">⏳ 连接中...</span>
    </div>

    <!-- 连接控制 -->
    <div class="controls">
      <button @click="connectWs" :disabled="connectionStatus === 'connected'">
        连接
      </button>
      <button @click="disconnectWs" :disabled="connectionStatus === 'disconnected'">
        断开
      </button>
      <button @click="sendTestMessage" :disabled="connectionStatus !== 'connected'">
        发送测试消息
      </button>
    </div>

    <!-- 消息显示 -->
    <div class="messages">
      <h3>消息记录</h3>
      <div v-for="(message, index) in messages" :key="index" class="message">
        <div class="message-header">
          <span class="timestamp">{{ formatTimestamp(message.timestamp) }}</span>
          <span class="type">{{ message.type }}</span>
        </div>
        <div class="message-content">{{ message.content }}</div>
      </div>
    </div>

    <!-- 当前用户状态 -->
    <div class="user-status" v-if="currentStatus">
      <h3>当前状态: {{ currentStatus }}</h3>
      <button @click="updateStatus('online')" :disabled="currentStatus === 'online'">设为在线</button>
      <button @click="updateStatus('away')" :disabled="currentStatus === 'away'">设为离开</button>
      <button @click="updateStatus('offline')" :disabled="currentStatus === 'offline'">设为离线</button>
    </div>
  </div>
</template>

<script setup>
import { ref,  onUnmounted , onMounted} from 'vue'

const ws = ref(null)
const connectionStatus = ref('disconnected')
const messages = ref([])
const currentStatus = ref(null)

// WebSocket URL - 根据你的实际地址调整
const WS_URL = '/ws/status/'

const connectWs = () => {
  console.log('尝试连接 WebSocket...')
  try {
    ws.value = new WebSocket(WS_URL)
    ws.value.onopen = (event) => {
      console.log('WebSocket 连接已建立', event)
      connectionStatus.value = 'connected'
      addMessage('system', 'WebSocket 连接成功', new Date())
    }
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到消息:', data)
        addMessage('receive', JSON.stringify(data, null, 2), new Date())
        
        // 处理不同类型的消息
        handleMessage(data)
      } catch (error) {
        console.error('解析消息失败:', error)
        addMessage('error', `解析消息失败: ${event.data}`, new Date())
      }
    }

    // WebSocket 关闭后的回调
    ws.value.onclose = (event) => {
      console.log('WebSocket 连接已关闭', event)
      connectionStatus.value = 'disconnected'
      addMessage('system', `连接已关闭: ${event.code} ${event.reason}`, new Date())
    }

    // 发生错误时的回调
    ws.value.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      connectionStatus.value = 'disconnected'
      addMessage('error', '连接发生错误', new Date())
    }

  } catch (error) {
    console.error('创建 WebSocket 失败:', error)
    addMessage('error', `创建连接失败: ${error.message}`, new Date())
  }
}

// 断开连接
const disconnectWs = () => {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
}

// 发送测试消息
const sendTestMessage = () => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    const testMessage = {
      type: 'test',
      message: 'Hello from Vue frontend!',
      timestamp: new Date().toISOString()
    }
    
    const messageStr = JSON.stringify(testMessage)
    ws.value.send(messageStr)
    addMessage('send', messageStr, new Date())
  } else {
    alert('WebSocket 未连接')
  }
}

// 更新用户状态
const updateStatus = (status) => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    const statusMessage = {
      type: 'status_update',
      status: status,
      timestamp: new Date().toISOString()
    }
    
    const messageStr = JSON.stringify(statusMessage)
    ws.value.send(messageStr)
    addMessage('send', `状态更新: ${status}`, new Date())
  } else {
    alert('WebSocket 未连接')
  }
}

// 处理接收到的消息
const handleMessage = (data) => {
  switch (data.type) {
    case 'status_update':
      currentStatus.value = data.status
      break
    case 'user_status':
      // 处理用户状态更新
      console.log('用户状态:', data.user_id, data.status)
      break
    case 'broadcast':
      // 处理广播消息
      console.log('广播消息:', data.content)
      break
    default:
      console.log('未知消息类型:', data.type)
  }
}

// 添加消息到记录
const addMessage = (type, content, timestamp) => {
  messages.value.unshift({
    type,
    content,
    timestamp: timestamp || new Date()
  })
  
  // 保持最多 50 条消息
  if (messages.value.length > 50) {
    messages.value = messages.value.slice(0, 50)
  }
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

onMounted(() => {connectWs()})
  

onUnmounted(() => {
  disconnectWs()
})
</script>

<style scoped>
.ws-test {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.status {
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 4px;
  background: #f5f5f5;
}

.connected {
  color: #28a745;
  font-weight: bold;
}

.disconnected {
  color: #dc3545;
  font-weight: bold;
}

.connecting {
  color: #ffc107;
  font-weight: bold;
}

.controls {
  margin-bottom: 20px;
}

.controls button {
  margin-right: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.controls button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button {
  background: #007bff;
  color: white;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

.messages {
  margin-bottom: 20px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  background: white;
}

.message {
  margin-bottom: 10px;
  padding: 8px;
  border-left: 3px solid #007bff;
  background: #f8f9fa;
  border-radius: 2px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.message-content {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-all;
}

.user-status {
  padding: 15px;
  background: #071422;
  border-radius: 4px;
  border-left: 4px solid #007bff;
}

.user-status button {
  margin-right: 10px;
  margin-bottom: 5px;
}
</style>