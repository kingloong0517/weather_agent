import axios from 'axios'
import type { ChatRequest, ChatResponse, ToolInfo } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

export const chatApi = {
  sendMessage: async (query: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', { query })
    return response.data
  },

  getTools: async (): Promise<ToolInfo[]> => {
    const response = await api.get<ToolInfo[]>('/tools')
    return response.data
  }
}

export default api
