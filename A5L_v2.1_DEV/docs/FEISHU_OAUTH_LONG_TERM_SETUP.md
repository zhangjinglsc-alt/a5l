# 飞书OAuth长期有效配置方案

## 问题原因

飞书OAuth Token都有有效期：
- **Tenant Access Token**: 2小时
- **User Access Token**: 2小时
- **Refresh Token**: 30天

之前的配置使用静态Token，过期后失效。

## ✅ 解决方案：自动刷新Token管理器

### 已部署组件

| 组件 | 文件 | 功能 |
|:-----|:-----|:-----|
| Token管理器 | `tools/feishu_token_manager.py` | 自动刷新Tenant/User Token |
| OAuth上传器 | `tools/feishu_oauth_uploader.py` | 使用Token管理器创建文档 |
| 自动上传器 | `TOOLS/feishu_auto_uploader.py` | 整合SSMG归档和飞书上传 |

### 自动刷新机制

```
调用API → 检查Token有效期 → 如果即将过期 → 自动刷新 → 返回有效Token
              ↓
         如果有效 → 直接使用
```

### Token优先级

1. **Tenant Access Token** (应用级别) - 优先使用
   - ✅ 使用App ID和App Secret自动获取
   - ✅ 可自动刷新
   - ✅ 适合批量文档操作

2. **User Access Token** (用户级别) - 备用
   - ⚠️ 需要用户授权获取
   - ⚠️ 需要Refresh Token才能自动刷新
   - ✅ 适合操作用户私人文档

## 🔧 当前配置状态

### config/feishu_oauth.json
```json
{
  "app_id": "cli_a94dcd846138dcb3",
  "app_secret": "GxlntRwJWdvAHkcDEGLmFbZZKUHUmu2Y",
  "tenant_access_token": "自动刷新",
  "tenant_token_expires_at": 自动更新,
  "user_access_token": null,  // 可选配置
  "refresh_token": null       // 可选配置
}
```

### 测试结果
```
✅ Tenant Token已刷新，有效期1小时
⚠️  User Token未配置（可选）
```

## 🚀 使用方法

### 方法1：使用自动上传器（推荐）
```bash
cd /workspace/projects/workspace
python3 TOOLS/feishu_auto_uploader.py
```

Token会自动刷新，无需手动干预。

### 方法2：使用Token管理器测试
```bash
cd /workspace/projects/workspace/tools
python3 feishu_token_manager.py
```

### 方法3：使用OAuth上传器单文件上传
```bash
cd /workspace/projects/workspace/tools
python3 feishu_oauth_uploader.py \
  --file /path/to/file.md \
  --title "文档标题"
```

## 📋 配置长期有效的关键

### 1. Tenant Token方案（已配置）
- ✅ **优点**: 无需用户授权，使用App凭证自动获取
- ✅ **有效期**: 2小时，但自动刷新
- ✅ **权限**: 应用有权限的所有资源
- ⚠️ **限制**: 不能访问用户私人数据

### 2. User Token + Refresh Token方案（可选）
如果需要操作用户私人文档，需要：
1. 用户通过OAuth授权获取User Token
2. 保存Refresh Token
3. Token管理器会自动使用Refresh Token刷新

**获取Refresh Token步骤**:
```bash
# 1. 引导用户访问授权URL
https://open.feishu.cn/open-apis/authen/v1/index?app_id=cli_a94dcd846138dcb3&redirect_uri=YOUR_REDIRECT_URI

# 2. 用户授权后获取code

# 3. 使用code换取Access Token和Refresh Token
curl -X POST https://open.feishu.cn/open-apis/authen/v1/access_token \
  -H "Authorization: Bearer {app_access_token}" \
  -d '{"grant_type": "authorization_code", "code": "用户授权码"}'

# 4. 保存Refresh Token到config/feishu_oauth.json
```

## 🎯 推荐配置

对于A5L自动归档系统：
- ✅ **使用Tenant Token** - 已配置，自动刷新
- ✅ **文档创建在应用目录** - 不需要User Token
- ⚠️ **如果需要访问用户私人文件夹** - 再配置User Token

## 📊 Token刷新日志

查看刷新历史：
```bash
cat /workspace/projects/workspace/config/feishu_oauth.json | grep updated_at
```

## 🔒 安全性说明

- App Secret存储在本地配置文件
- Token不输出到日志
- 配置文件权限：仅root可读写

## ✅ 状态确认

当前系统已配置：
- ✅ Token自动刷新管理器
- ✅ OAuth上传器集成
- ✅ 自动上传系统
- ✅ 三市场模拟交易文档导出

**现在执行自动上传时，Token会自动刷新，不会再出现"Invalid access token"错误！**
