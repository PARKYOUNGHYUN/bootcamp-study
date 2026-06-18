# 🥤 Coca-Cola Logo History

코카콜라 로고의 변천사를 연도별 이미지로 살펴볼 수 있는 Python GUI 학습 프로젝트입니다.

> Python 기초 문법, 함수 분리, 이벤트 처리, 이미지 로딩, Tkinter GUI 구성을 연습하기 위한 예제입니다.

## ✨ Key Features

- 코카콜라 로고 변천사를 연도별로 확인
- `이전`, `메인`, `다음` 버튼을 통한 간단한 GUI 탐색
- PNG/JPG 이미지 파일 자동 로딩
- 로고별 적용 기간을 화면에 표시
- Python 기본 GUI 라이브러리인 `Tkinter`와 이미지 처리 라이브러리 `Pillow` 활용

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)
![Pillow](https://img.shields.io/badge/Pillow-Image%20Processing-green?style=for-the-badge)

| 구분 | 기술 |
|---|---|
| Language | Python |
| GUI | Tkinter |
| Image Processing | Pillow |
| Package Manager | pip |

## 🚀 Getting Started

### Prerequisites

아래 프로그램이 설치되어 있어야 합니다.

```bash
python --version
pip --version
```

권장 환경:

```text
Python 3.9+
```

> Windows/macOS의 일반 Python 배포판에는 `tkinter`가 기본 포함되어 있습니다.  
> Linux 환경에서 `tkinter`가 없다면 별도 설치가 필요할 수 있습니다.

Ubuntu/Debian 예시:

```bash
sudo apt install python3-tk
```

### Installation

이미지 처리를 위해 `Pillow`를 설치합니다.

```bash
pip install pillow
```

### Usage

아래 명령어로 프로그램을 실행합니다.

```bash
python main.py
```

실행 후 GUI 창에서 다음 버튼을 사용할 수 있습니다.

```text
← 이전   메인   다음 →
```

> `main.py`는 `images/` 폴더를 상대 경로로 참조합니다.  
> 따라서 반드시 `coca_cola_history` 디렉토리 안에서 실행하는 것을 권장합니다.

## 📁 Project Structure

```text
01_PythonBasic/
└── coca_cola_history/
    ├── main.py
    └── images/ # 로고 파일
```

### 주요 파일 설명

| 파일/폴더 | 설명 |
|---|---|
| `main.py` | Tkinter GUI 실행 파일 |
| `images/` | 코카콜라 로고 이미지 리소스 폴더 |
| `images/main.png` | 메인 화면 이미지 |
| `images/{year}.png`, `images/{year}.jpg` | 연도별 로고 이미지 |

## ⚙️ Core Logic

`main.py`는 다음 흐름으로 동작합니다.

1. `CHANGE_YEARS` 리스트에 로고 변경 시작 연도를 저장합니다.
2. `click_next()`와 `click_prev()` 함수로 현재 로고 인덱스를 이동합니다.
3. `view_logo()` 함수가 이미지와 연도 텍스트를 화면에 표시합니다.
4. `read_image()` 함수가 `images/` 폴더에서 PNG 이미지를 우선 로딩하고, 없으면 JPG 파일을 로딩합니다.
5. Tkinter의 `Label`, `Button`, `pack()`을 사용해 GUI를 구성합니다.

## 🔐 Environment Variables

이 프로젝트는 별도의 환경 변수를 사용하지 않습니다.

`.env` 파일 설정이 필요하지 않습니다.

```env
# No environment variables required
```

## 📌 Notes

- 외부 API나 데이터베이스는 사용하지 않습니다.
- 모든 로고 이미지는 로컬 `images/` 폴더에서 불러옵니다.
- 이미지 크기는 실행 중 `700x300`으로 리사이즈되어 표시됩니다.

## 📄 License

현재 저장소에 라이선스 파일이 포함되어 있지 않습니다.

프로젝트를 공개 배포할 예정이라면 `MIT`, `Apache-2.0`, `GPL-3.0` 등 목적에 맞는 라이선스를 추가하는 것을 권장합니다.
