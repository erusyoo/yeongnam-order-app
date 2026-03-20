import streamlit as st
import datetime
import time

# ==========================================
# 1. 모바일 최적화 세팅 (여백 제거)
# ==========================================
st.set_page_config(page_title="영남물류 발주 시스템", page_icon="🚚", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 14px; color: #6B7280; text-align: center; margin-bottom: 20px; }
    .stButton>button { height: 55px; font-size: 18px; font-weight: bold; border-radius: 8px; }
    .qty-text { font-size: 24px; font-weight: bold; text-align: center; line-height: 2.2; color: #111827; }
    div[data-baseweb="tab-list"] { justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚚 영남물류 스마트 발주망</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">시스템 접속일: {datetime.date.today().strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
st.info("📌 본 시스템은 영업사원 현장 발주 간소화를 위해 특별 제작되었습니다.")

# ==========================================
# 2. 상태 초기화 (Session State)
# ==========================================
CATALOG = [
    {"id": "item1", "name": "남양 에코쿡 칼라냄비 (곰국)", "desc": "1박스 = 12입", "tab": "🫕 냄비/주방"},
    {"id": "item2", "name": "홈베큐 (프리미엄)", "desc": "냉장 보관 필수", "tab": "🍖 식품/가공"},
    {"id": "item3", "name": "(물)라온 브루미즈 핸들보행기-74", "desc": "색상 혼합", "tab": "🧸 생활/유아"}
]

if 'orders' not in st.session_state:
    st.session_state.orders = {item['id']: 0 for item in CATALOG}

# 중복 클릭 방지용 상태 변수
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# ==========================================
# 3. 지점 선택 (상단 고정 표시)
# ==========================================
clients = ["선택 안됨", "은현농협하나로마트", "수원유통센터(식자재)", "양주유통센터(소매)", "가평군(자라점)농협"]
selected_client = st.selectbox("📍 발주 지점 선택", clients, disabled=st.session_state.submitted)

# 영업용 핵심: 선택된 지점을 강하게 시각화
if selected_client != "선택 안됨":
    st.success(f"📍 현재 발주 지점: **{selected_client}**")

# ==========================================
# 4. 모바일 실사용 UI (+/- 스크롤 튐 방지)
# ==========================================
st.markdown("### 📦 발주 상품 선택")

tab_names = list(set([item['tab'] for item in CATALOG]))
tabs = st.tabs(tab_names)

for item in CATALOG:
    tab_index = tab_names.index(item['tab'])
    with tabs[tab_index]:
        st.markdown(f"**{item['name']}**")
        st.caption(item['desc'])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # type="secondary" 및 use_container_width 적용
            if st.button("➖", key=f"minus_{item['id']}", use_container_width=True, type="secondary", disabled=st.session_state.submitted):
                if st.session_state.orders[item['id']] > 0:
                    st.session_state.orders[item['id']] -= 1
                    st.rerun() # 즉각적 UI 갱신
        with col2:
            st.markdown(f"<div class='qty-text'>{st.session_state.orders[item['id']]}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("➕", key=f"plus_{item['id']}", use_container_width=True, type="secondary", disabled=st.session_state.submitted):
                st.session_state.orders[item['id']] += 1
                st.rerun()
        
        st.markdown("---")

# ==========================================
# 5. 발주 요약 
# ==========================================
st.markdown("### 🧾 발주 요약")
summary = { item['name']: st.session_state.orders[item['id']] for item in CATALOG if st.session_state.orders[item['id']] > 0 }

if summary:
    for name, qty in summary.items():
        st.write(f"✔️ {name} : **{qty}개**")
else:
    st.caption("선택된 상품이 없습니다.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. 전송 및 초기화 플로우 (Magic Demo)
# ==========================================
# 이미 전송을 눌렀다면, '새로운 발주' 버튼 띄우기
if st.session_state.submitted:
    st.success("✅ 발주가 서버에 안전하게 기록되었습니다.")
    if st.button("🔄 새로운 발주 작성하기", use_container_width=True, type="primary"):
        st.session_state.submitted = False
        st.rerun()

# 아직 전송 전이라면 '발주서 전송' 버튼 띄우기
else:
    if st.button("🚀 발주서 전송 (서버 전송)", use_container_width=True):
        if selected_client == "선택 안됨":
            st.error("❗ 발주 지점을 먼저 선택해주세요.")
        elif not summary:
            st.warning("❗ 선택된 상품 수량이 없습니다.")
        else:
            with st.spinner("📡 영남물류 본사 클라우드 서버로 암호화 전송 중..."):
                time.sleep(1.5)

            st.success(f"✅ [{selected_client}] 발주가 성공적으로 접수되었습니다!")

            final_payload = [{"client": selected_client, "item": name, "qty": qty} for name, qty in summary.items()]
            
            with st.expander("📄 전송된 백엔드 데이터 확인 (관리자용)"):
                st.json(final_payload)

            # 핵심: 상태 잠금 및 수량 초기화
            st.session_state.submitted = True
            for item in CATALOG:
                st.session_state.orders[item['id']] = 0
            
            time.sleep(1) # 시연 호흡을 위한 1초 대기
            st.rerun() # UI 리프레시하여 새 발주 버튼 띄우기

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("© 2026 영남물류 | U&I Soltech AI 자동화 센터 구축")
