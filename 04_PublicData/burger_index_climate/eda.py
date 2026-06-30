import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import csv
import os

# ── 상수 ──────────────────────────────────────────────────────────────
WEATHER_PATH        = './data/weather_data.csv'
PRODUCTION_PATH     = './data/yield_data.xlsx'
OUTPUT_DIR          = './data/output'

OPTIMUM_TEMP_MIN    = 15.0   # 적정온도 하한
OPTIMUM_TEMP_MAX    = 20.0   # 적정온도 상한
HIGHTEMP_MILD_MIN   = 20.1   # 온난 고온 구간 하한 (20.1~25°C)
HIGHTEMP_SEVERE_MIN = 25.0   # 강 고온 기준 (≥25°C)
HEAVY_RAIN_MIN      = 80.0   # 집중호우 기준 (≥80mm)


def _savefig(filename: str):
    plt.savefig(f'{OUTPUT_DIR}/{filename}.png', bbox_inches='tight')


def _extract_years(raw: pd.Series) -> list:
    return pd.Series(raw.index).astype(str).str.extract(r'(\d{4})')[0].tolist()


# ── 생산량 EDA ────────────────────────────────────────────────────────
def run_production_eda():
    print("\n=== [EDA-1] 상추 생산량 추이 ===")
    df = pd.read_excel(PRODUCTION_PATH)

    raw_total  = df.iloc[1:, 2::8].sum(axis=0)
    raw_noji   = df.iloc[1:, 4::8].sum(axis=0)
    raw_siseol = df.iloc[1:, 7::8].sum(axis=0)

    years_total  = _extract_years(raw_total)
    years_noji   = _extract_years(raw_noji)
    years_siseol = _extract_years(raw_siseol)

    plt.figure()
    sns.barplot(x=years_total, y=raw_total.values)
    plt.title('상추 생산량 (톤) 추이')
    _savefig('상추_생산량_톤_추이')
    plt.show()

    plt.figure()
    sns.barplot(x=years_noji, y=raw_noji.values)
    plt.title('노지상추 10a당 생산량 (kg) 추이')
    _savefig('노지상추_10a당_생산량_추이')
    plt.show()

    plt.figure()
    sns.barplot(x=years_siseol, y=raw_siseol.values)
    plt.title('시설상추 10a당 생산량 (kg) 추이')
    _savefig('시설상추_10a당_생산량_추이')
    plt.show()

    plt.figure()
    sns.lineplot(x=years_noji,   y=raw_noji.values,   color='skyblue', marker='o', label='노지상추')
    sns.lineplot(x=years_siseol, y=raw_siseol.values, color='salmon',  marker='s', label='시설상추')
    plt.title('상추 재배방식별 10a당 생산량 (kg) 추이')
    plt.xlabel('연도')
    plt.ylabel('생산량 (kg)')
    plt.legend()
    _savefig('재배방식별_생산량_추이')
    plt.show()


# ── 기상 EDA ──────────────────────────────────────────────────────────
def run_weather_eda():
    print("\n=== [EDA-2] 기상 분포 분석 ===")

    low_temp     = {}
    optimum_temp = {}
    high_temp    = {}   # 20.1 ~ 25°C
    high_tempp   = {}   # ≥ 25°C
    heavy_rain   = {}
    all_years    = set()

    with open(WEATHER_PATH, encoding='cp949') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            year = row[2][:4]
            all_years.add(year)

            if row[3]:
                temp = float(row[3])
                if OPTIMUM_TEMP_MIN <= temp <= OPTIMUM_TEMP_MAX:
                    optimum_temp[year] = optimum_temp.get(year, 0) + 1
                elif HIGHTEMP_MILD_MIN <= temp < HIGHTEMP_SEVERE_MIN:
                    high_temp[year] = high_temp.get(year, 0) + 1
                elif temp >= HIGHTEMP_SEVERE_MIN:
                    high_tempp[year] = high_tempp.get(year, 0) + 1
                else:
                    low_temp[year] = low_temp.get(year, 0) + 1

            if row[4] and float(row[4]) >= HEAVY_RAIN_MIN:
                heavy_rain[year] = heavy_rain.get(year, 0) + 1

    years_sorted = sorted(all_years)
    high_all = {y: high_temp.get(y, 0) + high_tempp.get(y, 0) for y in years_sorted}

    # 적온기온 빈도수
    xv, yv = zip(*[(y, optimum_temp.get(y, 0)) for y in years_sorted])
    plt.figure()
    plt.bar(xv, yv, color='#2ecc71', edgecolor='black', alpha=0.7)
    plt.title('적온기온 빈도수 (15~20°C)')
    _savefig('적온기온_빈도수')
    plt.show()

    # 고온 빈도수
    xv, yv = zip(*[(y, high_all[y]) for y in years_sorted])
    plt.figure()
    plt.bar(xv, yv, color='salmon', edgecolor='black', alpha=0.7)
    plt.title('고온 빈도수 (≥20.1°C)')
    _savefig('고온_빈도수')
    plt.show()

    # 집중호우 빈도수
    xv, yv = zip(*[(y, heavy_rain.get(y, 0)) for y in years_sorted])
    plt.figure()
    plt.bar(xv, yv, color='salmon', edgecolor='black', alpha=0.7)
    plt.title('집중호우 빈도수 (≥80mm)')
    _savefig('집중호우_빈도수')
    plt.show()

    # 연간 온도 분포 (%)
    df_temp = pd.DataFrame({
        '15℃ 미만':   low_temp,
        '15℃ ~ 20℃': optimum_temp,
        '20℃ 초과':   high_all,
    })
    df_pct = df_temp.divide(df_temp.sum(axis=1), axis=0) * 100

    ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6),
                     color=['#3498db', '#2ecc71', 'orange'])
    plt.title('연간 온도 분포 (%)', fontsize=15)
    plt.xlabel('Year')
    plt.ylabel('Percentage (%)')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    plt.xticks(rotation=0)

    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x_pos, y_pos = p.get_xy()
        if height > 0:
            ax.text(x_pos + width / 2, y_pos + height / 2,
                    f'{height:.1f}%', ha='center', va='center')

    plt.tight_layout()
    _savefig('연간_온도_분포')
    plt.show()


# ── 진입점 ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_production_eda()
    run_weather_eda()
