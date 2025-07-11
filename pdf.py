import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from fpdf import FPDF

TXT_FILE = "reflex_links.txt"
PDF_FILE = "reflex_docs.pdf"

def normalize_url(url: str) -> str:
    """Fragment 제거 및 trailing slash 제거."""
    url = urlsplit(url)._replace(fragment="").geturl()
    return url.rstrip("/")

def extract_text_from_xpath(soup: BeautifulSoup) -> str:
    """BeautifulSoup 기반으로 XPath 위치의 텍스트 추출."""
    try:
        # XPath: /html/body/div/div[3]/main/div[2]/div[2]/article
        container = soup.select_one("body > div > div:nth-of-type(3) > main > div:nth-of-type(2) > div:nth-of-type(2) > article")
        return container.get_text(separator="\n", strip=True) if container else ""
    except Exception:
        return ""

def load_links_from_txt(txt_path: str) -> list[str]:
    with open(txt_path, encoding="utf-8") as f:
        return sorted(set(normalize_url(line.strip()) for line in f if line.strip()))

def fetch_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        return extract_text_from_xpath(soup)
    except requests.RequestException:
        print(f"❌ 요청 실패: {url}")
    except Exception:
        print(f"⚠️ 파싱 실패: {url}")
    return ""

def save_to_pdf(texts: list[tuple[str, str]], filename: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for title, content in texts:
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=14)
        pdf.multi_cell(0, 10, title)
        pdf.ln(2)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, content or "[No content found]")

    pdf.output(filename)
    print(f"✅ PDF 저장 완료: {filename}")

if __name__ == "__main__":
    urls = load_links_from_txt(TXT_FILE)
    results = []

    for idx, url in enumerate(urls, start=1):
        print(f"[{idx}/{len(urls)}] 크롤링 중: {url}")
        text = fetch_text_from_url(url)
        if text:
            results.append((url, text))

    save_to_pdf(results, PDF_FILE)
