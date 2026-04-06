import { defineStore } from 'pinia'

export interface ToolCall {
  tool: string
  params: any
  result: string
}

export interface ReactStep {
  type: string
  content: string
  tool?: string
  params?: any
  result?: any
}

export interface Message {
  id?: number
  query: string
  response?: string
  entities?: any
  intent?: string
  confidence?: number
  tool_calls?: ToolCall[]
  execution_chain?: {
    react_steps?: ReactStep[]
  }
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as Message[],
    loading: false
  }),
  actions: {
    addMessage(message: Message) {
      this.messages.push(message)
    },
    
    updateMessage(id: number, updates: Partial<Message>) {
      const index = this.messages.findIndex(msg => msg.id === id)
      if (index !== -1) {
        this.messages[index] = { ...this.messages[index], ...updates }
      }
    },
    
    setLoading(loading: boolean) {
      this.loading = loading
    },
    
    async sendMessage(query: string) {
      const messageId = Date.now()
      
      // 添加初始消息
      this.messages.push({
        id: messageId,
        query,
        response: '',
        intent: '',
        tool_calls: [],
        execution_chain: {
          react_steps: []
        }
      })
      
      this.loading = true
      
      try {
        console.log('开始发送消息:', query)
        console.log('请求URL:', window.location.origin + '/api/v1/chat/stream')
        
        // 使用流式接口
        const response = await fetch('/api/v1/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json;charset=utf-8'
          },
          body: JSON.stringify({ query })
        })
        
        console.log('响应状态:', response.status, response.statusText)
        
        if (!response.ok) {
          throw new Error(`网络响应错误: ${response.status} ${response.statusText}`)
        }
        
        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('无法获取响应流')
        }
        
        const decoder = new TextDecoder()
        let buffer = ''
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          buffer += decoder.decode(value, { stream: true })
          
          // 处理 SSE 事件
          const events = buffer.split('\n\n')
          buffer = events.pop() || ''
          
          for (const event of events) {
            if (!event.trim()) continue
            
            const dataIndex = event.indexOf('data: ')
            if (dataIndex !== -1) {
              const data = event.substring(dataIndex + 6)
              try {
                const parsed = JSON.parse(data)
                console.log('收到流式数据:', parsed)
                await this.processStreamEvent(messageId, parsed)
              } catch (e) {
                console.error('解析流式数据失败:', e)
                console.error('原始数据:', data)
              }
            }
          }
        }
      } catch (error: any) {
        console.error('发送消息错误:', error)
        console.error('错误详情:', error.message)
        console.error('错误堆栈:', error.stack)
        
        const index = this.messages.findIndex(msg => msg.id === messageId)
        if (index !== -1) {
          this.messages[index].response = `发送失败: ${error.message}`
        }
      } finally {
        this.loading = false
        console.log('消息发送完成')
      }
    },
    
    async processStreamEvent(messageId: number, event: any) {
      const index = this.messages.findIndex(msg => msg.id === messageId)
      if (index === -1) return
      
      switch (event.type) {
        case 'intent':
          // 更新意图
          this.messages[index].intent = event.data
          break
        case 'react_step':
          // 添加 ReAct 步骤
          if (!this.messages[index].execution_chain) {
            this.messages[index].execution_chain = { react_steps: [] }
          }
          if (!this.messages[index].execution_chain.react_steps) {
            this.messages[index].execution_chain.react_steps = []
          }
          this.messages[index].execution_chain.react_steps.push(event.data)
          break
        case 'tool_call':
          // 添加工具调用
          if (!this.messages[index].tool_calls) {
            this.messages[index].tool_calls = []
          }
          this.messages[index].tool_calls.push(event.data)
          break
        case 'final_answer':
          // 更新最终回答
          this.messages[index].response = event.data
          break
        case 'done':
          // 完成
          break
      }
    }
  }
})
