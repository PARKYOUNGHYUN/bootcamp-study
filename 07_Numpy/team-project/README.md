# Circle Chart Album Performance Analysis

> Circle Chart 주간 앨범 차트 데이터를 수집하고, Apple iTunes Search API의 앨범 발매일 정보를 결합해 아티스트의 1집 대비 2집 차트 성과를 분석하는 Python 데이터 분석 프로젝트입니다.

## ✨ Key Features

- **Circle Chart 주간 랭킹 수집**: Circle Chart API를 호출해 연도/주차별 앨범 차트 순위 데이터를 `data/ranking_list.csv`로 저장합니다.
- **차트 기간 메타데이터 수집**: 주차 코드(`YYYYNN`)별 시작일과 종료일을 파싱해 `data/period.csv`를 생성합니다.
- **앨범 발매일 매핑**: Apple iTunes Search API를 활용해 아티스트별 앨범 발매일을 조회하고 차트 진입 시점과 비교합니다.
- **차트 성과 시각화**: Matplotlib과 NumPy를 활용해 1집 대비 2집의 첫 차트 진입 순위, 최고 순위, 차트 유지 기간 등을 그래프로 분석합니다.

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Analysis-013243?logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20Parsing-4B8BBE)
![Requests](https://img.shields.io/badge/Requests-HTTP%20Client-555555)
![CSV](https://img.shields.io/badge/CSV-Data%20Storage-555555)

| 구분 | 사용 기술 |
| --- | --- |
| Language | Python |
| Data Processing | `pandas`, `numpy` |
| Crawling / API | `requests`, `urllib`, `BeautifulSoup4` |
| Visualization | `matplotlib`, `koreanize-matplotlib` |
| Data Storage | CSV 파일 |
| External Services | Circle Chart, Apple iTunes Search API |

## 🚀 Getting Started

### Prerequisites

아래 프로그램이 설치되어 있어야 합니다.

- Python 3.x
- pip
- 인터넷 연결

> 이 프로젝트는 Circle Chart와 Apple iTunes Search API를 직접 호출합니다. 실행 시 외부 네트워크 접근이 필요하며, 크롤링 대상 서비스의 이용약관과 요청 제한을 확인한 뒤 사용해 주세요.

### Installation

프로젝트 폴더로 이동합니다.

```bash
cd 07_Numpy/team-project
```

가상환경을 생성합니다.

```bash
python -m venv .venv
```

가상환경을 활성화합니다.

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

필요한 패키지를 설치합니다.

```bash
pip install pandas numpy requests beautifulsoup4 matplotlib koreanize-matplotlib
```

## ▶️ Usage

### 메인 파이프라인 (순서대로 실행)

#### 1. 차트 주차 기간 수집

Circle Chart 주간 차트 페이지에서 주차 코드와 기간을 수집해 `data/period.csv`를 생성합니다.

```bash
python crawl_period.py
```

생성 파일: `data/period.csv`

#### 2. 주간 앨범 차트 랭킹 수집

Circle Chart API에서 주차별 앨범 차트 순위, 점수, 앨범명, 아티스트명을 수집합니다.

```bash
python crawl_ranking.py
```

생성 파일: `data/ranking_list.csv`

> `crawl_ranking.py`는 요청 사이에 `1.0~2.5초`의 랜덤 대기 시간을 둡니다. CSV에 append 방식으로 저장하므로 재실행 전 기존 파일 백업 또는 초기화 여부를 확인해 주세요.

#### 3. 아티스트별 앨범 목록 수집

Apple iTunes Search API를 통해 아티스트별 전체 앨범 목록과 발매일을 수집합니다.

```bash
python find_album.py
```

생성 파일: `data/albums_by_artist.csv`

#### 4. 차트 성과 분석 및 시각화

앨범 발매일과 차트 진입 기간을 결합해 1집 대비 2집 성과를 분석합니다.

```bash
python extract_artists.py
```

생성 파일:
- `data/success_df.csv` — 발매 10일 이내 차트 진입한 1집 아티스트 목록
- `data/success_sophomore.csv` — 해당 아티스트의 2집 차트 데이터
- `data/output/chart/앨범 첫 차트인 순위 1집 대비 2집 변화.png`

#### 5. 추가 시각화 (박스플롯 / 바 차트)

1집·2집 첫 차트인 순위, 최고 순위, 차트 유지 기간을 시각화합니다.  
`extract_artists.py` 실행 후 생성된 `success_df.csv`, `success_sophomore.csv`를 사용합니다.

```bash
python draw_graph.py
```

---

### 보조 스크립트 (선택 실행)

메인 파이프라인과 독립적으로 실행 가능한 유틸리티 스크립트입니다.

| 스크립트 | 설명 | 출력 파일 |
| --- | --- | --- |
| `filter_artists.py` | 10위권 진입 아티스트만 필터링 | `data/no10_artists.csv` |
| `map_release_date.py` | 10위권 아티스트의 iTunes 최초 발매일 매핑 | `data/no10_artists_release_date.csv` |

> `map_release_date.py`는 `filter_artists.py` 실행 후 사용합니다.

## 📁 Project Structure

```text
team-project/
├── README.md
├── crawl_period.py          # Circle Chart 주차 기간 수집
├── crawl_ranking.py         # Circle Chart 주간 앨범 순위 수집
├── find_album.py            # iTunes API로 아티스트별 앨범 목록 수집
├── extract_artists.py       # 1집/2집 차트 성과 분석 및 파이 차트 저장
├── draw_graph.py            # 박스플롯·바 차트 시각화
├── filter_artists.py        # 10위권 아티스트 필터링 (보조)
├── map_release_date.py      # 10위권 아티스트 발매일 매핑 (보조)
├── utils/
│   ├── __init__.py
│   └── apple_api.py         # iTunes API 공통 함수
└── data/
    ├── ranking_list.csv
    ├── period.csv
    ├── albums_by_artist.csv
    ├── no10_artists.csv
    ├── no10_artists_release_date.csv
    ├── success_df.csv
    ├── success_sophomore.csv
    └── output/
        └── chart/
            └── *.png
```

## 🔐 Environment Variables

현재 프로젝트는 별도의 `.env` 파일이나 환경 변수를 요구하지 않습니다.

외부 API 키도 필요하지 않으며, 아래 공개 엔드포인트와 페이지를 직접 요청합니다.

```text
https://circlechart.kr/page_chart/onoff.circle
https://circlechart.kr/data/api/chart/onoff
https://itunes.apple.com/search
https://itunes.apple.com/lookup
```

## ⚠️ Notes

- CSV 파일과 일부 데이터 값에는 한글이 포함되어 있으므로 `UTF-8` 또는 `UTF-8-SIG` 인코딩을 권장합니다.
- `crawl_ranking.py`는 기존 CSV에 데이터를 누적(append)합니다. 재실행 전 `data/ranking_list.csv` 상태를 확인해 주세요.
- 외부 서비스 응답 구조가 변경되면 수집 로직이 동작하지 않을 수 있습니다.

## 📄 License

현재 저장소에는 별도의 라이선스 파일이 포함되어 있지 않습니다.
