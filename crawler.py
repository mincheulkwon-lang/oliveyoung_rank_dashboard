import re
import time
from zoneinfo import ZoneInfo

from datetime import datetime
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

from config import (
    CATEGORIES,
    RANKING_URL,
    SELECTORS,
    HEADLESS,
    REQUEST_DELAY_SECONDS,
    PAGE_WAIT_SECONDS,
    MAX_PRODUCTS_PER_CATEGORY,
)

from database import (
    init_db,
    insert_rankings,
    insert_log
)


def clean_number(text):
    if not text:
        return None

    numbers = re.sub(r"[^0-9]", "", str(text))

    if numbers == "":
        return None

    return int(numbers)


def extract_goods_no(url):
    if not url:
        return None

    match = re.search(r"goodsNo=([A-Z0-9]+)", url)

    if not match:
        return None

    return match.group(1)


def calculate_discount_rate(normal_price, sale_price):
    if not normal_price or not sale_price:
        return ""

    if normal_price <= sale_price:
        return ""

    rate = round(
        (normal_price - sale_price) / normal_price * 100
    )

    return f"{rate}%"


def get_text_safe(element, selector):
    try:
        target = element.query_selector(selector)

        if target:
            return target.inner_text().strip()

    except Exception:
        pass

    return None


def get_link_safe(element, selector):
    try:
        target = element.query_selector(selector)

        if target:
            href = target.get_attribute("href")

            if href:
                return urljoin(
                    "https://www.oliveyoung.co.kr",
                    href
                )

    except Exception:
        pass

    return None


def parse_product_item(element, rank, category_name):
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    product_url = get_link_safe(
        element,
        SELECTORS["product_link"]
    )

    goods_no = extract_goods_no(product_url)

    brand_name = get_text_safe(
        element,
        SELECTORS["brand"]
    )

    product_name = get_text_safe(
        element,
        SELECTORS["product_name"]
    )

    normal_price = clean_number(
        get_text_safe(
            element,
            SELECTORS["normal_price"]
        )
    )

    sale_price = clean_number(
        get_text_safe(
            element,
            SELECTORS["sale_price"]
        )
    )

    discount_rate = get_text_safe(
        element,
        SELECTORS["discount_rate"]
    )

    if not discount_rate:
        discount_rate = calculate_discount_rate(
            normal_price,
            sale_price
        )

    return {
        "collected_date": now.strftime("%Y-%m-%d"),
        "collected_time": now.strftime("%H:%M:%S"),
        "category_name": category_name,
        "rank": rank,
        "brand_name": brand_name or "",
        "product_name": product_name or "",
        "goods_no": goods_no or "",
        "normal_price": normal_price,
        "sale_price": sale_price,
        "discount_rate": discount_rate or "",
        "product_url": product_url or "",
    }


def open_ranking_page(page):
    page.goto(
        RANKING_URL,
        wait_until="domcontentloaded",
        timeout=90000
    )

    page.wait_for_timeout(
        PAGE_WAIT_SECONDS * 1000
    )


def click_category(page, category_name):
    """
    올리브영 랭킹 페이지에서 카테고리명을 클릭합니다.

    같은 카테고리명이 여러 개 잡히는 경우가 있어,
    button → a → text 순서로 첫 번째 요소를 클릭합니다.
    """

    if category_name == "전체":
        return True

    click_candidates = [
        f'button:has-text("{category_name}")',
        f'a:has-text("{category_name}")',
        f'text="{category_name}"',
    ]

    for selector in click_candidates:
        try:
            locator = page.locator(selector)

            if locator.count() == 0:
                continue

            target = locator.first

            target.click(timeout=10000)

            page.wait_for_timeout(
                PAGE_WAIT_SECONDS * 1000
            )

            print(f"[카테고리 클릭 성공] {category_name} / {selector}")

            return True

        except Exception as e:
            print(f"[클릭 후보 실패] {category_name} / {selector} / {e}")

    print(f"[카테고리 클릭 최종 실패] {category_name}")

    insert_log(
        category_name,
        "ERROR",
        "카테고리 클릭 실패"
    )

    return False
    """
    올리브영 랭킹 페이지에서 카테고리명을 직접 클릭합니다.
    URL을 직접 관리하지 않기 위한 함수입니다.
    """

    if category_name == "전체":
        return True

    try:
        # 카테고리 표 안의 텍스트를 기준으로 클릭합니다.
        page.get_by_text(
            category_name,
            exact=True
        ).click(
            timeout=10000
        )

        page.wait_for_timeout(
            PAGE_WAIT_SECONDS * 1000
        )

        return True

    except Exception as e:
        print(f"[카테고리 클릭 실패] {category_name}: {e}")

        insert_log(
            category_name,
            "ERROR",
            f"카테고리 클릭 실패: {e}"
        )

        return False


def crawl_current_page(category_name, page):
    rows = []

    product_items = page.query_selector_all(
        SELECTORS["product_items"]
    )

    if not product_items:
        insert_log(
            category_name,
            "ERROR",
            "상품 목록을 찾지 못했습니다. SELECTORS 또는 페이지 구조를 확인하세요."
        )

        return rows

    seen_goods = set()
    real_rank = 1

    for item in product_items:
        if real_rank > MAX_PRODUCTS_PER_CATEGORY:
            break

        try:
            row = parse_product_item(
                item,
                real_rank,
                category_name
            )

            goods_no = row.get("goods_no")
            product_name = row.get("product_name")

            if not goods_no:
                continue

            if not product_name:
                continue

            if goods_no in seen_goods:
                continue

            seen_goods.add(goods_no)
            rows.append(row)

            print(
                f"[{category_name}] {real_rank}위 수집 완료 "
                f"- {row['brand_name']} / {row['goods_no']} / {row['product_name']}"
            )

            real_rank += 1

        except Exception as e:
            insert_log(
                category_name,
                "ERROR",
                f"{real_rank}위 상품 파싱 실패: {e}"
            )

    return rows


def crawl_category(category_name):
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1200
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            )
        )

        try:
            open_ranking_page(page)

            clicked = click_category(
                page,
                category_name
            )

            if not clicked:
                return rows

            rows = crawl_current_page(
                category_name,
                page
            )

            insert_log(
                category_name,
                "SUCCESS",
                f"{len(rows)}개 상품 수집 완료"
            )

        except Exception as e:
            insert_log(
                category_name,
                "ERROR",
                f"페이지 접속 또는 수집 실패: {e}"
            )

            print(f"[수집 실패] {category_name}: {e}")

        finally:
            browser.close()

    return rows


def crawl_all_categories():
    init_db()

    total_inserted = 0

    for category_name in CATEGORIES:

        print("=" * 80)
        print(f"[수집 시작] {category_name}")
        print(f"[기본 랭킹 URL] {RANKING_URL}")
        print("=" * 80)

        rows = crawl_category(
            category_name
        )

        inserted = insert_rankings(rows)

        total_inserted += inserted

        print(
            f"[수집 완료] {category_name}: {inserted}건 저장"
        )

        if rows:
            print("[샘플 확인]")
            for sample in rows[:5]:
                print(
                    f"- {sample.get('rank')}위 / "
                    f"{sample.get('brand_name')} / "
                    f"{sample.get('product_name')}"
                )

        time.sleep(REQUEST_DELAY_SECONDS)

    print("=" * 80)
    print(f"[전체 완료] 신규 저장 {total_inserted}건")
    print("=" * 80)

    return total_inserted


if __name__ == "__main__":
    crawl_all_categories()
