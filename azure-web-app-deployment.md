# Azure Web App 部署指南

## 📋 前置要求

1. Azure 账户
2. Azure CLI 已安装
3. Docker Desktop（用于本地测试）

## 🚀 部署步骤

### 1. 创建 Azure Web App

```bash
# 登录 Azure
az login

# 设置变量
RESOURCE_GROUP="realtoros-rg"
APP_NAME="realtoros-frontend"
LOCATION="eastus"
PLAN_NAME="realtoros-plan"

# 创建资源组
az group create --name $RESOURCE_GROUP --location $LOCATION

# 创建 App Service Plan
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux

# 创建 Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "NODE:20-lts"
```

### 2. 配置环境变量

```bash
# 设置环境变量（替换为你的实际URL）
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    NEXT_PUBLIC_API_URL="https://realtoros-auth.azurewebsites.net" \
    NEXT_PUBLIC_CRM_URL="https://realtoros-crm.azurewebsites.net" \
    NEXT_PUBLIC_TASK_URL="https://realtoros-task.azurewebsites.net" \
    NEXT_PUBLIC_EMAIL_URL="https://realtoros-email.azurewebsites.net" \
    NEXT_PUBLIC_ANALYTICS_URL="https://realtoros-analytics.azurewebsites.net" \
    NODE_ENV="production" \
    PORT="3000"
```

### 3. 配置 Docker 部署

```bash
# 启用持续部署（可选，如果使用GitHub Actions）
az webapp deployment container config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --enable-cd true

# 或者手动部署Docker镜像
# 1. 构建并推送到Azure Container Registry
# 2. 配置Web App使用该镜像
```

### 4. 本地构建和测试

```bash
# 进入frontend目录
cd frontend

# 构建Docker镜像
docker build -t realtoros-frontend:latest .

# 本地测试
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8001 \
  -e NEXT_PUBLIC_CRM_URL=http://localhost:8002 \
  realtoros-frontend:latest
```

### 5. 部署到 Azure Container Registry

```bash
# 创建 Azure Container Registry
ACR_NAME="realtorosacr"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# 登录到ACR
az acr login --name $ACR_NAME

# 构建并推送镜像
docker build -t $ACR_NAME.azurecr.io/realtoros-frontend:latest .
docker push $ACR_NAME.azurecr.io/realtoros-frontend:latest

# 配置Web App使用ACR镜像
az webapp config container set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_NAME.azurecr.io/realtoros-frontend:latest \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name $ACR_NAME --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `NEXT_PUBLIC_API_URL` | Auth服务URL | `https://realtoros-auth.azurewebsites.net` |
| `NEXT_PUBLIC_CRM_URL` | CRM服务URL | `https://realtoros-crm.azurewebsites.net` |
| `NEXT_PUBLIC_TASK_URL` | Task服务URL | `https://realtoros-task.azurewebsites.net` |
| `NEXT_PUBLIC_EMAIL_URL` | Email服务URL | `https://realtoros-email.azurewebsites.net` |
| `NEXT_PUBLIC_ANALYTICS_URL` | Analytics服务URL | `https://realtoros-analytics.azurewebsites.net` |
| `PORT` | 监听端口（Azure自动设置） | `3000` |
| `NODE_ENV` | 环境模式 | `production` |

### 端口配置

Azure Web App 会自动设置 `PORT` 环境变量，Next.js会自动使用它。

## 📝 GitHub Actions 自动部署（可选）

创建 `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to Azure Web App

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Azure Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.ACR_LOGIN_SERVER }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ secrets.ACR_LOGIN_SERVER }}/realtoros-frontend:${{ github.sha }}
          build-args: |
            NEXT_PUBLIC_API_URL=${{ secrets.NEXT_PUBLIC_API_URL }}
            NEXT_PUBLIC_CRM_URL=${{ secrets.NEXT_PUBLIC_CRM_URL }}
      
      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## 🔍 验证部署

1. 访问 Web App URL: `https://realtoros-frontend.azurewebsites.net`
2. 检查日志: `az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP`
3. 检查健康状态: `az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP`

## 🐛 故障排查

### 常见问题

1. **构建失败**
   - 检查 Dockerfile 是否正确
   - 检查环境变量是否设置
   - 查看构建日志: `az webapp log tail`

2. **运行时错误**
   - 检查环境变量配置
   - 检查后端服务是否可访问
   - 查看应用日志

3. **端口问题**
   - Azure Web App 自动设置 PORT，无需手动配置
   - 确保 Dockerfile 使用 `PORT` 环境变量

## 📚 参考资源

- [Azure Web App 文档](https://docs.microsoft.com/azure/app-service/)
- [Next.js 部署文档](https://nextjs.org/docs/deployment)
- [Docker 多阶段构建](https://docs.docker.com/build/building/multi-stage/)

