import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
from collections import deque

def normalize_url(url: str) -> str:
    """URL에서 fragment 제거 및 trailing slash 정리."""
    split_url = urlsplit(url)._replace(fragment="")
    path = split_url.path.rstrip("/") or "/"  # 루트는 유지
    return split_url._replace(path=path).geturl()

def is_valid_link(base_domain: str, url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc == base_domain and parsed.path.startswith("/docs")

def crawl_links_bfs(start_url: str) -> set[str]:
    visited = set()
    queue = deque([start_url])
    base_domain = urlparse(start_url).netloc

    while queue:
        current_url = queue.popleft()
        norm_current = normalize_url(current_url)
        if norm_current in visited:
            continue
        visited.add(norm_current)
        print(f"📄 방문 중: {norm_current}")

        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ 요청 실패: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(current_url, href)
            norm_url = normalize_url(full_url)
            if is_valid_link(base_domain, norm_url) and norm_url not in visited:
                queue.append(norm_url)

    return visited

def save_links_to_txt(links: set[str], filename: str = "reflex_links.txt") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")

if __name__ == "__main__":
    start = "https://reflex.dev/docs/getting-started/introduction"
    found_links = crawl_links_bfs(start)

    print(f"\n🔗 총 {len(found_links)}개 링크 수집됨")
    save_links_to_txt(found_links, "reflex_links.txt")
    print("✅ 링크 목록이 reflex_links.txt에 저장되었습니다.")
