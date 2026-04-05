import { defineStore } from 'pinia'
import axios from 'axios'

// 配置 axios
axios.defaults.headers.common['Content-Type'] = 'application/json;charset=utf-8'
axios.defaults.headers.common['Accept'] = 'application/json;charset=utf-8'
axios.defaults.timeout = 10000

export interface ToolCall {
  tool: string
  params: any
  result: string
}

export interface Message {
  query: string
  response?: string
  entities?: any
  intent?: string
  confidence?: number
  tool_calls?: ToolCall[]
  execution_chain?: any
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as Message[],
    loading: false
  }),
  actions: {
    async sendMessage(query: string) {
      this.loading = true
      try {
        console.log('发送请求:', query)
        const response = await axios.post('/api/v1/chat', { query })
        console.log('收到响应:', response.data)
        this.messages.push({
          query,
          response: response.data.response,
          intent: response.data.intent,
          tool_calls: response.data.tool_calls,
          execution_chain: response.data.execution_chain
        })
      } catch (error: any) {
        console.error('发送消息错误:', error)
        console.error('错误详情:', error.message)
        if (error.response) {
          console.error('响应错误:', error.response.data)
          console.error('响应状态:', error.response.status)
        } else if (error.request) {
          console.error('请求错误:', error.request)
        }
        this.messages.push({
          query,
          response: '发送失败，请重试'
        })
      } finally {
        this.loading = false
      }
    }
  }
})
