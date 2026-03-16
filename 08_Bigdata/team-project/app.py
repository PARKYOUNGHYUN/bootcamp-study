import streamlit as st
import joblib
import numpy as np

# 모델 로드
rf_tuned = joblib.load('./model/addiction_model.pkl')

st.title("📵 숏폼 중독 위험도 예측기")
st.subheader("나의 숏폼 사용 패턴을 입력하면 중독 위험도를 예측해드립니다")

st.divider()

# 입력 슬라이더
Q71A = st.selectbox(
    "숏폼이 전체 영상 소비에서 차지하는 비중",
    options=[1, 2, 3, 4],
    format_func=lambda x: {
        1: '0~25% 미만',
        2: '25~50% 미만',
        3: '50~75% 미만',
        4: '75% 이상'
    }[x]
)

Q73A = st.selectbox(
    "AI 알고리즘에 의해 숏폼을 반복 시청하게 된다",
    options=[1, 2, 3, 4],
    format_func=lambda x: {
        1: '전혀 그렇지 않다',
        2: '그렇지 않다',
        3: '그렇다',
        4: '매우 그렇다'
    }[x]
)

Q33 = st.selectbox(
    "SNS 이용시간 조절이 어렵다",
    options=[1, 2, 3, 4],
    format_func=lambda x: {
        1: '전혀 그렇지 않다',
        2: '그렇지 않다',
        3: '그렇다',
        4: '매우 그렇다'
    }[x]
)

st.divider()

# 예측 버튼
if st.button("🔍 위험도 예측하기"):
    input_data = np.array([[Q71A, Q73A, Q33]])
    proba = rf_tuned.predict_proba(input_data)[0][1]
    risk_score = round(proba * 100)

    st.subheader(f"중독 위험도: {risk_score}점")

    if risk_score >= 60:
        st.error("🔴 위험 — 숏폼 사용 패턴을 조절할 필요가 있습니다")
    elif risk_score >= 12:
        st.warning("🟡 주의 — 사용 습관을 점검해보세요")
    else:
        st.success("🟢 안전 — 건강한 숏폼 사용 패턴입니다")

    st.progress(risk_score / 100)

    st.caption("※ 위험 기준: 예측 확률 분포를 3등분하여 하위 33%를 안전(12점), 상위 33%를 위험(60점)으로 설정")
