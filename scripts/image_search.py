#!/usr/bin/env python3
"""
多平台图片搜索服务
支持 Unsplash, Pexels, Pixabay
"""

import requests
import json
import os
from typing import List, Dict

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')

def load_config():
    """加载API配置"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "unsplash_access_key": "TVJ2ds84O8K3n4szycxdLfam-EEMuaogY7qOqrZZHpA",
        "pexels_api_key": "ckdpM9F4SyjoRVQ9UQRbbVbdiSGbA7dS1gVOgSjVwF4R9rM8fFjuRWYt",
        "pixabay_api_key": "54668136-833728a65f1fadc00c24c410e"
    }

class ImageSearchService:
    """多平台图片搜索服务"""
    
    def __init__(self):
        self.config = load_config()
        self.results = []
        
    def search_unsplash(self, query: str, per_page: int = 5) -> List[Dict]:
        """搜索 Unsplash"""
        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {self.config.get('unsplash_access_key')}"
        }
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = []
                for result in data.get("results", []):
                    images.append({
                        "source": "Unsplash",
                        "url": result["urls"]["regular"],
                        "thumb": result["urls"]["small"],
                        "author": result["user"]["name"],
                        "description": result.get("description", query)
                    })
                return images
        except Exception as e:
            print(f"Unsplash 搜索失败: {e}")
        
        return []
    
    def search_pexels(self, query: str, per_page: int = 5) -> List[Dict]:
        """搜索 Pexels"""
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": self.config.get("pexels_api_key")
        }
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data.get("photos", []):
                    images.append({
                        "source": "Pexels",
                        "url": photo["src"]["large"],
                        "thumb": photo["src"]["medium"],
                        "author": photo["photographer"],
                        "description": photo.get("alt", query)
                    })
                return images
        except Exception as e:
            print(f"Pexels 搜索失败: {e}")
        
        return []
    
    def search_pixabay(self, query: str, per_page: int = 5) -> List[Dict]:
        """搜索 Pixabay"""
        url = "https://pixabay.com/api/"
        params = {
            "key": self.config.get("pixabay_api_key"),
            "q": query,
            "per_page": per_page,
            "orientation": "horizontal",
            "safesearch": "true"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = []
                for hit in data.get("hits", []):
                    images.append({
                        "source": "Pixabay",
                        "url": hit["largeImageURL"],
                        "thumb": hit["webformatURL"],
                        "author": hit["user"],
                        "description": hit.get("tags", query)
                    })
                return images
        except Exception as e:
            print(f"Pixabay 搜索失败: {e}")
        
        return []
    
    def search_all(self, query: str, total_needed: int = 4) -> List[Dict]:
        """聚合搜索所有平台"""
        print(f"\n🖼️  搜索图片: {query}")
        
        all_images = []
        
        # 从各平台获取图片
        unsplash_images = self.search_unsplash(query, per_page=2)
        pexels_images = self.search_pexels(query, per_page=2)
        pixabay_images = self.search_pixabay(query, per_page=2)
        
        # 合并结果并去重
        seen_urls = set()
        for img in unsplash_images + pexels_images + pixabay_images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)
        
        # 返回需要的数量
        return all_images[:total_needed]
    
    def search_for_article(self, topic: str, keywords: List[str]) -> List[Dict]:
        """为一篇文章搜索配图（4张）"""
        print(f"\n📷 为主题 '{topic}' 搜索配图...")
        
        all_images = []
        
        for keyword in keywords[:2]:  # 用前2个关键词搜索
            images = self.search_all(keyword, total_needed=2)
            all_images.extend(images)
            time.sleep(1.2)  # Brave API 延迟限制
        
        return all_images[:4]  # 每篇文章4张图

import time

def main():
    """测试图片搜索"""
    service = ImageSearchService()
    
    # 测试搜索
    query = "Spain Madrid cityscape"
    results = service.search_all(query, total_needed=4)
    
    print(f"\n✅ 找到 {len(results)} 张图片")
    for i, img in enumerate(results, 1):
        print(f"{i}. [{img['source']}] {img['author']}")
        print(f"   URL: {img['url'][:60]}...")

if __name__ == "__main__":
    main()
