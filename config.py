from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "oliveyoung_rank.db"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

CRAWL_TIMES = ["09:00", "15:00", "21:00"]

HEADLESS = True

REQUEST_DELAY_SECONDS = 3
PAGE_WAIT_SECONDS = 5
MAX_PRODUCTS_PER_CATEGORY = 100

# 올리브영 랭킹 기본 페이지
RANKING_URL = "https://www.oliveyoung.co.kr/store/main/getBestList.do"

# 올리브영 랭킹 화면에 노출되는 카테고리명 기준
# URL을 직접 넣지 않고, crawler.py에서 이 이름을 클릭해서 수집합니다.
CATEGORIES = [
    "전체",
    "스킨케어",
    "마스크팩",
    "클렌징",
    "선케어",
    "메이크업",
    "네일",
    "뷰티소품",
    "더모 코스메틱",
    "맨즈에딧",
    "향수/디퓨저",
    "헤어케어",
    "바디케어",
    "건강식품",
    "푸드",
    "구강용품",
    "헬스/건강용품",
    "위생용품",
    "패션",
    "홈리빙/가전",
    "취미/팬시",
]

# 올리브영 페이지 구조가 바뀌면 이 부분을 먼저 확인하세요.
SELECTORS = {
    "product_items": "ul.cate_prd_list > li",
    "brand": ".tx_brand",
    "product_name": ".tx_name",
    "normal_price": ".tx_org",
    "sale_price": ".tx_cur",
    "discount_rate": ".tx_discount",
    "product_link": "a",
}