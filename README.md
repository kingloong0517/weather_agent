# 天气 Agent 系统

一个基于规则驱动的天气查询系统，展示 AI Agent 的执行流程。

## 项目结构

```
weather_agent/
├── backend/           # 后端代码
│   ├── app/
│   │   ├── agents/    # Agent 模块
│   │   ├── api/       # API 路由
│   │   ├── models/    # 数据模型
│   │   ├── nlp/       # 自然语言处理
│   │   ├── rules/     # 规则引擎
│   │   ├── tools/     # 工具模块
│   │   ├── config.py  # 配置文件
│   │   └── main.py    # 主应用
│   ├── .env.example   # 环境变量示例
│   ├── requirements.txt  # 依赖包
│   └── test_nlu.py    # 测试文件
├── frontend/          # 前端代码
│   ├── dist/          # 构建输出
│   ├── src/
│   │   ├── api/       # API 调用
│   │   ├── components/ # 组件
│   │   ├── router/    # 路由
│   │   ├── stores/    # 状态管理
│   │   ├── types/     # 类型定义
│   │   ├── views/     # 视图
│   │   ├── App.vue    # 根组件
│   │   ├── main.ts    # 入口文件
│   │   └── vite-env.d.ts # Vite 类型
│   ├── .env.example   # 环境变量示例
│   ├── index.html     # HTML 模板
│   ├── package.json   # 前端依赖
│   ├── tsconfig.json  # TypeScript 配置
│   ├── tsconfig.node.json # Node TypeScript 配置
│   └── vite.config.ts # Vite 配置
└── .gitignore         # Git 忽略文件
```

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **路由**: Vue Router

### 后端
- **框架**: Python + FastAPI
- **数据验证**: Pydantic
- **自然语言处理**: 规则驱动（无大模型）
- **API 文档**: Swagger UI
- **天气 API**: 高德天气 API

## 功能特性

- **规则驱动的意图识别**: 支持天气查询和日程提醒两种意图
- **实体提取**: 提取日期、时间、地点等实体信息
- **工具调用**: 调用天气工具和日程提醒工具
- **执行流程展示**: 显示意图识别、工具调用和最终回答的完整流程
- **真实天气查询**: 集成高德天气 API 获取真实天气数据
- **美观的聊天界面**: 响应式设计，适合面试展示

## 快速开始

### 1. 安装依赖

#### 后端依赖
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt
```

#### 前端依赖
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 2. 配置环境变量

#### 后端配置
复制 `.env.example` 文件为 `.env`，并填写高德天气 API Key：
```bash
# .env 文件内容
AMAP_API_KEY=your_amap_api_key
```

### 3. 运行项目

#### 启动后端服务器
```bash
# 进入后端目录
cd backend

# 启动服务器
python -m uvicorn app.main:app --reload
```

后端服务器将运行在 `http://127.0.0.1:8000/`

#### 启动前端开发服务器
```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
```

前端开发服务器将运行在 `http://localhost:3006/`

### 4. 访问系统

打开浏览器，访问 `http://localhost:3006/` 即可使用天气 Agent 系统。

## API 接口

### 聊天接口
- **URL**: `/api/v1/chat`
- **方法**: POST
- **请求体**:
  ```json
  {
    "query": "北京今天天气怎么样"
  }
  ```
- **响应**:
  ```json
  {
    "query": "北京今天天气怎么样",
    "response": "今天北京的天气情况：晴，天气适宜，适合外出",
    "intent": "weather_query",
    "tool_calls": [
      {
        "tool": "weather_tool",
        "params": {"date": "今天", "location": "北京"},
        "result": "晴"
      }
    ],
    "execution_chain": {
      "user_input": "北京今天天气怎么样",
      "intent": "weather_query",
      "tool_calls": [
        {
          "tool": "weather_tool",
          "params": {"date": "今天", "location": "北京"},
          "result": "晴"
        }
      ],
      "final_answer": "今天北京的天气情况：晴，天气适宜，适合外出"
    }
  }
  ```

## 示例使用

### 天气查询
- **输入**: "北京今天天气怎么样"
- **输出**:
  ```
  用户：北京今天天气怎么样
  Agent：
  → 意图识别：天气查询
  → 调用工具：weather_tool
  → 返回结果：晴
  → 最终回答：今天北京的天气情况：晴，天气适宜，适合外出
  ```

### 日程提醒
- **输入**: "提醒我明天下午3点开会"
- **输出**:
  ```
  用户：提醒我明天下午3点开会
  Agent：
  → 意图识别：日程提醒
  → 调用工具：schedule_tool
  → 返回结果：ok
  → 最终回答：已成功设置明天下午3点的开会提醒
  ```

## 项目特点

1. **完全规则驱动**: 无大模型依赖，适合作为 AI Agent 的教学示例
2. **模块化设计**: 前后端分离，后端按功能模块划分，易于扩展
3. **可扩展性**: 支持后续接入大模型，增加更多工具
4. **美观的界面**: 响应式设计，适合面试展示
5. **真实天气数据**: 集成高德天气 API 获取真实天气信息

## 扩展建议

1. **接入大模型**: 将规则驱动的意图识别替换为大模型
2. **增加更多工具**: 如地图查询、新闻查询等
3. **优化前端界面**: 添加更多交互效果和动画
4. **增加用户认证**: 实现用户登录和个性化设置
5. **添加多语言支持**: 支持中英文切换

## 许可证

MIT License

## 作者

本项目由 AI 助手生成，用于展示 AI Agent 的执行流程。