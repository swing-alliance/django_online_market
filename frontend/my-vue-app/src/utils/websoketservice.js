import emitter from "./eventBus";
import { useMessageStore } from '@/stores/WsStore.js';
const WS_URL = `ws://${window.location.host}/ws/status/`;
let wsInstance = null;
let reconnectTimer = null;
let RECONNECT_DELAY = 5000; // 重连间隔 5 秒,逐渐增加,最大30秒
const HEARTBEAT_INTERVAL = 40000; // 30 秒发送一次心跳 (Ping)
const HEARTBEAT_TIMEOUT = 10000;  // 10 秒内未收到任何消息，则认为断开

let heartbeatTimer = null;
let timeoutTimer = null;

// --- 心跳管理函数 ---
function startHeartbeat() {
    heartbeatTimer = setInterval(() => {
        if (wsInstance && wsInstance.readyState === 1) {
            wsInstance.send(JSON.stringify({ type: 'ping' }));
            console.log('Ping');
            timeoutTimer = setTimeout(() => {
                console.warn('!!! 心跳超时，连接断开 !!!');
                if (wsInstance) {
                    wsInstance.close();
                }
            }, HEARTBEAT_TIMEOUT);
        }
    }, HEARTBEAT_INTERVAL);
}

/*重置心跳机制：收到任何消息后调用，以避免超时断开*/
function resetHeartbeat() {
    clearTimeout(timeoutTimer);
}

/* 停止心跳机制：连接关闭或断开时调用 */
function stopHeartbeat() {
    clearInterval(heartbeatTimer);
    clearTimeout(timeoutTimer);
}

// --- 核心连接函数 ---
function connect() {
    // 检查：如果正在连接 (0) 或已连接 (1)，则返回
    if (wsInstance && (wsInstance.readyState === 0 || wsInstance.readyState === 1)) {
        return;
    }
    stopHeartbeat(); 
    wsInstance = new WebSocket(WS_URL);
    wsInstance.onopen = () => {
        console.log('WebSocket 连接已建立');
        RECONNECT_DELAY = 5000;
        clearTimeout(reconnectTimer);
        startHeartbeat(); // 📌 连接成功后启动心跳
    };


    wsInstance.onmessage = (event) => {
        resetHeartbeat(); 
        "关键的消息处理逻辑"
        try {
            const messageStore = useMessageStore();
            const data = JSON.parse(event.data);
            if (data.type === 'pong') {
                console.log('Pong');
                return; 
            }
            if (data.type === 'pending_requests') {
                emitter.emit('pending-update', data.count);
                return; 
            }
            if (data.type === 'receivemessage') {
                messageStore.handleWsMessage(data);
                return; 
            }
            console.log('收到业务消息:', data);
        } catch (e) {
            console.error('消息解析错误:', e);
        }
    };

    wsInstance.onerror = (error) => {
        console.error('WebSocket 连接出错:', error);
        if (wsInstance) {
            // 触发 close，让 onclose 来处理重连
            wsInstance.close(); 
        }
    };

    wsInstance.onclose = (event) => {
        console.log('WebSocket 连接已关闭。');
        stopHeartbeat(); // 📌 连接关闭时停止心跳和超时
        wsInstance = null; // 清理实例引用
        if (!event.wasClean) {
            reconnect();
        }
    };
}

function reconnect(){
    if(reconnectTimer){
        clearTimeout(reconnectTimer);
    }
    reconnectTimer = setTimeout(connect, RECONNECT_DELAY);
    if (RECONNECT_DELAY < 30000){
        RECONNECT_DELAY += 1000 ;
    }
}

function disconnect() {
    if (wsInstance) {
        wsInstance.close();
    }
}

// 封装发送方法
function send(data) {
    if (wsInstance && wsInstance.readyState === 1) {
        wsInstance.send(JSON.stringify(data));
    } else {
        console.warn('WebSocket 未连接，消息发送失败。');
    }
}

function receive(data) {
    console.log('接收到消息:', data);
}

// 导出公共接口
export default {
    connect,
    send,
    receive,
    disconnect,
    // 1. 获取原始状态码 (0:连接中, 1:已连接, 2:关闭中, 3:已关闭)
    get readyState() {
        return wsInstance ? wsInstance.readyState : WebSocket.CLOSED;
    },
    // 2. 检查是否处于“健康且可用”状态
    isConnected() {
        return wsInstance !== null && wsInstance.readyState === WebSocket.OPEN;
    },
    // 3. 返回可读的状态文字信息
    getStatusText() {
        const states = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'];
        return wsInstance ? states[wsInstance.readyState] : 'CLOSED';
    }
};
connect();