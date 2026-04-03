# AI SSH Client

> 🧠 AI 增强的终端 SSH 客户端，支持自然语言转命令、自动错误排障

## 功能特性

- ✨ **AI 增强**: 自然语言生成 shell 命令、命令解释、自动错误排查
- 🔌 **多种认证**: 支持密码、密钥、证书、SSH Agent 多种认证方式
- 🖥️ **现代化终端 UI**: 基于 Textual 的漂亮终端界面
- 🤖 **多 AI 服务商支持**: 兼容 OpenAI、本地 Ollama，以及所有 OpenAI 兼容 API
- 💾 **连接管理**: 保存和管理常用 SSH 连接配置

## 支持的 AI 服务商

| 服务商 | 配置示例 | 说明 |
|--------|----------|------|
| OpenAI | 原生支持 | gpt-3.5-turbo, gpt-4 等 |
| Ollama | 原生支持 | 本地运行 llama3, qwen 等开源模型 |
| 阿里云通义千问 | OpenAI 兼容 | qwen-turbo, qwen-plus 等 |
| 百度文心一言 | OpenAI 兼容 | ernie-bot-4 等 |
| 字节跳动豆包 | OpenAI 兼容 | doubao-pro 等 |
| Anthropic Claude | OpenAI 兼容 | claude-3-opus 等 (需代理) |
| Google Gemini | OpenAI 兼容 | gemini-pro 等 (需代理) |
| 讯飞星火 | OpenAI 兼容 | spark 等 |

## 截图示例

*(待添加)*

## 安装

```bash
git clone https://github.com/a523959108/ai-ssh-client.git
cd ai-ssh-client
pip install -r requirements.txt
```

## 配置

复制 `config.example.json` 到 `config.json` 并编辑配置：

```bash
cp config.example.json config.json
```

### 基本配置

**使用 OpenAI:**
```json
{
  "ai": {
    "provider": "openai",
    "openai": {
      "api_key": "your-api-key-here",
      "model": "gpt-3.5-turbo",
      "base_url": "https://api.openai.com/v1"
    }
  }
}
```

**使用本地 Ollama:**
```json
{
  "ai": {
    "provider": "ollama",
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3"
    }
  }
}
```

### 主流厂商配置示例

#### 阿里云通义千问
```json
{
  "ai": {
    "provider": "openai_compatible",
    "openai_compatible": {
      "api_key": "your-dashscope-api-key",
      "model": "qwen-turbo",
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "extra_headers": {}
    }
  }
}
```

#### 百度文心一言
```json
{
  "ai": {
    "provider": "openai_compatible",
    "openai_compatible": {
      "api_key": "your-wenxin-api-key",
      "model": "ernie-3.5-8k",
      "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/",
      "extra_headers": {}
    }
  }
}
```

#### 字节跳动豆包
```json
{
  "ai": {
    "provider": "openai_compatible",
    "openai_compatible": {
      "api_key": "your-doubao-api-key",
      "model": "doubao-pro-4k",
      "base_url": "https://aquasearch.volcengineapi.com/endpoint/https://openshift.ai-bj-tj.bytegoofy.com/v1",
      "extra_headers": {}
    }
  }
}
```

## 使用

```bash
python main.py
```

### 主要功能

1. **连接管理**: 在主界面选择已保存连接或新建连接
2. **AI 命令生成**: 在 AI 面板输入自然语言描述需求，AI 自动生成命令
3. **命令解释**: 输入命令后点击解释，AI 解释命令用途
4. **错误排查**: 命令出错后，点击排错，AI 自动分析问题

## 系统要求

- Python 3.9+
- 支持 Intel Mac (本项目开发环境)
- 支持 Linux/macOS

## 依赖

- `paramiko` - SSH 连接库
- `textual` - 终端 UI 框架
- `openai` - OpenAI API 客户端，兼容各类 OpenAI 格式API
- `pydantic` - 数据验证
- `requests` - HTTP 请求

## 许可证

MIT License

## 作者

a523959108
