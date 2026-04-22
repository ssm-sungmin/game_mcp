import os
import httpx
from dotenv import load_dotenv

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
STORE_API = "https://store.steampowered.com/api"
WEB_API = "https://api.steampowered.com"
STEAMSPY_API = "https://steamspy.com/api.php"


async def _get(url: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def search_games(query: str, count: int = 10) -> list[dict]:
    data = await _get(f"{STORE_API}/storesearch/", {
        "term": query,
        "l": "korean",
        "cc": "KR",
    })
    items = data.get("items", [])[:count]
    return [
        {
            "app_id": item["id"],
            "name": item["name"],
            "price": item.get("price", {}).get("final_formatted", "무료 또는 정보 없음"),
            "platforms": item.get("platforms", {}),
        }
        for item in items
    ]


async def get_game_info(app_id: int) -> dict:
    data = await _get(f"{STORE_API}/appdetails", {
        "appids": app_id,
        "l": "korean",
        "cc": "KR",
    })
    app_data = data.get(str(app_id), {})
    if not app_data.get("success"):
        return {"error": f"앱 ID {app_id}에 대한 정보를 찾을 수 없습니다."}

    d = app_data["data"]
    return {
        "app_id": app_id,
        "name": d.get("name"),
        "type": d.get("type"),
        "short_description": d.get("short_description"),
        "developers": d.get("developers", []),
        "publishers": d.get("publishers", []),
        "price": d.get("price_overview", {}).get("final_formatted", "무료"),
        "release_date": d.get("release_date", {}).get("date"),
        "genres": [g["description"] for g in d.get("genres", [])],
        "categories": [c["description"] for c in d.get("categories", [])],
        "platforms": d.get("platforms", {}),
        "metacritic": d.get("metacritic", {}).get("score"),
        "recommendations": d.get("recommendations", {}).get("total"),
        "header_image": d.get("header_image"),
        "store_url": f"https://store.steampowered.com/app/{app_id}",
    }


async def get_game_news(app_id: int, count: int = 5) -> list[dict]:
    data = await _get(f"{WEB_API}/ISteamNews/GetNewsForApp/v0002/", {
        "appid": app_id,
        "count": count,
        "maxlength": 500,
        "format": "json",
    })
    news_items = data.get("appnews", {}).get("newsitems", [])
    return [
        {
            "title": item["title"],
            "url": item["url"],
            "author": item.get("author", ""),
            "date": item["date"],
            "contents": item.get("contents", "")[:300] + "...",
            "feed_name": item.get("feedname", ""),
        }
        for item in news_items
    ]


async def get_featured_games() -> dict:
    data = await _get(f"{STORE_API}/featured/", {"cc": "KR", "l": "korean"})
    def extract(items):
        return [
            {
                "app_id": item["id"],
                "name": item["name"],
                "discounted": item.get("discounted", False),
                "discount_percent": item.get("discount_percent", 0),
                "original_price": item.get("original_price", 0) / 100 if item.get("original_price") else None,
                "final_price": item.get("final_price", 0) / 100 if item.get("final_price") else None,
                "header_image": item.get("header_image"),
            }
            for item in items
        ]
    return {
        "large_capsules": extract(data.get("large_capsules", [])),
        "featured_win": extract(data.get("featured_win", [])[:5]),
    }


async def get_top_sellers() -> list[dict]:
    data = await _get(f"{STORE_API}/featuredcategories/", {"cc": "KR", "l": "korean"})
    items = data.get("top_sellers", {}).get("items", [])
    return [
        {
            "app_id": item["id"],
            "name": item["name"],
            "discounted": item.get("discounted", False),
            "discount_percent": item.get("discount_percent", 0),
            "final_price": item.get("final_price", 0) / 100 if item.get("final_price") else None,
            "header_image": item.get("header_image"),
        }
        for item in items[:10]
    ]


async def get_new_releases() -> list[dict]:
    data = await _get(f"{STORE_API}/featuredcategories/", {"cc": "KR", "l": "korean"})
    items = data.get("new_releases", {}).get("items", [])
    return [
        {
            "app_id": item["id"],
            "name": item["name"],
            "discounted": item.get("discounted", False),
            "discount_percent": item.get("discount_percent", 0),
            "final_price": item.get("final_price", 0) / 100 if item.get("final_price") else None,
            "header_image": item.get("header_image"),
        }
        for item in items[:10]
    ]


async def get_most_played() -> list[dict]:
    data = await _get(f"{WEB_API}/ISteamChartsService/GetMostPlayedGames/v1/")
    ranks = data.get("response", {}).get("ranks", [])
    return [
        {
            "rank": item["rank"],
            "app_id": item["appid"],
            "peak_in_game": item.get("peak_in_game"),
            "store_url": f"https://store.steampowered.com/app/{item['appid']}",
        }
        for item in ranks[:10]
    ]


async def get_trending_games() -> list[dict]:
    data = await _get(STEAMSPY_API, {"request": "top100in2weeks"})
    top = sorted(data.values(), key=lambda x: x.get("positive", 0), reverse=True)[:10]
    return [
        {
            "app_id": item["appid"],
            "name": item["name"],
            "developer": item.get("developer", ""),
            "publisher": item.get("publisher", ""),
            "positive_reviews": item.get("positive", 0),
            "negative_reviews": item.get("negative", 0),
            "owners": item.get("owners", ""),
            "store_url": f"https://store.steampowered.com/app/{item['appid']}",
        }
        for item in top
    ]
