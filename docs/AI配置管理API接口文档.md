# AI配置管理API接口文档

## 📋 功能概述

AI配置管理功能提供多AI服务提供商配置管理能力，参考数据源配置模式，支持配置、测试、激活等功能。用户可以管理通义千问、OpenAI、Ollama等多种AI服务配置。

## 🔧 核心特性

### ✅ 统一配置管理
- **多提供者支持**: 支持通义千问、OpenAI、Ollama等
- **配置验证**: 完整的配置参数验证
- **默认配置**: 支持设置默认AI提供者

### ✅ 连通性测试
- **实时测试**: AI配置连接实时测试
- **状态记录**: 记录测试结果和错误信息
- **自动更新**: 测试后自动更新配置状态

### ✅ 安全特性
- **敏感信息保护**: API密钥在返回时自动掩码
- **权限控制**: 配置管理权限控制
- **错误处理**: 完善的错误处理和日志记录

## 🚀 API接口详情

### 1. 获取所有AI配置

**接口地址**: `GET /api/ai-configs`

**功能描述**: 获取所有AI服务配置列表

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "provider_type": "tongyi",
      "provider_name": "通义千问",
      "config_data": {
        "api_key": "sk-****-****",
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "timeout": 30
      },
      "is_active": true,
      "is_default": true,
      "status": "成功",
      "last_test_time": "2025-11-24T15:30:00",
      "error_message": null,
      "created_at": "2025-11-24T10:00:00",
      "updated_at": "2025-11-24T15:30:00"
    }
  ]
}
```

### 2. 创建AI配置

**接口地址**: `POST /api/ai-configs`

**功能描述**: 创建新的AI服务配置

**请求参数**:
```json
{
  "provider_type": "tongyi",
  "provider_name": "通义千问",
  "config_data": {
    "api_key": "your_api_key_here",
    "model": "qwen-plus",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "timeout": 30
  },
  "is_active": true,
  "is_default": false
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 2,
    "provider_type": "tongyi",
    "provider_name": "通义千问",
    "config_data": {
      "api_key": "sk-****-****",
      "model": "qwen-plus",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "timeout": 30
    },
    "is_active": true,
    "is_default": false,
    "status": "未测试",
    "last_test_time": null,
    "error_message": null,
    "created_at": "2025-11-24T16:00:00",
    "updated_at": "2025-11-24T16:00:00"
  }
}
```

### 3. 更新AI配置

**接口地址**: `PUT /api/ai-configs/{config_id}`

**功能描述**: 更新指定的AI配置

**请求参数**:
```json
{
  "provider_name": "通义千问-更新",
  "config_data": {
    "api_key": "new_api_key_here",
    "model": "qwen-turbo",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "timeout": 60
  },
  "is_active": true,
  "is_default": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "provider_type": "tongyi",
    "provider_name": "通义千问-更新",
    "config_data": {
      "api_key": "sk-****-****",
      "model": "qwen-turbo",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "timeout": 60
    },
    "is_active": true,
    "is_default": true,
    "status": "未测试",
    "last_test_time": null,
    "error_message": null,
    "created_at": "2025-11-24T10:00:00",
    "updated_at": "2025-11-24T16:00:00"
  }
}
```

### 4. 删除AI配置

**接口地址**: `DELETE /api/ai-configs/{config_id}`

**功能描述**: 删除指定的AI配置

**响应示例**:
```json
{
  "success": true,
  "message": "删除成功"
}
```

**注意**: 不能删除默认配置

### 5. 测试AI配置连通性

**接口地址**: `POST /api/ai-configs/{config_id}/test`

**功能描述**: 测试AI配置的连通性和有效性

**响应示例**:
```json
{
  "success": true,
  "message": "连接测试成功",
  "data": {
    "test_response": "测试成功",
    "test_time": "2025-11-24T16:00:00"
  }
}
```

**失败响应**:
```json
{
  "success": false,
  "message": "连接测试失败: API密钥无效"
}
```

### 6. 获取当前激活的AI配置

**接口地址**: `GET /api/ai-configs/active`

**功能描述**: 获取当前激活使用的AI配置

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "provider_type": "tongyi",
    "provider_name": "通义千问",
    "config_data": {
      "api_key": "sk-****-****",
      "model": "qwen-plus",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "timeout": 30
    },
    "is_active": true,
    "is_default": true,
    "status": "成功",
    "last_test_time": "2025-11-24T15:30:00",
    "error_message": null,
    "created_at": "2025-11-24T10:00:00",
    "updated_at": "2025-11-24T15:30:00"
  }
}
```

### 7. 获取当前AI配置（兼容接口）

**接口地址**: `GET /api/ai-configs/current`

**功能描述**: 获取当前AI配置（兼容原有的AI推荐接口格式）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "ai_config": {
      "provider": "tongyi",
      "tongyi": {
        "api_key": "your_api_key_here",
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "timeout": 30
      },
      "openai": {
        "api_key": "",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30
      },
      "ollama": {
        "base_url": "http://localhost:11434",
        "model": "qwen2.5-coder",
        "timeout": 30
      }
    },
    "is_configured": true,
    "current_provider": "tongyi",
    "supported_providers": ["tongyi", "openai", "ollama"]
  },
  "message": "获取AI配置成功"
}
```

### 8. 设置默认AI配置

**接口地址**: `POST /api/ai-configs/{config_id}/set-default`

**功能描述**: 设置指定配置为默认AI服务

**响应示例**:
```json
{
  "success": true,
  "message": "已设置 通义千问 为默认配置",
  "data": {
    "id": 1,
    "provider_type": "tongyi",
    "provider_name": "通义千问",
    "config_data": {
      "api_key": "sk-****-****",
      "model": "qwen-plus"
    },
    "is_active": true,
    "is_default": true,
    "status": "成功"
  }
}
```

### 9. 获取支持的AI配置类型

**接口地址**: `GET /api/ai-configs/types`

**功能描述**: 获取支持的AI服务提供商类型和配置模板

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "type": "tongyi",
      "name": "通义千问",
      "description": "阿里云通义千问大语言模型",
      "required_fields": ["api_key", "model"],
      "optional_fields": ["base_url", "timeout"],
      "default_config": {
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "timeout": 30
      }
    },
    {
      "type": "openai",
      "name": "OpenAI",
      "description": "OpenAI GPT系列模型",
      "required_fields": ["api_key", "model"],
      "optional_fields": ["base_url", "timeout"],
      "default_config": {
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1",
        "timeout": 30
      }
    },
    {
      "type": "ollama",
      "name": "Ollama",
      "description": "本地部署的Ollama服务",
      "required_fields": [],
      "optional_fields": ["base_url", "model", "timeout"],
      "default_config": {
        "base_url": "http://localhost:11434",
        "model": "qwen2.5-coder",
        "timeout": 30
      }
    }
  ],
  "message": "获取AI配置类型成功"
}
```

## 📊 数据模型

### AIConfig 表结构

```sql
CREATE TABLE ai_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    provider_type VARCHAR(50) NOT NULL COMMENT 'AI提供者类型',
    provider_name VARCHAR(100) NOT NULL COMMENT 'AI服务名称',
    config_data JSON COMMENT '配置数据',
    is_active BOOLEAN DEFAULT FALSE COMMENT '是否激活',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认服务',
    status VARCHAR(20) DEFAULT '未测试' COMMENT '连接状态',
    last_test_time DATETIME COMMENT '最后测试时间',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
);
```

## 🎯 使用示例

### 1. 创建通义千问配置

```javascript
// 创建通义千问配置
fetch('/api/ai-configs', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        provider_type: 'tongyi',
        provider_name: '通义千问-生产',
        config_data: {
            api_key: 'your_tongyi_api_key',
            model: 'qwen-plus',
            base_url: 'https://dashscope.aliyuncs.com/api/v1',
            timeout: 30
        },
        is_active: true,
        is_default: true
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('AI配置创建成功:', data.data);
    } else {
        console.error('创建失败:', data.message);
    }
});
```

### 2. 测试配置连通性

```javascript
// 测试配置连通性
const configId = 1;
fetch(`/api/ai-configs/${configId}/test`, {
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('连接测试成功:', data.data.test_response);
    } else {
        console.error('连接测试失败:', data.message);
    }
});
```

### 3. 设置默认配置

```javascript
// 设置默认配置
const configId = 1;
fetch(`/api/ai-configs/${configId}/set-default`, {
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('默认配置设置成功');
    } else {
        console.error('设置失败:', data.message);
    }
});
```

### 4. 获取配置类型信息

```javascript
// 获取支持的配置类型
fetch('/api/ai-configs/types')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 获取通义千问的默认配置模板
            const tongyiType = data.data.find(type => type.type === 'tongyi');
            console.log('通义千问配置模板:', tongyiType.default_config);
        }
    });
```

## ⚙️ 配置类型说明

### 1. 通义千问 (tongyi)

**必需字段**:
- `api_key`: API密钥
- `model`: 模型名称 (qwen-plus, qwen-turbo)

**可选字段**:
- `base_url`: API地址 (默认: https://dashscope.aliyuncs.com/api/v1)
- `timeout`: 超时时间 (默认: 30秒)

**示例配置**:
```json
{
  "api_key": "sk-your-api-key-here",
  "model": "qwen-plus",
  "base_url": "https://dashscope.aliyuncs.com/api/v1",
  "timeout": 30
}
```

### 2. OpenAI

**必需字段**:
- `api_key`: API密钥
- `model`: 模型名称 (gpt-3.5-turbo, gpt-4)

**可选字段**:
- `base_url`: API地址 (默认: https://api.openai.com/v1)
- `timeout`: 超时时间 (默认: 30秒)

**示例配置**:
```json
{
  "api_key": "sk-your-openai-key-here",
  "model": "gpt-3.5-turbo",
  "base_url": "https://api.openai.com/v1",
  "timeout": 30
}
```

### 3. Ollama

**必需字段**: 无

**可选字段**:
- `base_url`: 服务地址 (默认: http://localhost:11434)
- `model`: 模型名称 (默认: qwen2.5-coder)
- `timeout`: 超时时间 (默认: 30秒)

**示例配置**:
```json
{
  "base_url": "http://localhost:11434",
  "model": "qwen2.5-coder",
  "timeout": 30
}
```

## ⚠️ 安全注意事项

### 1. API密钥安全
- **加密存储**: API密钥在数据库中安全存储
- **返回掩码**: API密钥在API返回时自动掩码显示
- **传输安全**: 建议使用HTTPS传输

### 2. 配置验证
- **字段验证**: 所有配置字段都经过验证
- **类型检查**: 配置参数类型和格式检查
- **连通性测试**: 新配置必须通过连通性测试

### 3. 权限控制
- **操作权限**: 建议为配置管理设置操作权限
- **审计日志**: 记录所有配置变更操作
- **删除保护**: 防止删除默认配置

## 🔧 数据库初始化

```bash
# 创建AI配置表
python create_ai_config_table.py
```

该脚本会：
1. 创建 `ai_config` 表
2. 初始化三种AI提供者的默认配置模板
3. 设置初始状态为未激活

## 📈 配置优先级

系统AI配置的加载优先级：

1. **数据库AI配置** (最高优先级)
2. **数据库系统配置** (中等优先级)
3. **应用配置文件** (最低优先级)

这确保了用户配置的AI服务具有最高优先级，同时保持向后兼容性。

## 🎉 功能特点

### ✅ 已实现功能
- **统一配置管理**: 与数据源配置一致的API设计
- **多提供者支持**: 通义千问、OpenAI、Ollama全支持
- **实时连通性测试**: AI配置连接测试功能
- **安全信息保护**: API密钥掩码显示
- **默认配置管理**: 支持设置默认AI服务
- **兼容性保证**: 兼容现有AI推荐功能

现在你可以按照数据源配置的模式来实现前端AI配置管理界面了！