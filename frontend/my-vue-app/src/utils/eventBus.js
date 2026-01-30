
import mitt from 'mitt';
const emitter = mitt();

export default emitter;

/*
pending-update  用于通知的待处理事项数量更新
login-requested
logout-requested
new-received-message 用于处理接受到的聊天信息
*/
