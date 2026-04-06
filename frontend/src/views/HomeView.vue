<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const inputMessage = ref('')

const sendMessage = async () => {
  if (inputMessage.value.trim()) {
    await chatStore.sendMessage(inputMessage.value)
    inputMessage.value = ''
  }
}
</script>

<template>
  <div class="home">
    <div class="chat-container">
      <div class="chat-header">
        <h1>天气 Agent</h1>
      </div>
      
      <div class="chat-body">
        <div v-for="(msg, index) in chatStore.messages" :key="index" class="message">
          <!-- 用户输入 -->
          <div class="message-user">
            <div class="message-label">用户：</div>
            <div class="message-text">{{ msg.query }}</div>
          </div>
          
          <!-- Agent 执行流程 -->
          <div class="message-agent" v-if="msg.response">
            <div class="message-label">Agent：</div>
            <div class="agent-flow">
              <!-- 意图识别 -->
              <div class="flow-step" v-if="msg.intent">
                <span class="flow-arrow">→</span> 意图识别：{{ msg.intent === 'weather_query' ? '天气查询' : msg.intent === 'schedule_reminder' ? '日程提醒' : msg.intent }}
              </div>
              
              <!-- ReAct 步骤 -->
              <div v-for="(step, step_index) in msg.execution_chain?.react_steps" :key="step_index" class="flow-step" :class="step.type">
                <span class="flow-arrow">→</span> 
                <span v-if="step.type === 'thought'">思考：{{ step.content }}</span>
                <span v-else-if="step.type === 'action'">动作：{{ step.content }}</span>
                <span v-else-if="step.type === 'observation'">观察：{{ step.content }}</span>
              </div>
              
              <!-- 工具调用 -->
              <div v-for="(tool_call, tool_index) in msg.tool_calls" :key="tool_index" class="flow-step">
                <span class="flow-arrow">→</span> 调用工具：{{ tool_call.tool }}
              </div>
              
              <!-- 工具返回结果 -->
              <div v-for="(tool_call, tool_index) in msg.tool_calls" :key="tool_index" class="flow-step">
                <span class="flow-arrow">→</span> 返回结果：{{ tool_call.result }}
              </div>
              
              <!-- 最终回答 -->
              <div class="flow-step flow-final">
                <span class="flow-arrow">→</span> 最终回答：{{ msg.response }}
              </div>
            </div>
          </div>
        </div>
        <div v-if="chatStore.loading" class="loading">加载中...</div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          placeholder="输入天气查询，例如：北京明天天气怎么样"
          @keyup.enter="sendMessage"
        />
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  height: 100%;
  background: linear-gradient(135deg, #ffeb3b 0%, #2196f3 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1IiBoZWlnaHQ9IjUiPgo8cmVjdCB3aWR0aD0iNSIgaGVpZ2h0PSI1IiBmaWxsPSIjZmZmZmZmMTAiPjwvcmVjdD4KPC9zdmc+') repeat;
  opacity: 0.1;
  z-index: 0;
}

.home > * {
  position: relative;
  z-index: 1;
}

.chat-container {
  width: 100%;
  max-width: 600px;
  height: 80vh;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 20px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  border-radius: 10px 10px 0 0;
}

.chat-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.chat-header p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 14px;
}

.chat-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message {
  margin-bottom: 20px;
  border-radius: 8px;
}

.message-user {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 8px 8px 8px 0;
  margin-bottom: 10px;
}

.message-agent {
  background: #f3e5f5;
  padding: 15px;
  border-radius: 8px 8px 0 8px;
}

.message-label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.message-text {
  color: #555;
}

.agent-flow {
  margin-top: 10px;
}

.flow-step {
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
  color: #555;
}

.flow-arrow {
  position: absolute;
  left: 0;
  color: #9c27b0;
  font-weight: bold;
}

.flow-final {
  font-weight: bold;
  color: #6a1b9a;
}

.flow-step:hover {
  background: rgba(156, 39, 176, 0.05);
  padding-left: 25px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.flow-step.thought {
  color: #2196f3;
  font-style: italic;
}

.flow-step.action {
  color: #4caf50;
  font-weight: 500;
}

.flow-step.observation {
  color: #ff9800;
}

.flow-step.thought::before {
  content: "💭 ";
}

.flow-step.action::before {
  content: "⚡ ";
}

.flow-step.observation::before {
  content: "👁️ ";
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 10px;
  border-radius: 0 0 10px 10px;
}

.chat-input .el-input {
  flex: 1;
}
</style>
