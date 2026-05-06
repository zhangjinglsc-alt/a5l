#!/usr/bin/env python3
"""
A5L Tavily Search 集成模块
提供统一的搜索接口供A5L所有Skill调用
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace/skills/tavily/scripts')

def tavily_search(query: str, 
                  search_depth: str = "basic",
                  topic: str = "general", 
                  max_results: int = 5,
                  include_answer: bool = True,
                  include_images: bool = False) -> dict:
    """
    Tavily AI搜索 - A5L统一接口
    
    Args:
        query: 搜索查询
        search_depth: "basic"(快速) 或 "advanced"(深度)
        topic: "general"(通用) 或 "news"(新闻)
        max_results: 返回结果数量 (1-10)
        include_answer: 是否包含AI生成的答案
        include_images: 是否包含图片
    
    Returns:
        dict: 搜索结果
    """
    from tavily_search import search
    
    # 从环境变量获取API Key
    api_key = os.environ.get('TAVILY_API_KEY')
    
    if not api_key:
        return {
            "error": "TAVILY_API_KEY not set",
            "message": "请设置环境变量 TAVILY_API_KEY=tvly-xxx"
        }
    
    try:
        result = search(
            query=query,
            api_key=api_key,
            search_depth=search_depth,
            topic=topic,
            max_results=max_results,
            include_answer=include_answer,
            include_images=include_images
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }


def tavily_news(query: str, max_results: int = 10) -> dict:
    """
    Tavily新闻搜索 - 获取最新新闻
    
    Args:
        query: 新闻搜索关键词
        max_results: 返回结果数量
    
    Returns:
        dict: 新闻搜索结果
    """
    return tavily_search(
        query=query,
        topic="news",
        search_depth="advanced",
        max_results=max_results,
        include_answer=True
    )


def tavily_research(query: str, max_results: int = 10) -> dict:
    """
    Tavily深度研究 - 全面的研究分析
    
    Args:
        query: 研究主题
        max_results: 返回结果数量
    
    Returns:
        dict: 深度研究结果
    """
    return tavily_search(
        query=query,
        search_depth="advanced",
        topic="general",
        max_results=max_results,
        include_answer=True,
        include_images=True
    )


# 测试函数
if __name__ == "__main__":
    import json
    # 测试基础搜索
    print("=" * 70)
    print("🧪 测试 Tavily 搜索")
    print("=" * 70)
    
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        print("\n⚠️  TAVILY_API_KEY 未设置")
        print("请设置环境变量: export TAVILY_API_KEY=tvly-xxx")
        print("获取API Key: https://tavily.com")
    else:
        print(f"\n✅ API Key 已设置: {api_key[:10]}...")
        print("\n测试搜索: 'AI investing trends 2026'")
        result = tavily_search("AI investing trends 2026", max_results=3)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        print("\n... (truncated)")
