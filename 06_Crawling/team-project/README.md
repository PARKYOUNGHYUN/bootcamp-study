# Saramin Job Crawling & Analysis Pipeline

> 사람인(Saramin) 채용공고를 산업군과 키워드 기준으로 수집하고, 공고 상세 본문까지 수집한 뒤 기술 키워드 빈도, 지역별·경력별 분포, 워드클라우드 등을 시각화하는 Python 파이프라인 프로젝트입니다.

## ✨ Key Features

**크롤링 파이프라인**
- **산업군 코드 수집**: 사람인 Open API 가이드의 산업/업종 코드표를 파싱해 `data/00_code.csv`로 저장합니다.
- **채용공고 목록 크롤링**: 산업군 코드와 키워드(`ai`, `빅데이터`, `python`, `llm`) 조합으로 전체 산업군의 채용공고 목록을 수집합니다.
- **CSV 병합 및 중복 제거**: 키워드별 결과를 산업군별 CSV로 합치고, 전체 공고 목록(`data/01_all.csv`)을 생성합니다.
- **공고 상세 페이지 수집**: Selenium으로 공고 상세 페이지에 접근해 본문 텍스트를 `data/crolling_detail.csv`에 누적 저장합니다.
- **실패 로그 관리**: 상세 페이지 수집 실패 시 `data/error_log.txt`에 공고 ID와 오류 메시지를 기록합니다.

**분석 파이프라인**
- **목록 + 상세 병합**: 산업군별 공고 목록과 상세 본문을 join해 분석용 CSV(`data/04_merged_details_*.csv`)를 생성합니다.
- **기술 키워드 빈도 분석**: 공고 본문에서 기술 스택·자격증 등 주요 키워드 등장 횟수를 집계하고 막대 차트로 시각화합니다.
- **채용공고 통계 시각화**: 키워드별 산업군 비율, 지역별 분포, 경력별 비율, 경력×고용형태 분포를 차트로 저장합니다.
- **워드클라우드 생성**: 공고 메타데이터의 기술 태그를 워드클라우드 이미지로 저장합니다.

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?logo=pandas&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-Browser%20Automation-43B02A?logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20Parsing-4B8BBE)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C)

| 구분 | 사용 기술 |
| --- | --- |
| Language | Python |
| Crawling | `urllib`, `BeautifulSoup4`, `Selenium` |
| Data Processing | `pandas`, `csv` |
| Visualization | `matplotlib`, `seaborn`, `koreanize-matplotlib` |
| WordCloud | `wordcloud`, `Pillow`, `numpy` |
| Browser | Google Chrome, ChromeDriver 또는 Selenium Manager |
| Data Storage | CSV 파일 |

## 🚀 Getting Started

### Prerequisites

아래 프로그램이 설치되어 있어야 합니다.

- Python 3.x
- Google Chrome

> Selenium 4.6 이상은 Selenium Manager를 통해 ChromeDriver를 자동으로 관리할 수 있습니다.

### Installation

프로젝트 폴더로 이동합니다.

```bash
cd 06_Crawling/team-project
```

가상환경을 생성하고 활성화합니다.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

필요한 패키지를 설치합니다.

```bash
pip install pandas beautifulsoup4 selenium matplotlib seaborn koreanize-matplotlib wordcloud Pillow numpy
```

## ▶️ Usage

스크립트를 순서대로 실행해 파이프라인을 구성합니다.

### 크롤링 파이프라인

#### 1. 산업군 코드 수집

```bash
python code_list.py
```

생성: `data/00_code.csv`

#### 2. 채용공고 목록 수집

```bash
python announcement_list.py
```

생성 예시:

```
data/IT·웹·통신_ai.csv
data/IT·웹·통신_python.csv
data/제조·화학_llm.csv
...
```

#### 3. 목록 데이터 병합

```bash
python merge_df.py
```

생성:

```
data/02_IT·웹·통신.csv
data/02_제조·화학.csv
...
data/01_all.csv
```

#### 4. 상세 공고 본문 수집

```bash
python announcement_details.py
```

생성 및 갱신:

```
data/crolling_detail.csv
data/error_log.txt
```

### 분석 파이프라인

#### 5. 목록 + 상세 병합

```bash
python merge_list_details.py
```

생성: `data/04_merged_details_{산업군}.csv` × 10개

#### 6. 키워드 맵 CSV 생성

```bash
python words_df.py
```

생성: `data/03_채용 공고 매칭 역량 키워드 리스트.csv`

#### 7. 기술 키워드 빈도 분석

```bash
python detail_filtering.py
```

IT·웹·통신 산업군의 공고 본문에서 기술 키워드 등장 빈도를 막대 차트로 출력합니다.

#### 8. 채용공고 통계 시각화

```bash
python jobs_list_by_keyword.py   # 키워드별 산업군 공고 비율
python jobs_list_by_region.py    # 산업군별 지역 분포
python jobs_list_by_refined.py   # 산업군별 경력 비율
python jobs_list_by_career.py    # 경력별 고용형태 분포
```

저장 위치: `data/output/chart/`

#### 9. 워드클라우드 생성

```bash
python pick_words.py
```

저장 위치: `data/output/wordCloud/`

## 📁 Project Structure

```text
team-project/
├── README.md
├── utils.py                      # 공통 유틸리티 함수
│
├── [크롤링 파이프라인]
├── code_list.py                  # 1단계: 산업군 코드 수집
├── announcement_list.py          # 2단계: 공고 목록 크롤링
├── merge_df.py                   # 3단계: 목록 병합
├── announcement_details.py       # 4단계: 상세 페이지 크롤링
│
├── [분석 파이프라인]
├── merge_list_details.py         # 5단계: 목록 + 상세 병합
├── words_df.py                   # 키워드 맵 CSV 저장
├── detail_filtering.py           # 기술 키워드 빈도 분석
├── jobs_list_by_keyword.py       # 키워드별 공고 비율 차트
├── jobs_list_by_region.py        # 지역별 공고 분포 차트
├── jobs_list_by_refined.py       # 경력별 비율 차트
├── jobs_list_by_career.py        # 경력 × 고용형태 차트
├── pick_words.py                 # 워드클라우드 생성
│
├── .vscode/
│   ├── settings.json
│   └── launch.json
│
└── data/
    ├── 00_code.csv
    ├── 01_all.csv
    ├── 02_{산업군}.csv              × 10
    ├── 03_채용 공고 매칭 역량 키워드 리스트.csv
    ├── 04_merged_details_{산업군}.csv × 10
    ├── {산업군}_{키워드}.csv        × 40
    ├── crolling_detail.csv
    ├── droped_crolling_detail.csv
    ├── error_log.txt
    ├── image/
    │   └── cloud.png
    └── output/
        ├── chart/
        │   ├── 경력에 따른 고용형태/
        │   ├── 신입 vs 경력vs 경력무관 비율/
        │   ├── 지역별 채용공고 비교/
        │   └── 키워드별 채용공고 수 비교/
        └── wordCloud/
```

| 파일/폴더 | 설명 |
| --- | --- |
| `utils.py` | 공통 유틸리티 함수 (`classify_refined` 등) |
| `code_list.py` | 사람인 산업/업종 코드표를 파싱해 `00_code.csv`를 생성합니다. |
| `announcement_list.py` | 전체 산업군과 키워드 기준으로 채용공고 목록을 수집합니다. |
| `merge_df.py` | 키워드별 목록 CSV를 산업군별/전체 CSV로 병합하고 중복을 제거합니다. |
| `announcement_details.py` | Selenium으로 공고 상세 페이지 본문을 수집합니다. |
| `merge_list_details.py` | 공고 목록과 상세 본문을 산업군별로 병합합니다. |
| `words_df.py` | 역량 키워드 맵을 CSV로 저장합니다. |
| `detail_filtering.py` | 공고 본문의 기술 키워드 등장 빈도를 분석합니다. |
| `jobs_list_by_keyword.py` | 키워드별 산업군 공고 비율 파이 차트를 생성합니다. |
| `jobs_list_by_region.py` | 산업군별 지역 분포 막대 차트를 생성합니다. |
| `jobs_list_by_refined.py` | 산업군별 신입/경력/경력무관 비율 파이 차트를 생성합니다. |
| `jobs_list_by_career.py` | 경력 구분별 정규직/계약직 분포 막대 차트를 생성합니다. |
| `pick_words.py` | 기술 태그 워드클라우드 이미지를 생성합니다. |
| `data/` | 크롤링 입출력 CSV, 분석 결과, 차트 이미지를 저장하는 디렉터리입니다. |

## ⚠️ Notes

- 크롤링 대상 사이트의 이용약관과 `robots.txt` 정책을 확인한 뒤 실행해 주세요.
- `announcement_details.py`는 상세 페이지 요청 간 `2.5~4.5초`의 랜덤 대기 시간을 사용하고, 100건마다 1분 휴식, 500건마다 드라이버를 재시작합니다.
- 상세 수집 스크립트는 `data/crolling_detail.csv`에 append 방식으로 데이터를 누적합니다. 재실행 전 기존 파일 백업 여부를 확인해 주세요.
- 일부 데이터 파일명과 컬럼 값은 한글을 포함하므로 CSV를 열 때 `UTF-8` 또는 `UTF-8-SIG` 인코딩을 권장합니다.
- VSCode에서 실행할 때는 `.vscode/launch.json`의 `"cwd": "${fileDirname}"` 설정으로 각 스크립트가 자신의 디렉터리를 기준으로 `./data/` 경로를 참조합니다. 터미널에서 직접 실행할 경우 `team-project/` 디렉터리에서 실행해야 합니다.
- `pick_words.py`는 `c:\Windows\Fonts\malgun.ttf` (Windows 맑은 고딕)를 폰트로 사용합니다. macOS/Linux 환경에서는 해당 경로를 수정해야 합니다.

## 📄 License

현재 저장소에는 별도의 라이선스 파일이 포함되어 있지 않습니다.
