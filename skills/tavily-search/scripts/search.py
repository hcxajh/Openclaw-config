#!/usr/bin/env python3
"""Tavily Web Search CLI"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

def search(query, max_results=5):
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    url = "https://api.tavily.com/search"
    data = json.dumps({
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "include_answer": True,
        "include_raw_content": False,
        "include_images": False
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if result.get("answer"):
        print(f"【摘要】{result['answer']}\n")
    
    for i, r in enumerate(result.get("results", []), 1):
        print(f"{i}. {r.get('title', 'No title')}")
        print(f"   {r.get('url', '')}")
        print(f"   {r.get('content', '')[:200]}...")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tavily Web Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--max-results", type=int, default=5, help="Max results")
    args = parser.parse_args()
    search(args.query, args.max_results)
