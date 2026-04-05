export interface ChatRequest {
  query: string
}

export interface ChatResponse {
  query: string
  response: string | null
  tool_calls: ToolCall[] | null
  metadata: Record<string, unknown> | null
}

export interface ToolCall {
  tool: string
  arguments: Record<string, unknown>
  result: unknown
}

export interface ToolInfo {
  name: string
  description: string
}
