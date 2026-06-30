import pandas as pd
from config import get_connection


def fetch_sido_accident_count():
    """시도별 보증사고 건수 평균 + 전세율 평균"""
    query = """
    SELECT
        dc.sido,
        avg(jda.count) AS count_avg,
        avg(pr.value) AS price_rate_avg
    FROM jeonse_deposit_accidents jda
    INNER JOIN price_rate pr ON jda.legal_dong_code = pr.NO
    INNER JOIN dong_code dc ON pr.NO = dc.legal_dong_code
    GROUP BY jda.legal_dong_code
    ORDER BY dc.LEGAL_DONG_CODE
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = ['지역', '보증사고 건수 평균', '전세율 평균']
    return df


def fetch_sido_deposit_amount():
    """시도별 보증금액 평균 + 전세율 평균"""
    query = """
    SELECT
        dc.sido,
        avg(jda.deposit_amount * jda.count) AS deposit_amount_avg,
        avg(pr.value) AS price_rate_avg
    FROM jeonse_deposit_accidents jda
    INNER JOIN price_rate pr ON jda.legal_dong_code = pr.NO
    INNER JOIN dong_code dc ON pr.NO = dc.legal_dong_code
    GROUP BY jda.legal_dong_code
    ORDER BY dc.LEGAL_DONG_CODE
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = ['지역', '보증금액 평균', '전세율 평균']
    return df


def fetch_yearly_accident_unsold():
    """연도별 보증사고 건수 평균 + 미분양 평균"""
    query = """
    SELECT
        jda.year,
        avg(jda.count) AS count_avg,
        avg(u.unsold) AS unsold_avg
    FROM dong_code dc
    INNER JOIN unsold u ON u.legal_dong_code = dc.legal_dong_code
    INNER JOIN jeonse_deposit_accidents jda
        ON jda.year = u.year
        AND (
            dc.legal_dong_code = jda.legal_dong_code
            OR dc.province_code = jda.legal_dong_code
        )
    GROUP BY jda.year
    ORDER BY jda.year
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = ['연도', '보증건수 평균', '미분양 평균']
    return df
