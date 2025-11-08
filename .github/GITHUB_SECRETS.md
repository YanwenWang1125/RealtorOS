# GitHub Secrets 配置指南

本文档说明在 GitHub Actions 中需要配置的 Secrets 和环境变量。

## 📋 必需的 GitHub Secrets

### 部署相关（必需）

这些 Secrets 用于部署到 Azure：

| Secret 名称 | 描述 | 示例 | 必需 |
|------------|------|------|------|
| `AZURE_CREDENTIALS` | Azure 服务主体凭据（JSON 格式） | `{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"..."}` | ✅ |
| `ACR_NAME` | Azure Container Registry 名称 | `realtorosacr12345` | ✅ |
| `ACR_USERNAME` | ACR 用户名 | `realtorosacr12345` | ✅ |
| `ACR_PASSWORD` | ACR 密码 | `...` | ✅ |
| `NEXT_PUBLIC_API_URL` | 前端 API URL（用于构建时） | `https://realtoros-backend.eastus.azurecontainerapps.io` | ✅ |
| `DB_PASSWORD` | PostgreSQL 数据库管理员密码（至少 8 个字符） | `SecurePass123!` | ✅ |

### 后端应用配置（部署时必需）

这些 Secrets 用于配置后端容器应用的环境变量：

| Secret 名称 | 描述 | 示例 | 必需 |
|------------|------|------|------|
| `DATABASE_URL` | PostgreSQL 数据库连接字符串（如果未设置，将自动从 `DB_PASSWORD` 构建） | `postgresql+asyncpg://user:pass@host:5432/db` | ⚠️ 可选* |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` | ✅ |
| `OPENAI_MODEL` | OpenAI 模型名称 | `gpt-4` | ✅ |
| `AWS_REGION` | AWS 区域 | `us-east-1` | ✅ |
| `SES_FROM_EMAIL` | AWS SES 发件人邮箱（必须已验证） | `agent@example.com` | ✅ |
| `AWS_ACCESS_KEY_ID` | AWS 访问密钥 ID | `AKIA...` | ✅ |
| `AWS_SECRET_ACCESS_KEY` | AWS 密钥 | `...` | ✅ |
| `SECRET_KEY` | JWT 签名密钥（至少 32 字符） | `...` | ✅ |
| `CORS_ORIGINS` | 允许的 CORS 源（逗号分隔） | `https://realtoros-frontend.eastus.azurecontainerapps.io` | ✅ |

### 测试相关（可选，但推荐）

这些 Secrets 用于测试环境。如果不设置，工作流会使用默认测试值：

| Secret 名称 | 描述 | 默认值 | 必需 |
|------------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥（用于真实 API 测试） | `test-key` | ❌ |
| `OPENAI_MODEL` | OpenAI 模型名称 | `gpt-4` | ❌ |
| `AWS_REGION` | AWS 区域 | `us-east-1` | ❌ |
| `SES_FROM_EMAIL` | SES 发件人邮箱 | `test@example.com` | ❌ |
| `AWS_ACCESS_KEY_ID` | AWS 访问密钥 ID | `test-key` | ❌ |
| `AWS_SECRET_ACCESS_KEY` | AWS 密钥 | `test-secret` | ❌ |
| `TEST_SECRET_KEY` | 测试用密钥（至少 32 字符） | `test-secret-key-minimum-32-characters-long` | ❌ |

## 🔧 如何设置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 输入 Secret 名称和值
5. 点击 **Add secret**

## 📝 环境变量说明

### 测试环境变量（自动设置）

以下环境变量在测试作业中**自动设置**，无需在 Secrets 中配置：

- `ENVIRONMENT=test`
- `DEBUG=true`
- `API_TITLE=RealtorOS API`
- `API_VERSION=1.0.0`
- `DATABASE_URL=sqlite+aiosqlite:///:memory:` (测试使用内存数据库)
- `OPENAI_MAX_TOKENS=2000`
- `LOG_LEVEL=INFO`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `CORS_ORIGINS=http://localhost:3000`

### 工作流行为

- **如果设置了 Secrets**：工作流会使用 Secrets 中的真实值
- **如果未设置 Secrets**：工作流会使用默认测试值（不会调用真实 API）

## ⚠️ 重要提示

1. **测试环境**：默认使用内存 SQLite 数据库，不会影响生产数据
2. **API 密钥**：如果不需要测试真实 API，可以不设置 `OPENAI_API_KEY` 和 AWS 相关密钥
3. **安全性**：所有 Secrets 都会被加密存储，不会在日志中显示
4. **数据库配置**：
   - 如果设置了 `DATABASE_URL`，工作流将使用该值
   - 如果未设置 `DATABASE_URL`，工作流将自动创建 PostgreSQL 服务器并使用 `DB_PASSWORD` 构建连接字符串
   - **首次部署**：必须设置 `DB_PASSWORD`，工作流会自动创建数据库服务器
   - **后续部署**：可以继续使用 `DB_PASSWORD` 或直接设置 `DATABASE_URL`
5. **最小配置**：至少需要设置部署相关的 6 个 Secrets（包括 `DB_PASSWORD`）才能完成首次部署

## 🚀 快速开始

### 最小配置（仅部署）

需要设置以下 Secrets：

**Azure 部署（6个）：**
- `AZURE_CREDENTIALS`
- `ACR_NAME`
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `NEXT_PUBLIC_API_URL`
- `DB_PASSWORD` ⭐ **新增：用于自动创建数据库**

**后端应用配置（9个）：**
- `DATABASE_URL`（可选，如果未设置将自动构建）
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `AWS_REGION`
- `SES_FROM_EMAIL`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SECRET_KEY`
- `CORS_ORIGINS`

**总计：15 个必需的 Secrets**（如果使用自动数据库创建）

### 完整配置（包含测试）

设置所有 Secrets 以获得完整的 CI/CD 功能。

## 📚 相关文档

- [GitHub Actions 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure 服务主体创建指南](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)

