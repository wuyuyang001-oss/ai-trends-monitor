#!/usr/bin/env python3
"""
AI Trends Monitor - 监控 GitHub/Reddit/小红书 AI 趋势
为 AI 产品经理提供早期信号
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import urlencode

# 飞书 webhook（需要配置 secrets）
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK', '')
AI_TREND_MONITOR = os.environ.get('AI_TREND_MONITOR', '')

def send_feishu(title, content):
    """发送消息到飞书"""
    if not FEISHU_WEBHOOK:
        print("Warning: FEISHU_WEBHOOK not set")
        return
    
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [[{"tag": "text", "text": content}]]
                }
            }
        }
    }
    
    try:
        requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
    except Exception as e:
        print(f"Send feishu error: {e}")

def fetch_github_trending():
    """获取 GitHub AI 趋势项目"""
    headers = {}
    if AI_TREND_MONITOR:
        headers['Authorization'] = f'token {AI_TREND_MONITOR}'
    
    topics = ['artificial-intelligence', 'machine-learning', 'llm', 'claude', 'openai']
    results = []
    
    for topic in topics[:2]:  # 限制API调用
        url = f'https://api.github.com/search/repositories?q=topic:{topic}+created:>2026-01-01&sort=stars&order=desc&per_page=5'
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('items', []):
                    results.append({
                        'name': item['full_name'],
                        'stars': item['stargazers_count'],
                        'description': item['description'] or 'No description',
                        'url': item['html_url'],
                        'created': item['created_at'][:10]
                    })
        except Exception as e:
            print(f"GitHub API error: {e}")
    
    return results[:5]  # 取前5个

def analyze_for_pm(repo):
    """AI PM 视角分析"""
    analysis = []
    
    # 技术价值
    if 'agent' in repo['description'].lower():
        analysis.append("🎯 **Agent方向**：AI代理是当前热点，可能改变工作流")
    if 'llm' in repo['description'].lower() or 'model' in repo['description'].lower():
        analysis.append("🧠 **模型层创新**：基础模型或微调方案，关注技术突破")
    if 'ui' in repo['description'].lower() or 'interface' in repo['description'].lower():
        analysis.append("🎨 **交互创新**：AI产品界面层创新，用户体验优化")
    
    # 商业机会
    stars = repo['stars']
    if stars > 1000:
        analysis.append(f"🔥 **高关注度**：{stars} stars，社区认可度高，值得深入研究")
    elif stars > 100:
        analysis.append(f"⚡ **早期信号**：{stars} stars，处于爆发前夜，抢先布局")
    
    # 挑战提示
    if 'experimental' in repo['description'].lower():
        analysis.append("⚠️ **实验性质**：技术尚未成熟，商业化需谨慎")
    
    return '\n'.join(analysis) if analysis else "💡 **值得关注**：新技术方向，持续观察"

def generate_report():
    """生成监控报告"""
    report = []
    report.append("📊 AI 趋势监控报告")
    report.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 50)
    
    # GitHub 趋势
    report.append("\n🔥 GitHub AI 热门项目\n")
    github_repos = fetch_github_trending()
    
    for i, repo in enumerate(github_repos, 1):
        report.append(f"{i}. **{repo['name']}** ⭐ {repo['stars']}")
        report.append(f"   描述：{repo['description']}")
        report.append(f"   链接：{repo['url']}")
        report.append(f"   创建：{repo['created']}")
        report.append(f"   \n   📈 PM分析：")
        analysis = analyze_for_pm(repo)
        for line in analysis.split('\n'):
            report.append(f"   {line}")
        report.append("")
    
    return '\n'.join(report)

def main():
    """主函数"""
    print("Starting AI Trends Monitor...")
    
    report = generate_report()
    print(report)
    
    # 保存到文件
    with open(f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.md", 'w') as f:
        f.write(report)
    
    # 发送到飞书
    send_feishu("🔥 AI 趋势日报", report[:3000])  # 限制长度
    
    print("Monitor completed!")

if __name__ == '__main__':
    main()
