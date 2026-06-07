"""
Sentiment Analyzer MCP Server - Hacker News Edition
Target audience: Developers who pay for tools
"""

from textblob import TextBlob
import json
import requests
from typing import Dict, Any, List

# ============================================================
# TOOL DEFINITIONS - What AI agents can call
# ============================================================

TOOLS = [
    {
        "name": "analyze_sentiment",
        "description": "Analyze sentiment of any text. Returns positive/negative/neutral with confidence score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "analyze_hackernews_sentiment",
        "description": "Analyze sentiment of Hacker News posts about a topic. Perfect for developer sentiment and tech trends.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to search (e.g., 'LangChain', 'OpenAI', 'Rust')"},
                "limit": {"type": "integer", "description": "Number of posts to analyze", "default": 20}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "compare_topic_sentiment",
        "description": "Compare sentiment across multiple topics on Hacker News. Great for competitive analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topics": {"type": "array", "items": {"type": "string"}, "description": "List of topics to compare"},
                "limit_per_topic": {"type": "integer", "description": "Posts per topic", "default": 15}
            },
            "required": ["topics"]
        }
    }
]

# ============================================================
# CORE SENTIMENT FUNCTION
# ============================================================

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Core sentiment analysis - your money maker"""
    if not text or len(text.strip()) == 0:
        return {"error": "Text is empty", "sentiment_label": "neutral", "sentiment_score": 0}
    
    blob = TextBlob(text[:500])
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "sentiment_score": round(polarity, 3),
        "sentiment_label": label,
        "confidence": round(abs(polarity) * 100, 1)
    }

# ============================================================
# HACKER NEWS - Your revenue driver
# ============================================================

def search_hackernews(topic: str, limit: int = 20) -> List[Dict]:
    """Search Hacker News using Algolia API - FREE, no key needed"""
    url = f"https://hn.algolia.com/api/v1/search"
    params = {"query": topic, "hitsPerPage": min(limit, 50), "tags": "story"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for hit in data.get('hits', []):
            results.append({
                "title": hit.get('title', ''),
                "url": hit.get('url', ''),
                "points": hit.get('points', 0),
                "num_comments": hit.get('num_comments', 0),
                "author": hit.get('author', ''),
                "created_at": hit.get('created_at', '')
            })
        return results
    except Exception as e:
        return []

def analyze_hackernews_sentiment(topic: str, limit: int = 20) -> Dict[str, Any]:
    """Analyze HN sentiment - PRO feature worth $29/month"""
    posts = search_hackernews(topic, limit)
    
    if not posts:
        return {"topic": topic, "error": "No posts found", "total_analyzed": 0}
    
    results = []
    for post in posts:
        text_to_analyze = f"{post['title']}"
        sentiment = analyze_sentiment(text_to_analyze)
        results.append({
            "title": post['title'][:80],
            "points": post['points'],
            "comments": post['num_comments'],
            "sentiment": sentiment['sentiment_label'],
            "score": sentiment['sentiment_score']
        })
    
    positive = [r for r in results if r['sentiment'] == 'positive']
    negative = [r for r in results if r['sentiment'] == 'negative']
    
    avg_score = sum(r['score'] for r in results) / len(results)
    
    # Sort by engagement for top posts
    top_posts = sorted(results, key=lambda x: x['points'] + (x['comments'] * 10), reverse=True)[:5]
    
    return {
        "topic": topic,
        "total_analyzed": len(results),
        "positive_count": len(positive),
        "negative_count": len(negative),
        "positive_percentage": round(len(positive) / len(results) * 100, 1),
        "average_sentiment_score": round(avg_score, 3),
        "verdict": "bullish" if avg_score > 0.1 else "bearish" if avg_score < -0.1 else "neutral",
        "top_posts": top_posts
    }

def compare_topic_sentiment(topics: List[str], limit_per_topic: int = 15) -> Dict[str, Any]:
    """Compare sentiment across topics - Enterprise feature"""
    results = []
    for topic in topics:
        data = analyze_hackernews_sentiment(topic, limit_per_topic)
        if "error" not in data:
            results.append({
                "topic": topic,
                "average_score": data['average_sentiment_score'],
                "positive_percentage": data['positive_percentage'],
                "verdict": data['verdict']
            })
    
    if not results:
        return {"error": "No data found"}
    
    results.sort(key=lambda x: x['average_score'], reverse=True)
    
    return {
        "comparison": results,
        "most_positive": results[0]['topic'],
        "most_negative": results[-1]['topic'],
        "summary": f"'{results[0]['topic']}' has the most positive developer sentiment ({results[0]['positive_percentage']}% positive)."
    }

# ============================================================
# MCP HANDLER
# ============================================================

def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    if tool_name == "analyze_sentiment":
        text = arguments.get("text", "")
        return analyze_sentiment(text)
    
    elif tool_name == "analyze_hackernews_sentiment":
        topic = arguments.get("topic", "")
        limit = arguments.get("limit", 20)
        return analyze_hackernews_sentiment(topic, limit)
    
    elif tool_name == "compare_topic_sentiment":
        topics = arguments.get("topics", [])
        limit = arguments.get("limit_per_topic", 15)
        return compare_topic_sentiment(topics, limit)
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}

# ============================================================
# TEST (run with: python server.py)
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Revenue-Focused Sentiment Analyzer\n")
    
    print("1. analyze_sentiment:")
    print(analyze_sentiment("Claude is amazing for building MCP servers!"))
    
    print("\n2. analyze_hackernews_sentiment for 'MCP':")
    print(analyze_hackernews_sentiment("MCP", 10))
    
    print("\n3. compare_topic_sentiment:") 
    print(compare_topic_sentiment(["OpenAI", "Anthropic", "Google"]))