---
name: agent-browser
description: Browser automation for web interaction, form filling, and data extraction. Use for automated web testing, scraping, and web-based workflows.
---

# Agent Browser SKILL

## 描述

浏览器自动化CLI，用于网页交互、表单填写、按钮点击、截图、数据抓取、测试web应用，适用于网页交互、爬虫、数据抓取、测试自动化。

## 使用方法

触发此 Skill 的指令：
- `浏览器` - 启动浏览器自动化
- `网页自动化` - 自动化网页操作
- `爬虫` - 爬取网页数据
- `数据抓取` - 抓取网页数据
- `测试自动化` - 自动化测试

## 功能

### 网页导航
- 打开URL
- 前进/后退
- 刷新页面
- 切换标签页

### 元素操作
- 点击元素
- 输入文本
- 选择下拉框
- 上传文件

### 数据提取
- 获取元素文本
- 获取属性值
- 提取表格数据
- 截图保存

### 等待机制
- 等待元素出现
- 等待页面加载
- 设置超时
- 自定义等待条件

## 使用示例

```python
# 打开网页
browser.open("https://example.com")

# 点击按钮
browser.click("#submit-button")

# 输入文本
browser.type("#search-box", "query")

# 获取数据
data = browser.get_text(".result")

# 截图
browser.screenshot("result.png")
```
