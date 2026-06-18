# 🏔️ Olympic Host Impact

동계 올림픽 개최국의 개최 전후 GDP 변화를 분석하고 시각화하는 데이터 분석 노트북 프로젝트입니다.

## ✨ Key Features

- 동계 올림픽 개최국 데이터를 기반으로 개최 연도별 GDP 추이 분석
- 개최 전후 5년(`WINDOW = 5`) 범위의 GDP 윈도우 데이터 생성
- 개최 연도를 기준점으로 한 GDP 성장률 계산
- 선 그래프와 히트맵을 활용한 GDP 변화 시각화
- 한국어 그래프 출력을 위한 `koreanize-matplotlib` 적용

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square)
![Seaborn](https://img.shields.io/badge/Seaborn-4B8BBE?style=flat-square)

## 🚀 Getting Started

### Prerequisites

아래 프로그램이 설치되어 있어야 합니다.

- Python 3.10+
- Jupyter Notebook 또는 JupyterLab
- pip 또는 conda

### Installation

프로젝트 디렉토리로 이동합니다.

```bash
cd 03_DataVisualization/olympic_host_impact
```

필요한 패키지를 설치합니다.

```bash
pip install numpy pandas seaborn matplotlib koreanize-matplotlib jupyter
```

conda 환경을 사용하는 경우 다음과 같이 설치할 수 있습니다.

```bash
conda install numpy pandas seaborn matplotlib jupyter
pip install koreanize-matplotlib
```

### Usage

Jupyter Notebook을 실행합니다.

```bash
jupyter notebook main.ipynb
```

또는 JupyterLab을 사용하는 경우:

```bash
jupyter lab
```

노트북을 열고 위에서부터 셀을 순서대로 실행하면 GDP 분석 결과와 시각화 그래프를 확인할 수 있습니다.

## 📊 Analysis Overview

이 프로젝트는 다음 흐름으로 데이터를 분석합니다.

1. `olympic_games.csv`에서 동계 올림픽 개최국 데이터를 추출합니다.
2. `gdp.csv`에서 개최국에 해당하는 GDP 데이터를 필터링합니다.
3. 개최 연도를 기준으로 전후 5년의 GDP 데이터를 생성합니다.
4. 개최 연도 GDP를 기준값으로 삼아 상대 성장률을 계산합니다.
5. 선 그래프와 히트맵으로 국가별 GDP 변화 패턴을 시각화합니다.

> 현재 분석 대상은 1988년부터 2022년까지의 주요 동계 올림픽 개최국입니다.

## 📁 Project Structure

```text
olympic_host_impact/
├── main.ipynb
├── data/
│   ├── olympic_games.csv
│   └── gdp.csv
└── .vscode/
    └── settings.json
```

### 주요 파일 설명

| 경로 | 설명 |
| --- | --- |
| `main.ipynb` | 데이터 로드, 전처리, GDP 성장률 계산, 시각화를 수행하는 메인 노트북 |
| `data/olympic_games.csv` | 올림픽 개최 정보와 국가별 메달 데이터를 포함한 CSV 파일 |
| `data/gdp.csv` | 국가별 연도별 GDP 데이터 |
| `.vscode/settings.json` | VS Code Python/conda 환경 설정 |

## 🧾 Data

### `olympic_games.csv`

올림픽 연도, 개최 유형, 개최국, 개최 도시, 참가 선수 수, 참가국 수, 경기 수, 국가별 메달 정보를 포함합니다.

주요 컬럼:

```text
year, games_type, host_country, host_city, athletes, teams,
competitions, country, gold, silver, bronze
```

### `gdp.csv`

World Bank 형식의 국가별 GDP 시계열 데이터입니다.

주요 컬럼:

```text
Country Name, Country Code, Indicator Name, Indicator Code, 1960, ..., 2024
```

노트북에서는 `skiprows=4` 옵션을 사용해 실제 데이터 영역부터 읽습니다.

## ⚙️ Environment Variables

이 프로젝트는 별도의 환경 변수를 요구하지 않습니다.

`.env` 파일은 필요하지 않으며, 모든 분석은 로컬 CSV 파일을 기반으로 실행됩니다.

## 📈 Visualizations

노트북은 다음 시각화를 제공합니다.

- 국가별 GDP 절대값 추이 선 그래프
- 개최 연도 기준 GDP 성장률 선 그래프
- 개최 전후 GDP 성장률 히트맵

## 📝 Notes

- GDP 데이터의 국가명과 올림픽 데이터의 국가명이 다르기 때문에 `OLYMPIC_TO_GDP_NAME` 매핑을 사용합니다.
- 한국어 그래프 라벨 표시를 위해 `koreanize-matplotlib`이 필요합니다.
- 일부 개최국 데이터가 원본 CSV에서 누락된 경우, 노트북 내부에서 보정 데이터를 추가합니다.

## 📄 License

현재 저장소에 명시된 라이선스 파일이 없습니다.

프로젝트를 공개하거나 재사용할 계획이라면 `MIT`, `Apache-2.0`, `GPL-3.0` 등 목적에 맞는 라이선스를 추가하는 것을 권장합니다.
