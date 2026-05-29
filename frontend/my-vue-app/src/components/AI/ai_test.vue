<template>
  <div class="chat-wrapper">

    <div class="header">
      <div class="title">系统AI 助手</div>
      <div class="status-indicator">
        状态: <span :class="status.toLowerCase()">{{ statusText }}</span>
      </div>
    </div>


    <div class="chat-content" ref="scrollContainer">

      <div
        v-for="(msg,index) in chatHistory"
        :key="index"
        :class="['msg-row',msg.role]"
      >

        <div class="avatar">
          {{ msg.role === 'user' ? 'ME' : 'AI' }}
        </div>

        <div class="bubble">

          <div class="text">
            {{ msg.content || (msg.role==='assistant' && loading ? '●●●' : '') }}
          </div>

        </div>

      </div>

    </div>


    <div class="input-container">

      <textarea
        v-model="inputMsg"
        @keydown.enter.exact.prevent="handleSend"
        placeholder="请描述您的问题..."
        :disabled="loading"
      ></textarea>

      <button
        @click="handleSend"
        :disabled="loading || !inputMsg.trim()"
      >
        {{ loading ? '生成中...' : '发送' }}
      </button>

    </div>

  </div>
</template>



<script setup>

import { ref,onMounted,nextTick,computed } from 'vue'

const inputMsg = ref('')
const chatHistory = ref([])
const loading = ref(false)
const status = ref('OFFLINE')
const scrollContainer = ref(null)


const statusText = computed(()=>{

  const map={
    IDLE:'空闲',
    BUSY:'模型忙碌',
    LOADING:'加载中',
    OFFLINE:'未连接'
  }

  return map[status.value] || status.value

})


const scrollToBottom = async ()=>{

  await nextTick()

  if(scrollContainer.value){
    scrollContainer.value.scrollTop =
      scrollContainer.value.scrollHeight
  }

}


const fetchStatus = async ()=>{

  try{

    const res = await fetch('/api/users/ai_chat/')
    const data = await res.json()

    status.value = data.model_status || 'OFFLINE'

  }catch{

    status.value = 'OFFLINE'

  }

}



const buildHistory = ()=>{

  const history=[]

  for(let i=0;i<chatHistory.value.length;i++){

    const msg = chatHistory.value[i]

    if(msg.role==='user'){

      const next = chatHistory.value[i+1]

      history.push([
        msg.content,
        next?.role==='assistant'?next.content:''
      ])

    }

  }

  return history

}



const handleSend = async ()=>{

  if(!inputMsg.value.trim() || loading.value) return


  const userQuery = inputMsg.value.trim()


  chatHistory.value.push({
    role:'user',
    content:userQuery
  })


  const aiReply = {
    role:'assistant',
    content:''
  }

  chatHistory.value.push(aiReply)


  inputMsg.value=''
  loading.value=true


  scrollToBottom()


  try{

    const response = await fetch('/api/users/ai_chat/',{

      method:'POST',

      headers:{
        'Content-Type':'application/json'
      },

      body:JSON.stringify({
        query:userQuery,
        history:buildHistory()
      })

    })


    if(!response.ok){
      throw new Error(`HTTP ${response.status}`)
    }


    const reader = response.body.getReader()
    const decoder = new TextDecoder()


    const readStream = async ()=>{

      const {done,value} = await reader.read()

      if(done) return


      const chunk = decoder.decode(value,{stream:true})

      const lines = chunk.split('\n\n')


      for(const line of lines){

        if(!line.startsWith('data: ')) continue

        const dataStr = line.slice(6).trim()

        if(dataStr==='[DONE]') return


        try{

          const payload = JSON.parse(dataStr)

          if(payload.token){

            aiReply.content += payload.token

            scrollToBottom()

          }

        }catch{
            console.warn('无法解析的行:', line)
        }

      }

      await readStream()

    }


    await readStream()

  }
  catch(err){

    aiReply.content = `❌ ${err.message}`

  }
  finally{

    loading.value=false
    fetchStatus()

  }

}


onMounted(()=>{

  fetchStatus()

})

</script>

<style scoped>
.chat-wrapper {
  max-width: 900px; margin: 20px auto;
  border: 1px solid #e0e0e0; border-radius: 12px;
  display: flex; flex-direction: column;
  height: 85vh; background: #fff; overflow: hidden;
}

.header {
  padding: 15px 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}

.title { font-weight: bold; font-size: 18px; color: #2c3e50; }

.status-indicator span { padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; }
.idle { background: #e8f5e9; color: #2e7d32; }
.busy { background: #fff3e0; color: #ef6c00; }
.loading { background: #e3f2fd; color: #1565c0; }
.offline { background: #fafafa; color: #999; }

.chat-content { flex: 1; overflow-y: auto; padding: 20px; background: #f9f9f9; }

.msg-row { display: flex; margin-bottom: 18px; }
.msg-row.user { flex-direction: row-reverse; }

.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: #eee; display: flex; align-items: center; justify-content: center;
  margin: 0 10px; font-size: 12px; flex-shrink: 0;
}

.user .avatar { background: #007bff; color: white; }

.bubble {
  max-width: 75%; padding: 12px 16px; border-radius: 16px;
  font-size: 14px; line-height: 1.5;
}

.user .bubble { background: #007bff; color: white; border-bottom-right-radius: 2px; }
.assistant .bubble { 
  background: #fff; color: #333; 
  border-bottom-left-radius: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
}

.typing {
  letter-spacing: 4px; color: #999;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; }
}

.input-container { padding: 16px; border-top: 1px solid #eee; display: flex; gap: 10px; background: #fff; }

textarea {
  flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #ddd;
  resize: none; height: 44px; outline: none;
}

button {
  padding: 0 20px; border: none; background: #007bff;
  color: white; border-radius: 8px; cursor: pointer; font-weight: bold;
}

button:disabled { background: #ccc; cursor: not-allowed; }
</style>