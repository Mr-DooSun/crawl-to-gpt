from urllib.parse import urlsplit

def normalize_url(url: str) -> str:
    """URL에서 fragment 제거 + trailing slash 정리."""
    split_url = urlsplit(url)._replace(fragment="")
    path = split_url.path.rstrip("/") or "/"  # `/`만 남을 경우 유지
    return split_url._replace(path=path).geturl()

def clean_fragment_and_slash_links(input_file: str, output_file: str) -> None:
    clean_links = set()

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            clean_url = normalize_url(url)
            clean_links.add(clean_url)

    with open(output_file, "w", encoding="utf-8") as f:
        for link in sorted(clean_links):
            f.write(link + "\n")

    print(f"✅ 정리된 {len(clean_links)}개 링크가 {output_file}에 저장되었습니다.")


# 실행
clean_fragment_and_slash_links("reflex_links.txt", "reflex_links_cleaned.txt")
