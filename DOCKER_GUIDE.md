# Docker 部署指南

本项目已配置完整的 Docker Compose 环境，包含前端、后端、MySQL 和 Redis。

## 1. 快速启动

在项目根目录下运行：

```bash
docker-compose up -d --build
```

启动后：
- 前端访问地址：`http://localhost`
- 后端 API 地址：`http://localhost/api`
- WebSocket 地址：`ws://localhost`

## 2. 环境变量配置

你可以通过修改 `docker-compose.yml` 或创建 `.env` 文件来配置环境变量：

- `DB_PASSWORD`: 数据库密码 (默认: 20050204Ylm)
- `CORS_ALLOWED_ORIGINS`: 额外的 CORS 允许来源（逗号分隔）

## 3. 服务更新与替换

如果你修改了代码并想更新服务，可以使用以下命令：

### 更新所有服务
```bash
docker-compose up -d --build
```

### 仅更新后端
```bash
docker-compose up -d --build backend
```

### 仅更新前端
```bash
docker-compose up -d --build frontend
```

Docker Compose 会自动检测变更，重新构建镜像并替换运行中的容器，实现平滑更新。

## 4. 常用命令

- **查看日志**: `docker-compose logs -f`
- **停止服务**: `docker-compose down`
- **查看容器状态**: `docker-compose ps`
- **进入后端容器**: `docker-compose exec backend bash`

## 5. 注意事项

- 数据库数据持久化在 `db_data` 卷中，即使删除容器数据也不会丢失。
- 前端构建使用了多阶段构建，镜像体积小且性能高。
- Nginx 负责反向代理，解决了跨域问题。
