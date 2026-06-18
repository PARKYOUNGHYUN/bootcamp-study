# Jeonse Risk Analysis

전세보증금 사고, 전세가율, 미분양 데이터를 MySQL에서 조회하고 Python으로 시각화하여 전세 리스크를 분석하는 데이터 분석 프로젝트입니다.

> 본 프로젝트는 부동산 전세 리스크를 지역별·연도별로 비교하기 위한 학습용 데이터 분석 코드입니다.

---

## Key Features

- **전세보증금 사고 데이터 분석** — 지역별 전세보증금 사고 건수 및 보증금 규모를 집계합니다.
- **전세가율 비교 분석** — 법정동 코드 기준으로 전세 사고 데이터와 전세가율 데이터를 조인하여 지역별 위험도를 비교합니다.
- **미분양 데이터 연계 분석** — 연도별 전세 사고 건수와 미분양 물량의 평균 추이를 함께 분석합니다.
- **Matplotlib 기반 시각화** — 막대그래프, 선그래프, 산점도를 활용해 분석 결과를 시각적으로 확인할 수 있습니다.
- **MySQL 데이터베이스 연동** — `pymysql`, `SQLAlchemy`, `pandas`를 사용해 MySQL 데이터를 조회하거나 CSV 데이터를 적재합니다.

---

## Tech Stack

| 구분 | 기술 |
|---|---|
| Language | Python |
| Database | MySQL |
| Data Processing | pandas |
| DB Connector | pymysql, SQLAlchemy |
| Visualization | matplotlib, koreanize-matplotlib |
| Config | python-dotenv |

---

## Getting Started

### Prerequisites

- Python 3.9+
- MySQL Server 또는 접근 가능한 MySQL 데이터베이스
- pip

### Installation

```bash
cd 05_DatabaseBasic/jeonse_risk_analysis
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install pandas pymysql sqlalchemy matplotlib koreanize-matplotlib python-dotenv
```

### 환경 변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 DB 접속 정보를 입력합니다.

```bash
cp .env.example .env
```

```env
DB_HOST=172.30.1.12
DB_PORT=3306
DB_USER=team1
DB_PASSWORD=1234
DB_NAME=team1_01
```

---

## Usage

### 1. CSV 데이터를 MySQL에 적재

`data_loader.py`는 `./data/data.csv`를 읽어 `jeonse_deposit_accidents` 테이블에 적재합니다.

```bash
python data_loader.py
```

실행 전 다음 파일이 필요합니다.

```text
data/data.csv
```

### 2. 지역별 보증금액 및 전세율 조회

`sido_deposit_query.py`는 시도별 보증금액 평균과 전세율 평균을 조회해 콘솔에 출력합니다.

```bash
python sido_deposit_query.py
```

### 3. 지역별 전세 사고 건수 및 전세율 시각화

`sido_accident_chart.py`는 지역별 전세 사고 건수와 전세율을 4종의 차트로 시각화합니다.

```bash
python sido_accident_chart.py
```

### 4. 연도별 전세 사고 건수와 미분양 추이 시각화

`yearly_analysis.py`는 연도별 전세 사고 건수 평균과 미분양 평균을 이중 축 그래프로 시각화합니다.

```bash
python yearly_analysis.py
```

---

## Project Structure

```text
jeonse_risk_analysis/
├── .env                       # DB 접속 정보 (비공개 — git 제외)
├── .env.example               # .env 양식
├── config.py                  # DB 연결 설정
├── queries.py                 # SQL 쿼리 함수
├── sido_accident_chart.py     # 지역별 사고건수 + 전세율 시각화
├── sido_deposit_query.py      # 지역별 보증금액 + 전세율 조회
├── yearly_analysis.py         # 연도별 사고건수 + 미분양 시각화
├── data_loader.py             # CSV 데이터 적재
├── sido_accident_chart.ipynb  # 실행 결과 보존 노트북 (참고용)
└── README.md
```

---

## Main Database Tables

| 테이블명 | 설명 |
|---|---|
| `jeonse_deposit_accidents` | 전세보증금 사고 데이터 |
| `dong_code` | 법정동 코드 및 지역 정보 |
| `price_rate` | 전세가율 데이터 |
| `unsold` | 미분양 주택 데이터 |
| `house_type` | 주택 유형 코드 |
| `active_realtors` | 개업 공인중개사 관련 데이터 |

---

## Analysis Queries

### 지역별 보증사고 건수 + 전세율 평균

```sql
SELECT
    dc.sido,
    AVG(jda.count) AS count_avg,
    AVG(pr.value) AS price_rate_avg
FROM jeonse_deposit_accidents jda
INNER JOIN price_rate pr ON jda.legal_dong_code = pr.NO
INNER JOIN dong_code dc ON pr.NO = dc.legal_dong_code
GROUP BY jda.legal_dong_code
ORDER BY dc.legal_dong_code;
```

### 지역별 보증금액 + 전세율 평균

```sql
SELECT
    dc.sido,
    AVG(jda.deposit_amount * jda.count) AS deposit_amount_avg,
    AVG(pr.value) AS price_rate_avg
FROM jeonse_deposit_accidents jda
INNER JOIN price_rate pr ON jda.legal_dong_code = pr.NO
INNER JOIN dong_code dc ON pr.NO = dc.legal_dong_code
GROUP BY jda.legal_dong_code
ORDER BY dc.legal_dong_code;
```

### 연도별 보증사고 건수 + 미분양 평균

```sql
SELECT
    jda.year,
    AVG(jda.count) AS count_avg,
    AVG(u.unsold) AS unsold_avg
FROM dong_code dc
INNER JOIN unsold u ON u.legal_dong_code = dc.legal_dong_code
INNER JOIN jeonse_deposit_accidents jda
    ON jda.year = u.year
    AND (
        dc.legal_dong_code = jda.legal_dong_code
        OR dc.province_code = jda.legal_dong_code
    )
GROUP BY jda.year
ORDER BY jda.year;
```

---

## Notes

- Windows 환경에서는 한글 그래프 출력을 위해 `koreanize-matplotlib` 패키지를 사용합니다.
- `data_loader.py` 실행 시 `./data/data.csv` 파일이 필요합니다.
- DB 접속 정보는 `.env` 파일로 관리하며, `.env`는 git에 포함되지 않습니다.
- `sido_accident_chart.ipynb`는 실제 DB 조회 결과가 저장된 참고용 노트북입니다.
