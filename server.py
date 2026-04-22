from mcp.server.fastmcp import FastMCP
import steam_client as steam

mcp = FastMCP("steam-game-server")


@mcp.tool()
async def search_games(query: str, count: int = 10) -> list[dict]:
    """게임 이름으로 Steam 게임을 검색합니다."""
    return await steam.search_games(query, count)


@mcp.tool()
async def get_game_info(app_id: int) -> dict:
    """Steam App ID로 게임의 상세 정보를 조회합니다 (장르, 가격, 리뷰 수 등)."""
    return await steam.get_game_info(app_id)


@mcp.tool()
async def get_game_news(app_id: int, count: int = 5) -> list[dict]:
    """특정 게임의 최신 뉴스/패치노트를 가져옵니다."""
    return await steam.get_game_news(app_id, count)


@mcp.tool()
async def get_featured_games() -> dict:
    """Steam 메인 페이지의 추천/특별 할인 게임 목록을 가져옵니다."""
    return await steam.get_featured_games()


@mcp.tool()
async def get_top_sellers() -> list[dict]:
    """Steam 실시간 판매 상위 게임 목록을 가져옵니다."""
    return await steam.get_top_sellers()


@mcp.tool()
async def get_new_releases() -> list[dict]:
    """Steam 최신 출시 게임 목록을 가져옵니다."""
    return await steam.get_new_releases()


@mcp.tool()
async def get_most_played() -> list[dict]:
    """현재 Steam에서 동시 접속자가 가장 많은 게임 Top 10을 가져옵니다."""
    return await steam.get_most_played()


@mcp.tool()
async def get_trending_games() -> list[dict]:
    """최근 2주 동안 Steam에서 가장 뜨고 있는 트렌딩 게임을 가져옵니다 (SteamSpy 기준)."""
    return await steam.get_trending_games()


if __name__ == "__main__":
    import os
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    port = int(os.getenv("PORT", 8000))

    if transport == "streamable-http":
        # 배포 환경 (Render 등) — uvicorn으로 직접 실행
        import uvicorn
        app = mcp.streamable_http_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # 로컬 환경 (Claude Code stdio)
        mcp.run()
