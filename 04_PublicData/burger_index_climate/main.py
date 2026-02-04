import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import csv
import os

# ── 상수 ──────────────────────────────────────────────────────────────
WEATHER_PATH     = './data/weather_data.csv'
PRODUCTION_PATH  = './data/yield_data.xlsx'
OUTPUT_DIR       = './data/output'

CULTIVATION_MONTHS    = ['03', '04', '05', '09', '10', '11']
OPTIMUM_TEMP_MIN      = 15.0   # 적정온도 하한
OPTIMUM_TEMP_MAX      = 20.0   # 적정온도 상한 / 고온 기준선 (≥20°C)
HIGHTEMP_MILD_MIN     = 20.1   # 온난 고온 구간 하한 (20.1~25°C)
HIGHTEMP_SEVERE_MIN   = 25.0   # 강 고온 기준 (≥25°C)
HEAVY_RAIN_MIN        = 80.0   # 집중호우 기준 (≥80mm)
RAIN_STREAK_FREQ_MIN  = 4      # 연속강우 빈도 카운트 기준 (연속 ≥4일)
RAIN_STREAK_RISK_DAYS = 10     # 위험 임계 연속강우 (10일)
OUTLIER_THRESHOLD     = 500    # 10월 고온일수 이상치 제거 상한
PAST_YEARS_START      = 2015
PAST_YEARS_END        = 2019
RECENT_YEARS_START    = 2020
RECENT_YEARS_END      = 2024
WORST_YEARS_N         = 3

CROP_COLS = {'노지 상추': 4, '시설 상추': 7}


# ── 데이터 로더 ────────────────────────────────────────────────────────
def load_yield_series(col_offset: int) -> pd.Series:
    df  = pd.read_excel(PRODUCTION_PATH)
    raw = df.iloc[1:, col_offset::8].sum(axis=0)
    years = pd.Series(raw.index).astype(str).str.extract(r'(\d{4})')[0].astype(int)
    return pd.Series(raw.values, index=years, name='yield')


def _savefig(filename: str):
    plt.savefig(f'{OUTPUT_DIR}/{filename}.png', bbox_inches='tight')


# ── 분석 1: 기본 기상 지표 × 생산량 상관계수 ──────────────────────────
def run_basic_weather_correlation(yield_series: pd.Series, crop_label: str):
    print(f"\n=== [1] 기본 기상 지표 × 생산량 상관계수 — {crop_label} ===")
    try:
        df_weather = pd.read_csv(WEATHER_PATH, encoding='cp949')
        df_weather.columns = [
            '지점', '지점명', '일시', '평균기온(°C)',
            '일강수량(mm)', '합계 일조시간(hr)', '합계 일사량(MJ/m2)'
        ]
        df_weather['일시'] = pd.to_datetime(df_weather['일시'])
        df_weather['연도'] = df_weather['일시'].dt.year.astype(int)
        df_weather['월']   = df_weather['일시'].dt.strftime('%m')
        df_weather = df_weather[df_weather['월'].isin(CULTIVATION_MONTHS)].copy().fillna(0)

        weather_results = []
        for (year, station), group in df_weather.groupby(['연도', '지점명']):
            temp  = group['평균기온(°C)']
            rain  = group['일강수량(mm)']
            sun   = group['합계 일조시간(hr)']
            solar = group['합계 일사량(MJ/m2)']

            optimum        = ((temp >= OPTIMUM_TEMP_MIN) & (temp <= OPTIMUM_TEMP_MAX)).sum()
            high_temp_days = (temp > HIGHTEMP_SEVERE_MIN).sum()

            is_rain      = rain > 0
            rain_groups  = (is_rain != is_rain.shift()).cumsum()
            streaks      = group.groupby(rain_groups)['일강수량(mm)'].count()
            rain_streaks = streaks[is_rain.groupby(rain_groups).first()]
            max_streak   = rain_streaks.max() if not rain_streaks.empty else 0

            weather_results.append({
                '연도': year, 'optimum': optimum, 'high_temp_days': high_temp_days,
                'max_streak': max_streak, 'total_sun': sun.sum(), 'total_solar': solar.sum()
            })

        df_stats = pd.DataFrame(weather_results).groupby('연도').mean()
        df_final = df_stats.join(yield_series, how='inner').fillna(0)

        print("--- 상관계수 ---")
        print(df_final.corr()['yield'].sort_values(ascending=False))

        slug = crop_label.replace(' ', '_')
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        sns.regplot(data=df_final, x='max_streak', y='yield', color='red')
        plt.title(f'연속 강우와 생산량 — {crop_label}')
        plt.subplot(1, 2, 2)
        sns.regplot(data=df_final, x='total_solar', y='yield', color='orange')
        plt.title(f'총 일사량과 생산량 — {crop_label}')
        plt.tight_layout()
        _savefig(f'{slug}_기본상관_연속강우_일사량')
        plt.show()
    except Exception as e:
        print(f"run_basic_weather_correlation ({crop_label}) 오류: {e}")


# ── 분석 2: 월별 고온일수 × 생산량 상관계수 ──────────────────────────
def run_monthly_hightemp_correlation(yield_series: pd.Series, crop_label: str):
    print(f"\n=== [2] 월별 고온일수 × 생산량 상관계수 — {crop_label} ===")
    try:
        yield_dict = yield_series.to_dict()  # {int_year: float_yield}

        monthly_temp_counts = {str(m).zfill(2): {} for m in range(1, 13)}
        all_years = set()

        with open(WEATHER_PATH, encoding='cp949') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if not row[3]:
                    continue
                year  = row[2][:4]
                month = row[2][5:7]
                temp  = float(row[3])
                all_years.add(year)
                if temp >= OPTIMUM_TEMP_MAX:
                    monthly_temp_counts[month][year] = monthly_temp_counts[month].get(year, 0) + 1

        years_list   = sorted(list(all_years))
        correlations = {}

        for month, year_counts in monthly_temp_counts.items():
            temp_counts_list, yield_vals = [], []
            for y in years_list:
                if int(y) in yield_dict:
                    temp_counts_list.append(year_counts.get(y, 0))
                    yield_vals.append(yield_dict[int(y)])
            if len(temp_counts_list) > 1:
                correlations[month] = pd.Series(temp_counts_list).corr(pd.Series(yield_vals))

        slug    = crop_label.replace(' ', '_')
        corr_df = pd.Series(correlations)

        plt.figure(figsize=(12, 6))
        corr_df.plot(kind='bar', color='skyblue', edgecolor='navy')
        plt.axhline(0, color='red', linewidth=1, linestyle='--')
        plt.title(f'월별 20도 이상 일수와 생산량 간의 상관관계 — {crop_label}', fontsize=15)
        plt.xlabel('월 (Month)', fontsize=12)
        plt.ylabel('상관계수 (Correlation)', fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        _savefig(f'{slug}_월별_고온일수_상관계수')
        plt.show()

        print("--- 월별 상관계수 (음수가 클수록 생산량 감소에 큰 영향) ---")
        print(corr_df.sort_values())

        oct_data = [
            {'temp_days': monthly_temp_counts['10'].get(y, 0), 'yield': yield_dict[int(y)]}
            for y in years_list if int(y) in yield_dict
        ]
        df_oct = pd.DataFrame(oct_data)

        # 10월 산점도 — 이상치 제거 전
        plt.figure(figsize=(8, 6))
        sns.regplot(x='temp_days', y='yield', data=df_oct, color='orange')
        plt.title(f'10월 고온 일수와 생산량 산점도 — {crop_label}', fontsize=14)
        plt.xlabel('10월 중 20도 이상 일수')
        plt.ylabel('10a당 생산량 (kg)')
        plt.grid(True)
        _savefig(f'{slug}_10월_고온일수_이상치전')
        plt.show()

        # 10월 산점도 — 이상치 제거 후
        df_oct_filtered = df_oct[df_oct['temp_days'] < OUTLIER_THRESHOLD]
        corr_before     = df_oct.corr().iloc[0, 1]
        corr_after      = df_oct_filtered.corr().iloc[0, 1]
        print(f"이상치 제거 전 상관계수: {corr_before:.4f}")
        print(f"이상치 제거 후 상관계수: {corr_after:.4f}")

        plt.figure(figsize=(8, 6))
        sns.regplot(x='temp_days', y='yield', data=df_oct_filtered,
                    scatter_kws={'s': 50}, line_kws={'color': 'red'})
        plt.title(f'10월 고온 일수와 생산량 (이상치 제거 후) — {crop_label}', fontsize=14)
        plt.xlabel('10월 중 20도 이상 일수')
        plt.ylabel('10a당 생산량 (kg)')
        plt.grid(True)
        _savefig(f'{slug}_10월_고온일수_이상치후')
        plt.show()

        # 5월·10월 상관 히트맵
        may_oct_data = [
            {
                '05월_고온일수': monthly_temp_counts['05'].get(y, 0),
                '10월_고온일수': monthly_temp_counts['10'].get(y, 0),
                '생산량': yield_dict[int(y)]
            }
            for y in years_list if int(y) in yield_dict
        ]
        df_may_oct = pd.DataFrame(may_oct_data)
        print(df_may_oct[['05월_고온일수', '10월_고온일수', '생산량']].corr())

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            df_may_oct[['05월_고온일수', '10월_고온일수', '생산량']].corr(),
            annot=True, cmap='RdYlGn', center=0
        )
        plt.title(f'기온 변화와 생산량 상관관계 분석 — {crop_label}')
        _savefig(f'{slug}_5월10월_히트맵')
        plt.show()
    except Exception as e:
        print(f"run_monthly_hightemp_correlation ({crop_label}) 오류: {e}")


# ── 분석 3: 전월 기준 고온·집중호우 × 생산량 상관계수 ────────────────
def run_allmonth_extreme_correlation(yield_series: pd.Series, crop_label: str):
    print(f"\n=== [3] 전월 기준 고온·집중호우 × 생산량 상관계수 — {crop_label} ===")
    try:
        high_temp_dict  = {}
        heavy_rain_dict = {}

        with open(WEATHER_PATH, encoding='cp949') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                year_int = int(row[2][:4])
                if row[3] and float(row[3]) >= OPTIMUM_TEMP_MAX:
                    high_temp_dict[year_int] = high_temp_dict.get(year_int, 0) + 1
                if row[4] and float(row[4]) >= HEAVY_RAIN_MIN:
                    heavy_rain_dict[year_int] = heavy_rain_dict.get(year_int, 0) + 1

        df_stats = pd.DataFrame({
            'high_20_plus': pd.Series(high_temp_dict),
            'heavy_rain':   pd.Series(heavy_rain_dict),
        }).fillna(0).sort_index()

        df_final = df_stats.join(yield_series, how='inner').fillna(0)
        print("--- 상관계수 ---")
        print(df_final.corr()['yield'])
    except Exception as e:
        print(f"run_allmonth_extreme_correlation ({crop_label}) 오류: {e}")


# ── 분석 4: 재배기 기상 상세 분석 ────────────────────────────────────
def run_detailed_cultivation_analysis(yield_series: pd.Series, crop_label: str) -> dict:
    print(f"\n=== [4] 재배기 기상 상세 분석 — {crop_label} ===")
    try:
        optimum_temp, high_temp, high_tempp         = {}, {}, {}
        max_streak_dict, streak_freq_dict           = {}, {}
        max_dry_streak_dict                         = {}
        precip_intensity_dict, precip_std_dict      = {}, {}
        annual_rain_values                          = {}
        current_rain_streak = current_dry_streak    = 0
        last_year = last_station                    = ""

        with open(WEATHER_PATH, encoding='cp949') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                station = row[1]
                year    = row[2][:4]
                month   = row[2][5:7]
                if month not in CULTIVATION_MONTHS:
                    continue

                if station != last_station or year != last_year:
                    current_rain_streak = current_dry_streak = 0
                    last_station, last_year = station, year

                if row[3]:
                    temp = float(row[3])
                    if OPTIMUM_TEMP_MIN <= temp <= OPTIMUM_TEMP_MAX:
                        optimum_temp[year] = optimum_temp.get(year, 0) + 1
                    elif HIGHTEMP_MILD_MIN <= temp < HIGHTEMP_SEVERE_MIN:
                        high_temp[year] = high_temp.get(year, 0) + 1
                    elif temp >= HIGHTEMP_SEVERE_MIN:
                        high_tempp[year] = high_tempp.get(year, 0) + 1

                raw_rain = row[4].strip()
                rain     = float(raw_rain) if raw_rain else 0.0

                if rain > 0:
                    annual_rain_values.setdefault(year, []).append(rain)
                    current_rain_streak += 1
                    current_dry_streak   = 0
                    if current_rain_streak > max_streak_dict.get(year, 0):
                        max_streak_dict[year] = current_rain_streak
                    if current_rain_streak == RAIN_STREAK_FREQ_MIN:
                        streak_freq_dict[year] = streak_freq_dict.get(year, 0) + 1
                else:
                    current_dry_streak  += 1
                    current_rain_streak  = 0
                    if current_dry_streak > max_dry_streak_dict.get(year, 0):
                        max_dry_streak_dict[year] = current_dry_streak

        for year, rains in annual_rain_values.items():
            precip_intensity_dict[year] = sum(rains) / len(rains)
            if len(rains) > 1:
                precip_std_dict[year] = np.std(rains)

        def _to_int_series(d: dict) -> pd.Series:
            return pd.Series({int(k): v for k, v in d.items()})

        df_stats = pd.DataFrame({
            'optimum':          _to_int_series(optimum_temp),
            'high_20_25':       _to_int_series(high_temp),
            'high_25_plus':     _to_int_series(high_tempp),
            'max_streak':       _to_int_series(max_streak_dict),
            'max_dry_streak':   _to_int_series(max_dry_streak_dict),
            'streak_freq':      _to_int_series(streak_freq_dict),
            'precip_intensity': _to_int_series(precip_intensity_dict),
            'precip_std':       _to_int_series(precip_std_dict),
        }).fillna(0).sort_index()

        df_stats = df_stats.join(yield_series, how='inner').fillna(0)

        print("--- 상관계수 ---")
        print(df_stats.corr()['yield'].sort_values())

        # 가뭄형 / 장마형 폭염 시나리오
        dry_heat = df_stats[
            (df_stats['high_20_25'] > df_stats['high_20_25'].mean()) &
            (df_stats['max_dry_streak'] > df_stats['max_dry_streak'].mean())
        ]
        wet_heat = df_stats[
            (df_stats['high_20_25'] > df_stats['high_20_25'].mean()) &
            (df_stats['max_streak'] > df_stats['max_streak'].mean())
        ]
        dry_mean = dry_heat['yield'].mean()
        wet_mean = wet_heat['yield'].mean()
        print(f"가뭄형 폭염 연도 생산량 평균: {dry_mean}")
        print(f"장마형 폭염 연도 생산량 평균: {wet_mean}")

        # 편차 분석 (변동계수)
        past_yield   = df_stats.loc[PAST_YEARS_START:PAST_YEARS_END,       'yield']
        recent_yield = df_stats.loc[RECENT_YEARS_START:RECENT_YEARS_END,   'yield']
        print(f"과거 변동계수: {past_yield.std() / past_yield.mean() * 100:.2f}%")
        print(f"최근 변동계수: {recent_yield.std() / recent_yield.mean() * 100:.2f}%")

        # 최악 3개년 분석
        worst_3_years    = df_stats.sort_values(by='yield').head(WORST_YEARS_N)
        worst_years_list = worst_3_years.index.tolist()
        normal_years     = df_stats.drop(worst_years_list)
        normal_avg       = normal_years.mean()

        print(f"\n📉 생산량 최악의 3개년: {worst_years_list}")
        print("-" * 50)
        for year in worst_years_list:
            year_data    = df_stats.loc[year]
            streak_diff  = (year_data['max_streak'] - normal_avg['max_streak'])  / normal_avg['max_streak']  * 100
            optimum_diff = (year_data['optimum']     - normal_avg['optimum'])     / normal_avg['optimum']     * 100
            yield_diff   = (year_data['yield']       - normal_avg['yield'])       / normal_avg['yield']       * 100
            print(f"[{year}년 집중 분석]")
            print(f"- 생산량: {year_data['yield']:.1f} (평년 대비 {yield_diff:+.1f}%)")
            print(f"- 최장 연속 강우({year_data['max_streak']}일): 평년 대비 {streak_diff:+.1f}% 증가")
            print(f"- 적정 온도 일수({year_data['optimum']}일): 평년 대비 {optimum_diff:+.1f}% 변화")
            print("-" * 30)

        comparison_df = pd.DataFrame({
            '평년 평균': normal_avg,
            f'최악의 해({worst_years_list[0]})': df_stats.loc[worst_years_list[0]]
        }).drop('yield')
        print(comparison_df)

        print("\n--- 최악의 해들 간의 기상 지표 ---")
        print(df_stats.loc[worst_years_list].drop('yield', axis=1))

        # max_streak × yield 회귀 플롯
        slug = crop_label.replace(' ', '_')
        plt.figure(figsize=(10, 6))
        sns.regplot(x='max_streak', y='yield', data=df_stats, color='#e74c3c',
                    line_kws={'color': 'black', 'ls': '--'})
        plt.title(f'연속 강우일수 증가에 따른 생산량 변화 — {crop_label}', fontsize=14)
        plt.xlabel('최장 연속 강우일수 (일)')
        plt.ylabel('생산량')
        plt.axvline(x=RAIN_STREAK_RISK_DAYS, color='gray', linestyle=':',
                    label=f'위험 임계점({RAIN_STREAK_RISK_DAYS}일)')
        plt.legend()
        _savefig(f'{slug}_연속강우_생산량')
        plt.show()

        return {
            'df_stats': df_stats,
            'dry_mean': dry_mean,
            'wet_mean': wet_mean,
            'corr':     df_stats.corr()['yield'],
        }
    except Exception as e:
        print(f"run_detailed_cultivation_analysis ({crop_label}) 오류: {e}")
        return {}


# ── 통합 시각화 (노지 + 시설 결합) ───────────────────────────────────
def plot_correlation_comparison(noji_corr: pd.Series, siseol_corr: pd.Series):
    metric_map = {
        '강수변동성': 'precip_std',
        '연속강우':   'max_streak',
        '고온빈도':   'high_20_25',
        '적정온도':   'optimum',
    }
    labels = list(metric_map.keys())
    cols   = list(metric_map.values())

    df_corr = pd.DataFrame({
        '지표':     labels,
        '노지 상추': [noji_corr[c]   for c in cols],
        '시설 상추': [siseol_corr[c] for c in cols],
    }).set_index('지표')

    df_corr.plot(kind='barh', figsize=(10, 6), color=['#3498db', '#e74c3c'])
    plt.axvline(0, color='black', linewidth=0.8)
    plt.title('재배 방식별 기상 지표-생산량 상관계수 비교', fontsize=15)
    plt.xlabel('상관계수 (Correlation)')
    plt.xlim(-1, 1)
    plt.legend(loc='lower right')
    _savefig('재배방식별_상관계수_비교')
    plt.show()


def plot_scenario_chart(noji_dry: float, noji_wet: float,
                        siseol_dry: float, siseol_wet: float):
    scenario_data = {
        '시나리오': ['가뭄형 폭염', '장마형 폭염'],
        '노지 상추': [noji_dry,   noji_wet],
        '시설 상추': [siseol_dry, siseol_wet],
    }
    df_scn   = pd.DataFrame(scenario_data).melt(
        id_vars='시나리오', var_name='재배방식', value_name='평균생산량'
    )
    all_vals = [noji_dry, noji_wet, siseol_dry, siseol_wet]

    plt.figure(figsize=(9, 6))
    sns.barplot(x='시나리오', y='평균생산량', hue='재배방식', data=df_scn,
                palette=['#e74c3c', '#3498db'], alpha=0.7)
    sns.lineplot(x='시나리오', y='평균생산량', hue='재배방식', data=df_scn,
                 palette=['#e74c3c', '#3498db'], legend=False)
    plt.ylim(min(all_vals) * 0.9, max(all_vals) * 1.1)
    plt.title('기후 시나리오별 평균 생산량 변화 (노지 vs 시설)', fontsize=14)
    _savefig('기후_시나리오별_생산량')
    plt.show()


def plot_kde_density(df_stats_noji: pd.DataFrame, df_stats_siseol: pd.DataFrame):
    plt.figure(figsize=(12, 8))
    sns.kdeplot(data=df_stats_noji,   x='high_20_25', y='max_streak',
                fill=True, cmap='Reds',  alpha=0.4, label='노지 생산성 분포')
    sns.kdeplot(data=df_stats_siseol, x='high_20_25', y='max_streak',
                fill=True, cmap='Blues', alpha=0.4, label='시설 생산성 분포')

    for i in range(len(df_stats_siseol)):
        plt.text(df_stats_siseol['high_20_25'].iloc[i],
                 df_stats_siseol['max_streak'].iloc[i],
                 str(df_stats_siseol.index[i]), fontsize=9, ha='right')
    plt.scatter(df_stats_siseol['high_20_25'], df_stats_siseol['max_streak'],
                color='black', s=50, alpha=0.6)

    plt.axvline(df_stats_siseol['high_20_25'].mean(), color='red',  linestyle='--',
                alpha=0.5, label='고온 평균')
    plt.axhline(df_stats_siseol['max_streak'].mean(),  color='blue', linestyle='--',
                alpha=0.5, label='강수 평균')
    plt.text(df_stats_siseol['high_20_25'].max(), df_stats_siseol['max_streak'].max(),
             '장마형 폭염 구역', ha='right', va='top',
             fontsize=12, fontweight='bold', color='darkblue')

    plt.title('기상 조건별 재배 방식 생산성 밀도 비교', fontsize=15)
    plt.xlabel('고온 발생 빈도 (high_20_25)')
    plt.ylabel('최장 연속 강우일 (max_streak)')
    plt.legend(loc='upper left')
    _savefig('기상조건_생산성_밀도')
    plt.show()


# ── 진입점 ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    yield_series_map = {
        label: load_yield_series(col) for label, col in CROP_COLS.items()
    }

    for crop_label, yield_series in yield_series_map.items():
        run_basic_weather_correlation(yield_series, crop_label)
        run_monthly_hightemp_correlation(yield_series, crop_label)
        run_allmonth_extreme_correlation(yield_series, crop_label)

    detailed_results = {
        label: run_detailed_cultivation_analysis(yield_series, label)
        for label, yield_series in yield_series_map.items()
    }

    noji_result   = detailed_results['노지 상추']
    siseol_result = detailed_results['시설 상추']

    if noji_result and siseol_result:
        plot_correlation_comparison(noji_result['corr'], siseol_result['corr'])
        plot_scenario_chart(
            noji_result['dry_mean'],   noji_result['wet_mean'],
            siseol_result['dry_mean'], siseol_result['wet_mean'],
        )
        plot_kde_density(noji_result['df_stats'], siseol_result['df_stats'])
