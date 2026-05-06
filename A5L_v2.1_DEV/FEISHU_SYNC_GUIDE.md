
# 飞书同步操作指南

## 快速开始

### 方式1: 自动上传（推荐）

1. **创建飞书文件夹结构**
   - 在飞书云空间创建文件夹: `OpenClaw Agent数据归档`
   - 创建子文件夹: 01-SOUL, 02-SKILL, 03-MEMORY, 04-GOAL, 05-DATA

2. **运行同步脚本**
   ```bash
   python3 TOOLS/feishu_cloud_sync.py
   ```

3. **复制到飞书**
   - 脚本会生成所有必要的文件
   - 按提示复制到对应的飞书文件夹

### 方式2: 一键导出所有文件

```bash
# 生成所有导出文件
python3 TOOLS/ssmg_archive_system.py

# 文件位置
ls feishu_export/
# SOUL-2026-05-01.md
# SKILL-2026-05-01.md
# MEMORY-2026-05-01.md
# GOAL-2026-05-01.md
```

## 文件说明

| 文件 | 飞书位置 | 格式 |
|------|----------|------|
| SOUL-*.md | 01-SOUL/ | 文档 |
| SKILL-*.md | 02-SKILL/ | 表格 |
| SKILL-*.csv | 02-SKILL/ | CSV导入 |
| MEMORY-*.md | 03-MEMORY/每日情景记忆/ | 文档 |
| GOAL-*.md | 04-GOAL/ | 文档 |
| DATA-持仓-*.md | 05-DATA/ | 表格 |

## 定时同步

配置每日自动同步:
```bash
# 编辑crontab
crontab -e

# 添加每日23:30执行
0 23 * * * cd /workspace/projects/workspace && python3 TOOLS/feishu_cloud_sync.py >> logs/sync.log 2>&1
```
