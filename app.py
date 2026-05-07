import io

import pandas as pd
import plotly.express as px
import streamlit as st

from database import init_db, load_logs, load_rankings


st.set_page_config(
    page_title="올리브영 랭킹 대시보드",
    layout="wide"
)


CUSTOM_CSS = """
<style>
:root {
    --bg: #f6f8fb;
    --panel: #ffffff;
    --text: #17202a;
    --muted: #6b7280;
    --line: #e5e7eb;
    --green: #0f8f5f;
    --green-dark: #076c47;
    --green-soft: #e9fff5;
    --shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    --radius: 18px;
}

html, body, [class*="css"] {
    color: var(--text);
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1520px;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    letter-spacing: -0.4px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e2a20 0%, #10231b 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] label {
    color: #c8d5ce !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] .stCaption {
    color: #b9c7bf !important;
}

/* 사이드바 날짜 선택 */
section[data-testid="stSidebar"] .stDateInput > div > div {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

section[data-testid="stSidebar"] .stDateInput input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

/* 사이드바 드롭다운 */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #ffffff !important;
}

/* A코드 검색 입력창 */
section[data-testid="stSidebar"] .stTextInput > div > div {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
}

section[data-testid="stSidebar"] .stTextInput input {
    background: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}

section[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* 체크박스 */
section[data-testid="stSidebar"] .stCheckbox label span {
    color: #ffffff !important;
}

/* 슬라이더 */
section[data-testid="stSidebar"] .stSlider {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
    color: #ffffff !important;
}

/* KPI 카드 */
div[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 18px 20px;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 800 !important;
}

div[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 900 !important;
}

/* 테이블 */
.stDataFrame {
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
    background: var(--panel);
}

/* 버튼 */
.stDownloadButton button,
.stButton button {
    border-radius: 999px !important;
    padding: 0.62rem 1.1rem !important;
    border: 1px solid var(--green) !important;
    color: var(--green) !important;
    background: #ffffff !important;
    font-weight: 800 !important;
}

.stDownloadButton button:hover,
.stButton button:hover {
    background: #f3fbf7 !important;
    border-color: var(--green-dark) !important;
    color: var(--green-dark) !important;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: #ffffff;
    border-radius: 999px;
    border: 1px solid var(--line);
    padding: 10px 18px;
    color: var(--text) !important;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    background: var(--green-soft) !important;
    border-color: #cbeedc !important;
    color: var(--green-dark) !important;
}

/* 상단 타이틀 */
.olive-title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 12px;
}

.olive-title {
    color: var(--text);
    font-size: 40px;
    font-weight: 900;
    margin: 0 0 6px 0;
    letter-spacing: -1px;
}

.olive-subtitle {
    color: var(--muted);
    font-size: 15px;
    margin-top: 0;
    margin-bottom: 12px;
}

.status-pill {
    background: var(--green-soft);
    color: var(--green-dark);
    padding: 12px 16px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 900;
    white-space: nowrap;
    border: 1px solid #d5f5e4;
}

/* 분석 카드 */
.analysis-card-wrap {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 8px 0 18px;
}

.analysis-card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 20px;
    min-height: 130px;
}

.analysis-title {
    color: var(--muted);
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}

.analysis-value {
    color: var(--text);
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 4px;
}

.analysis-desc {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
}

/* 섹션 카드 */
.section-card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 18px 20px;
    margin: 14px 0 22px;
}

.section-title {
    color: var(--text);
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.6px;
    margin: 12px 0 12px 0;
}

.section-subtitle {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 8px;
}

/* expander */
details {
    background: var(--panel);
    border-radius: 16px;
    border: 1px solid var(--line);
    padding: 8px 12px;
}

/* 반응형 */
@media (max-width: 1200px) {
    .analysis-card-wrap {
        grid-template-columns: 1fr;
    }

    .olive-title-row {
        flex-direction: column;
    }

    .olive-title {
        font-size: 30px;
    }
}
</style>
"""


def make_excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ranking_data")
    return output.getvalue()


def prepare_dataframe(df):
    if df.empty:
        return df

    df["collected_date"] = pd.to_datetime(df["collected_date"])
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["normal_price"] = pd.to_numeric(df["normal_price"], errors="coerce")
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")

    return df


def make_daily_average_df(df):
    if df.empty:
        return df

    df = df.sort_values(
        ["collected_date", "category_name", "goods_no", "collected_time"]
    )

    daily_df = (
        df.groupby(
            ["collected_date", "category_name", "goods_no"],
            dropna=False
        )
        .agg(
            rank=("rank", "mean"),
            brand_name=("brand_name", "last"),
            product_name=("product_name", "last"),
            normal_price=("normal_price", "last"),
            sale_price=("sale_price", "last"),
            discount_rate=("discount_rate", "last"),
            product_url=("product_url", "last"),
            latest_collected_time=("collected_time", "max"),
        )
        .reset_index()
    )

    daily_df["rank"] = daily_df["rank"].round(1)

    return daily_df


def make_period_average_df(df, start_date, end_date):
    period_df = df[
        (df["collected_date"].dt.date >= start_date)
        & (df["collected_date"].dt.date <= end_date)
    ].copy()

    if period_df.empty:
        return period_df

    result = (
        period_df.groupby(["category_name", "goods_no"], dropna=False)
        .agg(
            rank=("rank", "mean"),
            brand_name=("brand_name", "last"),
            product_name=("product_name", "last"),
            normal_price=("normal_price", "last"),
            sale_price=("sale_price", "last"),
            discount_rate=("discount_rate", "last"),
            product_url=("product_url", "last"),
            latest_collected_time=("latest_collected_time", "max"),
        )
        .reset_index()
    )

    result["rank"] = result["rank"].round(1)

    return result


def add_compare_rank(base_df, compare_df):
    if compare_df is None or compare_df.empty:
        base_df["compare_rank"] = pd.NA
        base_df["rank_change"] = pd.NA
        return base_df

    compare_rank_df = compare_df[
        ["category_name", "goods_no", "rank"]
    ].rename(columns={"rank": "compare_rank"})

    result_df = base_df.merge(
        compare_rank_df,
        on=["category_name", "goods_no"],
        how="left"
    )

    result_df["rank_change"] = result_df["compare_rank"] - result_df["rank"]

    return result_df


def apply_common_filters(df, selected_category, selected_brand, goods_search, top_n):
    result = df.copy()

    result = result[result["category_name"] == selected_category]

    if selected_brand != "전체":
        result = result[result["brand_name"] == selected_brand]

    if goods_search:
        result = result[
            result["goods_no"].fillna("").str.contains(goods_search, case=False, na=False)
        ]

    result = result[result["rank"] <= top_n]

    return result


def make_brand_share(base_df, selected_category, selected_brand, top_n):
    category_df = base_df[base_df["category_name"] == selected_category].copy()
    top_df = category_df[category_df["rank"] <= top_n].copy()

    if top_df.empty:
        return pd.DataFrame()

    total_products = top_df["goods_no"].nunique()

    result = (
        top_df.groupby("brand_name", dropna=False)
        .agg(
            top_product_count=("goods_no", "nunique"),
            avg_rank=("rank", "mean"),
        )
        .reset_index()
    )

    result["share_percent"] = (
        result["top_product_count"] / total_products * 100
    ).round(1)

    result["avg_rank"] = result["avg_rank"].round(1)

    result = result.sort_values(
        ["share_percent", "top_product_count", "avg_rank"],
        ascending=[False, False, True]
    )

    if selected_brand != "전체":
        result = result[result["brand_name"] == selected_brand]

    return result


def make_brand_growth(base_df, compare_df, selected_category, selected_brand, top_n):
    if compare_df is None or compare_df.empty:
        return pd.DataFrame()

    base_top = base_df[
        (base_df["category_name"] == selected_category)
        & (base_df["rank"] <= top_n)
    ].copy()

    compare_top = compare_df[
        (compare_df["category_name"] == selected_category)
        & (compare_df["rank"] <= top_n)
    ].copy()

    if selected_brand != "전체":
        base_top = base_top[base_top["brand_name"] == selected_brand]
        compare_top = compare_top[compare_top["brand_name"] == selected_brand]

    base_brand = (
        base_top.groupby("brand_name", dropna=False)
        .agg(
            base_product_count=("goods_no", "nunique"),
            base_avg_rank=("rank", "mean"),
        )
        .reset_index()
    )

    compare_brand = (
        compare_top.groupby("brand_name", dropna=False)
        .agg(
            compare_product_count=("goods_no", "nunique"),
            compare_avg_rank=("rank", "mean"),
        )
        .reset_index()
    )

    result = base_brand.merge(compare_brand, on="brand_name", how="outer")

    result = result.fillna(
        {"base_product_count": 0, "compare_product_count": 0}
    )

    result["product_count_change"] = (
        result["base_product_count"] - result["compare_product_count"]
    )

    result["avg_rank_change"] = (
        result["compare_avg_rank"] - result["base_avg_rank"]
    )

    result["base_avg_rank"] = result["base_avg_rank"].round(1)
    result["compare_avg_rank"] = result["compare_avg_rank"].round(1)
    result["avg_rank_change"] = result["avg_rank_change"].round(1)

    return result.sort_values(
        ["product_count_change", "avg_rank_change"],
        ascending=[False, False]
    )


def make_ranking_retention(base_df, compare_df, selected_category, selected_brand, top_n):
    if compare_df is None or compare_df.empty:
        return pd.DataFrame()

    base_top = base_df[
        (base_df["category_name"] == selected_category)
        & (base_df["rank"] <= top_n)
    ].copy()

    compare_top = compare_df[
        (compare_df["category_name"] == selected_category)
        & (compare_df["rank"] <= top_n)
    ].copy()

    if selected_brand != "전체":
        base_top = base_top[base_top["brand_name"] == selected_brand]
        compare_top = compare_top[compare_top["brand_name"] == selected_brand]

    if base_top.empty:
        return pd.DataFrame()

    merged = base_top.merge(
        compare_top[["category_name", "goods_no", "rank"]].rename(
            columns={"rank": "compare_rank"}
        ),
        on=["category_name", "goods_no"],
        how="left"
    )

    merged["is_retained"] = merged["compare_rank"].notna()

    summary = (
        merged.groupby("brand_name", dropna=False)
        .agg(
            base_top_products=("goods_no", "nunique"),
            retained_products=("is_retained", "sum"),
            avg_base_rank=("rank", "mean"),
            avg_compare_rank=("compare_rank", "mean"),
        )
        .reset_index()
    )

    summary["retention_rate"] = (
        summary["retained_products"] / summary["base_top_products"] * 100
    ).round(1)

    summary["avg_base_rank"] = summary["avg_base_rank"].round(1)
    summary["avg_compare_rank"] = summary["avg_compare_rank"].round(1)

    return summary.sort_values("retention_rate", ascending=False)


def format_rank_value(value):
    if pd.isna(value) or value == "":
        return ""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def format_price_value(value):
    if pd.isna(value) or value == "":
        return ""
    try:
        return f"{int(value):,}"
    except Exception:
        return value


def format_for_display(df):
    display_df = df.copy()

    for col in display_df.columns:
        display_df[col] = display_df[col].fillna("")

    if "기준 순위" in display_df.columns:
        display_df["기준 순위"] = display_df["기준 순위"].apply(format_rank_value)

    if "비교 순위" in display_df.columns:
        display_df["비교 순위"] = display_df["비교 순위"].apply(format_rank_value)

    if "순위 증감" in display_df.columns:
        display_df["순위 증감"] = display_df["순위 증감"].apply(format_rank_value)

    if "평균 순위" in display_df.columns:
        display_df["평균 순위"] = display_df["평균 순위"].apply(format_rank_value)

    if "기준 기간 평균 순위" in display_df.columns:
        display_df["기준 기간 평균 순위"] = display_df["기준 기간 평균 순위"].apply(format_rank_value)

    if "비교 기간 평균 순위" in display_df.columns:
        display_df["비교 기간 평균 순위"] = display_df["비교 기간 평균 순위"].apply(format_rank_value)

    if "평균 순위 증감" in display_df.columns:
        display_df["평균 순위 증감"] = display_df["평균 순위 증감"].apply(format_rank_value)

    for col in ["정상가", "판매가"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_price_value)

    return display_df


def rename_ranking_columns(df, use_compare):
    rename_map = {
        "category_name": "카테고리",
        "rank": "기준 순위",
        "compare_rank": "비교 순위",
        "rank_change": "순위 증감",
        "brand_name": "브랜드명",
        "goods_no": "A코드",
        "product_name": "상품명",
        "normal_price": "정상가",
        "sale_price": "판매가",
        "discount_rate": "할인율",
        "product_url": "상품 URL",
    }

    if not use_compare:
        df = df.drop(columns=["compare_rank", "rank_change"], errors="ignore")

    return df.rename(columns=rename_map)


def rename_share_columns(df):
    return df.rename(
        columns={
            "brand_name": "브랜드명",
            "top_product_count": "TOP 순위 내 상품 수",
            "avg_rank": "평균 순위",
            "share_percent": "점유율(%)",
        }
    )


def rename_growth_columns(df):
    return df.rename(
        columns={
            "brand_name": "브랜드명",
            "base_product_count": "기준 기간 상품 수",
            "base_avg_rank": "기준 기간 평균 순위",
            "compare_product_count": "비교 기간 상품 수",
            "compare_avg_rank": "비교 기간 평균 순위",
            "product_count_change": "상품 수 증감",
            "avg_rank_change": "평균 순위 증감",
        }
    )


def rename_retention_columns(df):
    return df.rename(
        columns={
            "brand_name": "브랜드명",
            "base_top_products": "기준 기간 TOP 상품 수",
            "retained_products": "비교 기간에도 유지된 상품 수",
            "avg_base_rank": "기준 기간 평균 순위",
            "avg_compare_rank": "비교 기간 평균 순위",
            "retention_rate": "랭킹 유지율(%)",
        }
    )


def make_summary_cards(ranking_df, use_compare):
    product_count = len(ranking_df)
    brand_count = ranking_df["brand_name"].nunique()
    avg_rank = ranking_df["rank"].mean()

    if use_compare and "rank_change" in ranking_df.columns:
        avg_change = ranking_df["rank_change"].dropna().mean()
    else:
        avg_change = None

    return product_count, brand_count, avg_rank, avg_change


def apply_plotly_style(fig, yaxis_title=None, xaxis_title=None, reverse_y=False):
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#17202a", size=13),
        title=dict(font=dict(color="#17202a", size=18)),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#e5e7eb",
            borderwidth=1,
            title_font=dict(color="#17202a"),
            font=dict(color="#17202a", size=12),
        ),
        margin=dict(l=40, r=30, t=60, b=40),
    )

    fig.update_xaxes(
        title=xaxis_title,
        showgrid=False,
        linecolor="#d1d5db",
        tickfont=dict(color="#374151"),
        title_font=dict(color="#374151"),
    )

    fig.update_yaxes(
        title=yaxis_title,
        showgrid=True,
        gridcolor="#e5e7eb",
        zeroline=False,
        linecolor="#d1d5db",
        tickfont=dict(color="#374151"),
        title_font=dict(color="#374151"),
        autorange="reversed" if reverse_y else True,
    )

    fig.update_traces(
        textfont_color="#17202a"
    )

    return fig


def render_analysis_cards(share_df, growth_df, retention_df, use_compare):
    top_share = "-"
    if not share_df.empty:
        top_share = f"{share_df['share_percent'].max():.1f}%"

    growth_value = "-"
    if use_compare and not growth_df.empty:
        growth_value = f"{growth_df['product_count_change'].max():+.0f}개"

    retention_value = "-"
    if use_compare and not retention_df.empty:
        retention_value = f"{retention_df['retention_rate'].mean():.1f}%"

    st.markdown(
        f"""
        <div class="analysis-card-wrap">
            <div class="analysis-card">
                <div class="analysis-title">카테고리별 점유율</div>
                <div class="analysis-value">{top_share}</div>
                <div class="analysis-desc">선택 조건 내 가장 높은 브랜드 점유율입니다.</div>
            </div>
            <div class="analysis-card">
                <div class="analysis-title">브랜드 성장률</div>
                <div class="analysis-value">{growth_value}</div>
                <div class="analysis-desc">비교 기간 대비 TOP 순위 내 상품 수 증가입니다.</div>
            </div>
            <div class="analysis-card">
                <div class="analysis-title">랭킹 유지력</div>
                <div class="analysis-value">{retention_value}</div>
                <div class="analysis-desc">비교 기간에도 TOP 순위에 남아있는 비율입니다.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# 초기화
init_db()
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

raw_df = load_rankings()
raw_df = prepare_dataframe(raw_df)

if raw_df.empty:
    st.title("올리브영 카테고리 랭킹 대시보드")
    st.warning("아직 저장된 데이터가 없습니다.")
    st.info("먼저 `python crawler.py`를 실행하세요.")
    st.stop()

daily_df = make_daily_average_df(raw_df)

available_dates = sorted(
    daily_df["collected_date"].dt.date.unique().tolist()
)

default_base_start = available_dates[-1]
default_base_end = available_dates[-1]

if len(available_dates) >= 2:
    default_compare_start = available_dates[-2]
    default_compare_end = available_dates[-2]
else:
    default_compare_start = available_dates[-1]
    default_compare_end = available_dates[-1]


# 사이드바
with st.sidebar:
    st.markdown("## OLIVE RANK")
    st.caption("올리브영 랭킹 자동 누적 대시보드")

    base_period = st.date_input(
        "조회 기준 기간",
        value=(default_base_start, default_base_end),
        min_value=available_dates[0],
        max_value=available_dates[-1],
    )

    if isinstance(base_period, tuple):
        base_start, base_end = base_period
    else:
        base_start = base_end = base_period

    use_compare = st.checkbox(
        "비교 기간 사용",
        value=len(available_dates) >= 2,
    )

    if use_compare:
        compare_period = st.date_input(
            "비교 기간",
            value=(default_compare_start, default_compare_end),
            min_value=available_dates[0],
            max_value=available_dates[-1],
        )

        if isinstance(compare_period, tuple):
            compare_start, compare_end = compare_period
        else:
            compare_start = compare_end = compare_period
    else:
        compare_start = None
        compare_end = None

    categories = sorted(
        daily_df["category_name"].dropna().unique().tolist()
    )

    selected_category = st.selectbox("카테고리", categories)

    brand_source_df = daily_df[
        (daily_df["collected_date"].dt.date >= base_start)
        & (daily_df["collected_date"].dt.date <= base_end)
        & (daily_df["category_name"] == selected_category)
    ]

    brands = ["전체"] + sorted(
        brand_source_df["brand_name"].dropna().unique().tolist()
    )

    selected_brand = st.selectbox("브랜드 선택", brands)

    goods_search = st.text_input("A코드 검색")

    top_n = st.slider(
        "분석 기준 순위",
        min_value=10,
        max_value=100,
        value=100,
        step=10,
    )


# 데이터 준비
base_df = make_period_average_df(daily_df, base_start, base_end)

if use_compare:
    compare_df = make_period_average_df(daily_df, compare_start, compare_end)
else:
    compare_df = None

ranking_df = add_compare_rank(base_df, compare_df)

ranking_df = apply_common_filters(
    ranking_df,
    selected_category,
    selected_brand,
    goods_search,
    top_n,
).sort_values("rank", ascending=True)

share_df = make_brand_share(base_df, selected_category, selected_brand, top_n)

if use_compare:
    growth_df = make_brand_growth(
        base_df, compare_df, selected_category, selected_brand, top_n
    )
    retention_df = make_ranking_retention(
        base_df, compare_df, selected_category, selected_brand, top_n
    )
else:
    growth_df = pd.DataFrame()
    retention_df = pd.DataFrame()

last_collect_time = raw_df.sort_values(
    ["collected_date", "collected_time"]
).tail(1)

if not last_collect_time.empty:
    last_date = last_collect_time.iloc[0]["collected_date"].date()
    last_time = last_collect_time.iloc[0]["collected_time"]
    status_text = f"마지막 수집 {last_date} {last_time}"
else:
    status_text = "수집 이력 없음"


# 상단 헤더
st.markdown(
    f"""
    <div class="olive-title-row">
        <div>
            <div class="olive-title">올리브영 카테고리 랭킹 대시보드</div>
            <div class="olive-subtitle">
                카테고리 랭킹, 브랜드 점유율, 성장률, 유지력을 한 화면에서 확인합니다.
            </div>
        </div>
        <div class="status-pill">{status_text}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# KPI
product_count, brand_count, avg_rank, avg_change = make_summary_cards(
    ranking_df, use_compare
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("조회 상품 수", f"{product_count:,}")
col2.metric("조회 브랜드 수", f"{brand_count:,}")
col3.metric("평균 순위", "-" if pd.isna(avg_rank) else f"{avg_rank:.1f}")

if use_compare:
    col4.metric("평균 순위 증감", "-" if pd.isna(avg_change) else f"{avg_change:+.1f}")
else:
    col4.metric("조회 기준 기간", f"{base_start} ~ {base_end}")


# 요약 카드
render_analysis_cards(share_df, growth_df, retention_df, use_compare)


# 순위 추이
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">순위 추이</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">조회 기준 기간 기준 상위 상품의 날짜별 순위 변화를 보여줍니다.</div>',
    unsafe_allow_html=True
)

trend_df = daily_df[
    (daily_df["collected_date"].dt.date >= base_start)
    & (daily_df["collected_date"].dt.date <= base_end)
    & (daily_df["category_name"] == selected_category)
].copy()

if selected_brand != "전체":
    trend_df = trend_df[trend_df["brand_name"] == selected_brand]

if goods_search:
    trend_df = trend_df[
        trend_df["goods_no"].fillna("").str.contains(goods_search, case=False, na=False)
    ]

top_products = ranking_df.sort_values("rank").head(10)["goods_no"].tolist()
trend_df = trend_df[trend_df["goods_no"].isin(top_products)]

if trend_df.empty:
    st.info("선택한 조건에 맞는 추이 데이터가 없습니다.")
else:
    trend_df = trend_df.sort_values(["collected_date", "rank"])
    trend_df["수집일"] = trend_df["collected_date"].dt.strftime("%Y-%m-%d")
    trend_df["상품"] = (
        trend_df["brand_name"].fillna("")
        + " | "
        + trend_df["product_name"].fillna("")
    )

    fig = px.line(
        trend_df,
        x="수집일",
        y="rank",
        color="상품",
        markers=True,
        title=f"{base_start} ~ {base_end} 제품별 순위 추이"
    )

    fig = apply_plotly_style(
        fig,
        yaxis_title="순위",
        xaxis_title="수집일",
        reverse_y=True
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# 랭킹 테이블
st.markdown('<div class="section-title">랭킹 테이블</div>', unsafe_allow_html=True)

display_cols = [
    "category_name",
    "rank",
    "compare_rank",
    "rank_change",
    "brand_name",
    "goods_no",
    "product_name",
    "normal_price",
    "sale_price",
    "discount_rate",
    "product_url",
]

display_df = ranking_df[display_cols].copy()
display_df = rename_ranking_columns(display_df, use_compare)
display_df = format_for_display(display_df)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
excel_data = make_excel_download(display_df)

download_col1, download_col2 = st.columns(2)

download_col1.download_button(
    "CSV 다운로드",
    data=csv_data,
    file_name="oliveyoung_ranking.csv",
    mime="text/csv",
)

download_col2.download_button(
    "Excel 다운로드",
    data=excel_data,
    file_name="oliveyoung_ranking.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)


# 전문 분석
st.markdown('<div class="section-title">전문 분석</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(
    ["카테고리별 점유율 분석", "브랜드 성장률", "랭킹 유지력"]
)

with tab1:
    if share_df.empty:
        st.info("점유율 분석 데이터가 없습니다.")
    else:
        share_display_df = rename_share_columns(share_df)
        share_display_df = format_for_display(share_display_df)

        st.dataframe(
            share_display_df,
            use_container_width=True,
            hide_index=True
        )

        fig = px.bar(
            share_display_df.head(20),
            x="브랜드명",
            y="점유율(%)",
            text="점유율(%)",
            title=f"{selected_category} TOP{top_n} 브랜드 점유율"
        )

        fig = apply_plotly_style(
            fig,
            yaxis_title="점유율(%)",
            xaxis_title="브랜드명",
            reverse_y=False
        )

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if not use_compare:
        st.info("브랜드 성장률은 비교 기간을 사용할 때 표시됩니다.")
    elif growth_df.empty:
        st.info("브랜드 성장률 데이터가 없습니다.")
    else:
        growth_display_df = rename_growth_columns(growth_df)
        growth_display_df = format_for_display(growth_display_df)

        st.dataframe(
            growth_display_df,
            use_container_width=True,
            hide_index=True
        )

        chart_df = growth_display_df.sort_values("상품 수 증감", ascending=False).head(20)

        fig = px.bar(
            chart_df,
            x="브랜드명",
            y="상품 수 증감",
            text="상품 수 증감",
            title=f"{selected_category} TOP{top_n} 브랜드 상품 수 증감"
        )

        fig = apply_plotly_style(
            fig,
            yaxis_title="상품 수 증감",
            xaxis_title="브랜드명",
            reverse_y=False
        )

        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if not use_compare:
        st.info("랭킹 유지력은 비교 기간을 사용할 때 표시됩니다.")
    elif retention_df.empty:
        st.info("랭킹 유지력 데이터가 없습니다.")
    else:
        retention_display_df = rename_retention_columns(retention_df)
        retention_display_df = format_for_display(retention_display_df)

        st.dataframe(
            retention_display_df,
            use_container_width=True,
            hide_index=True
        )

        fig = px.bar(
            retention_display_df.head(20),
            x="브랜드명",
            y="랭킹 유지율(%)",
            text="랭킹 유지율(%)",
            title=f"{selected_category} TOP{top_n} 랭킹 유지율"
        )

        fig = apply_plotly_style(
            fig,
            yaxis_title="랭킹 유지율(%)",
            xaxis_title="브랜드명",
            reverse_y=False
        )

        st.plotly_chart(fig, use_container_width=True)


# 로그
with st.expander("수집 로그 확인"):
    logs = load_logs()

    logs = logs.rename(
        columns={
            "id": "번호",
            "log_time": "로그 시간",
            "category_name": "카테고리",
            "status": "상태",
            "message": "메시지",
        }
    )

    st.dataframe(
        logs,
        use_container_width=True,
        hide_index=True
    )