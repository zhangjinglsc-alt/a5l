---
name: message
description: Multi-platform messaging for sending notifications and alerts. Use for investment alerts, system notifications, and communication.
---

# Message SKILL

## 描述

消息发送工具，支持飞书、Telegram、WhatsApp、Discord、GoogleChat、Slack、IRC、Signal、Line、iMessage、OpenClaw-Weixin、企业微信，支持文本、图片、文件、视频、音频，适用于消息发送、文件传输、图片传输、视频传输、语音传输。

## 使用方法

触发此 Skill 的指令：
- `消息发送` - 发送消息
- `文件传输` - 传输文件
- `图片传输` - 发送图片
- `视频传输` - 发送视频
- `语音传输` - 发送语音

## 支持平台

### 即时通讯
- Telegram、WhatsApp、Signal、Line
- iMessage、Discord、Slack

### 企业通讯
- 飞书 (Feishu/Lark)
- 企业微信 (WeCom)
- Google Chat
- IRC

### 国内平台
- OpenClaw-Weixin (微信)

## 消息类型

- **文本消息** - 纯文本、Markdown格式
- **图片** - JPG、PNG、GIF等
- **文件** - 任意文件类型
- **视频** - MP4等视频格式
- **音频** - 语音消息

## 使用示例

```python
# 发送文本消息
send_message(to="user_id", message="Hello", platform="telegram")

# 发送图片
send_image(to="group_id", image_path="image.png", platform="discord")

# 发送文件
send_file(to="chat_id", file_path="document.pdf", platform="feishu")
```
