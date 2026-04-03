import streamlit as st
from typing import Callable, Dict, List, Optional
import re

# =========================================================
# 복무관리 매뉴얼 앱 - 실무형 최종 구조 통합본
# - 첫번째 파일의 근무제도/자동판단 로직 보존
# - 두번째 파일의 실무형 UX 구조 적용
# - 페이지 함수 + PAGE_RENDERERS 방식으로 확장 가능
# =========================================================

st.set_page_config(
    page_title="복무관리 매뉴얼",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
:root {
    --line: #e5e7eb;
    --text: #111827;
    --muted: #6b7280;
    --blue-bg: #eff6ff;
    --blue-line: #2563eb;
    --amber-bg: #fffbeb;
    --amber-line: #f59e0b;
    --green-bg: #ecfdf5;
    --green-line: #10b981;
    --card-bg: #ffffff;
}
html, body, [class*="css"] { font-size: 16px; color: var(--text); }
.block-card { border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; background: var(--card-bg); margin-bottom: 12px; }
.summary-box { border-left: 5px solid var(--blue-line); background: var(--blue-bg); padding: 14px 16px; border-radius: 12px; margin: 8px 0 14px 0; }
.warn-box { border-left: 5px solid var(--amber-line); background: var(--amber-bg); padding: 14px 16px; border-radius: 12px; margin: 8px 0 14px 0; }
.result-box { border-left: 5px solid var(--green-line); background: var(--green-bg); padding: 14px 16px; border-radius: 12px; margin: 8px 0 14px 0; }
.kpi-card { border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px; background: #fff; min-height: 92px; }
.kpi-label { font-size: 0.9rem; color: var(--muted); margin-bottom: 6px; }
.kpi-value { font-size: 1.05rem; font-weight: 700; line-height: 1.4; }
.page-title { font-size: 1.7rem; font-weight: 800; margin-bottom: 4px; }
.page-caption { color: var(--muted); font-size: 0.95rem; margin-bottom: 10px; }
@media (max-width: 900px) { .page-title { font-size: 1.45rem; } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================================
# 공통 컴포넌트
# =========================================================
def render_page_header(title: str, breadcrumb: str, subtitle: Optional[str] = None):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-caption'>{breadcrumb}</div>", unsafe_allow_html=True)
    if subtitle:
        render_summary_box("한눈에 보기", subtitle)

def render_summary_box(title: str, text: str):
    st.markdown(f"<div class='summary-box'><b>{title}</b><br>{text}</div>", unsafe_allow_html=True)

def render_result_panel(result: str, basis: str, next_step: str, caution: str):
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown(f"**결과**  \n{result}")
    st.markdown(f"**적용 기준**  \n{basis}")
    st.markdown(f"**후속 처리**  \n{next_step}")
    st.markdown(f"**적용 시 유의사항**  \n{caution}")
    st.markdown("</div>", unsafe_allow_html=True)

def render_drims_box(path_text: str, note: str = ""):
    content = f"<b>DRIMS 처리 경로</b><br>{path_text}"
    if note:
        content += f"<br><span style='color:#6b7280'>{note}</span>"
    st.markdown(f"<div class='block-card'>{content}</div>", unsafe_allow_html=True)

def render_quick_kpis(items: List[Dict[str, str]]):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-label'>{item['label']}</div><div class='kpi-value'>{item['value']}</div></div>",
                unsafe_allow_html=True,
            )

def render_bullets(title: str, items: List[str], variant: str = "normal"):
    klass = "warn-box" if variant == "warn" else "block-card"
    st.markdown(f"### {title}")
    st.markdown(f"<div class='{klass}'>", unsafe_allow_html=True)
    for item in items:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 메뉴 구성
# =========================================================
MENU_CONFIG: Dict[str, List[str]] = {
    "홈": [],
    "근무제도": ["근무일과 휴일", "근무시간과 휴게시간", "휴일대체근무제도", "근무형태 변경시 처리", "지정휴무"],
    "휴가제도": ["휴가 기본원칙", "연차휴가", "공가", "병가", "청원휴가", "초과근무 보상휴가", "특별휴가(자녀돌봄)", "가족돌봄휴가", "반일휴가 / 휴가정정"],
    "출장제도": ["기본 안내"],
    "기타근태제도": [],
    "휴직제도": [],
}
DISPLAY_TO_INTERNAL = {
    "휴가 기본원칙": "일반사항",
    "초과근무 보상휴가": "보상휴가",
    "반일휴가 / 휴가정정": "반일휴가제",
}

# =========================================================
# 데이터 - 근무제도
# =========================================================
workday_holiday_data = {
    "title": "근무일과 휴일",
    "one_line_summary": "근무일은 휴일·휴무일을 제외한 날이고, 휴일은 근무형태에 따라 다르게 적용됩니다.",
    "definitions": {"근무일": "취업규칙상 정해진 근무시간 중 휴일 및 휴무일을 제외한 날", "휴일(휴무일)": "취업규칙에 따라 근로의무가 없는 날"},
    "work_types": [
        {"name": "통상근무", "summary": "가장 일반적인 형태", "holidays": ["토요일(무급휴일)", "일요일"], "practical": "사무직처럼 달력 기준으로 이해하면 가장 쉽습니다."},
        {"name": "현업일근", "summary": "요일 고정형이 아니라 지정형 휴무", "holidays": ["지정휴무: 주 2일", "연중지휴: 월 1일"], "practical": "달력보다 소속 부서의 지정 기준과 운영계획을 먼저 확인해야 합니다."},
        {"name": "교대근무", "summary": "요일보다 근무주기와 근무표가 중요", "holidays": ["6주기: 근무형태에서 발생되는 6주기당 2일", "지정휴무: 월 2일(주A 1일, 주B 1일)", "분기지휴: 8일(분기당 2일)", "21주기: 지정휴무 21주기당 2일(야간 2일 지정 불가)", "야간근무 후 휴일", "분기지휴: 4일(분기당 1일)"], "practical": "일요일이라고 무조건 쉬는 개념이 아니라 근무표상 휴일인지 먼저 봐야 합니다."},
        {"name": "교번근무", "summary": "기관사 등 근무표 기반 운영", "holidays": ["근무표에 의한 휴일", "대기휴무 등 발생된 휴일", "분기지휴: 4일(분기당 1일)"], "practical": "근무표가 사실상 기준표 역할을 합니다."},
    ],
    "public_holiday_rule": "법령 및 정부에서 정한 공휴일과 공사창립일은 유급휴일로 부여하되, 교대·교번근무자는 근무형태에서 발생된 휴일로, 현업일근자는 지정된 휴무일로 대체합니다. 단, 근로자의 날(5.1)은 휴일근무수당 지급 대상입니다.",
    "substitute_holiday": "명절휴일이 공휴일과 겹치거나 3·1절, 광복절, 개천절, 한글날, 어린이날이 토요일 또는 다른 공휴일과 겹치면 다음 첫 번째 비공휴일을 공휴일로 합니다.",
    "mistakes": ["공휴일이면 모든 직원이 같은 방식으로 쉬는 것은 아닙니다.", "교대·교번근무는 달력보다 근무표가 우선입니다.", "근로자의 날은 일반 공휴일과 동일하게 보면 실무상 오류가 생길 수 있습니다."],
}
worktime_break_data = {
    "title": "근무시간과 휴게시간",
    "one_line_summary": "기본은 1일 8시간, 1주 40시간이며, 근무형태별로 근무시간과 휴게시간이 다르고 변경·탄력근로 운용에도 제한이 있습니다.",
    "basic_rules": ["근무시간은 1일 8시간, 1주 40시간입니다.", "1주는 휴일을 포함한 7일(월~일) 기준입니다.", "휴게시간은 업무에 지장을 초래하지 않는 범위 내에서 자유롭게 사용할 수 있습니다.", "분야별 근무형태, 근무시간 및 휴게시간은 취업규칙 별표 1에 따르며, 계절 변화나 업무 특수사정이 있으면 조정할 수 있습니다."],
    "work_types": [
        {"name": "통상근무", "time": "월~금 09:00~18:00", "break": "1시간 (12:00~13:00)", "actual": "8시간", "cycle": "일반 주간근무"},
        {"name": "현업일근", "time": "09:00~18:00", "break": "1시간 (12:00~13:00)", "actual": "8시간", "cycle": "주 단위"},
        {"name": "3호선 역순회요원 (3조2교대)", "time": "주간A 05:20~14:50 / 주간B 14:00~24:30", "break": "각 1시간", "actual": "주간A 8.5시간 / 주간B 9.5시간", "cycle": "6일 주기"},
        {"name": "역무·관제·통신·변전·차량운영·전자(AFC)", "time": "주간 09:00~18:00 / 야간 18:00~익일 09:00", "break": "주간 1시간 / 야간 4시간 30분", "actual": "주간 8시간 / 야간 10.5시간", "cycle": "21일 주기"},
        {"name": "교번근무 (1,2호선 차량운영 기관사)", "time": "기관사 근무표에 의함", "break": "교번운용표에 의함", "actual": "교번운용표에 의함", "cycle": "교번운용표 기준"},
    ],
    "change_rules": ["단위기간 내 지정된 근무일과 근로시간은 원칙적으로 변경이 제한됩니다.", "현업 운영상 부득이하여 변경하지 않으면 본래 업무를 달성할 수 없는 경우에만 예외적으로 변경할 수 있습니다.", "기본적인 근무형태가 1주일 이상 변경되면 노무복지팀장 협조결재 후 변경 가능합니다.", "탄력근로 범위 내에서도 1일 최대근로시간은 12시간을 넘지 않아야 합니다."],
}
work_overtime_data = {
    "title": "휴일대체근무제도",
    "one_line_summary": "연장근무·야간근무·휴일근무는 시간대와 근무시간에 따라 보상휴가Ⅱ 또는 대체휴일로 처리되며, 사전 고지와 시간 기준 확인이 핵심입니다.",
    "overview": ["연장근무는 정해진 근로시간을 초과하는 시간이며 해당 시간의 1.5배를 보상합니다.", "야간근무는 22:00부터 06:00까지의 근로시간이며 해당 시간의 0.5배를 보상합니다.", "연장근로이면서 야간근로에 해당하면 연장·야간 모두 보상합니다."],
    "overtime_by_type": [["통상근무자", "8시간을 초과하는 시간"], ["교대 21일·8일주기", "주간 8시간 초과 / 야간 10.5시간 초과"], ["교대 6일주기", "주간A 8.5시간 초과 / 주간B 9.5시간 초과"]],
    "overtime_rules": ["연장근무는 1주 12시간을 초과할 수 없습니다.", "휴게시간은 4시간에 30분 이상, 8시간에 1시간 이상을 준수해야 합니다.", "조정이 불가하면 보상휴가Ⅱ를 부여합니다."],
}
work_change_data = {
    "title": "근무형태 변경시 처리",
    "one_line_summary": "근무형태 변경 시 변경된 근무를 즉시 적용하며, 변경 전 야간근무에 대한 휴무 보장과 주휴일 확보가 핵심입니다.",
    "basic_rules": ["근무형태 변경 시에는 변경된 근무를 그대로 적용합니다.", "변경 전 야간근무로 인해 발생한 휴무일은 반드시 보장합니다.", "근로기준법 및 취업규칙에 따라 1주(월~일)에 주휴일 1일을 반드시 보장해야 합니다."],
}
work_designated_off_data = {
    "title": "지정휴무",
    "one_line_summary": "근무형태 변경 시 지정휴무는 ‘잔여 근무일수 + 변경 유형’으로 결정됩니다.",
    "concept": ["주 1회 주휴일 보장은 무조건 적용합니다.", "21주기 근무자는 지정휴무 2일 중 1일은 주휴 개념으로 사용합니다."],
    "grant_rules": ["현업일근: 주 2일 지정휴무", "6주기: 월 2일 (주A 1일, 주B 1일)", "21주기: 총 2일", "교번근무: 분기/연간 기준 관리"],
    "usage_rules": ["지정휴무는 해당 월 또는 주기 내 반드시 사용합니다.", "미사용 시 소멸하며 이월되지 않습니다.", "사용계획은 사전 승인 필요합니다."],
    "case_21": [["통상 → 21주기", "조건 무관", "2일 발생"], ["주간 → 야간", "4일 이상", "1일 발생"], ["주간 → 야간", "3일 이하", "미발생"], ["야간 → 주간", "3일 이상", "2일 발생"], ["야간 → 주간", "2일 이하", "1일 발생"]],
    "case_field": [["현업일근 → 21주기", "5일 이상", "2일 발생"], ["현업일근 → 21주기", "4일 이하", "1일 발생"], ["21주기 → 현업일근", "5일 이상", "2일 발생"], ["21주기 → 현업일근", "4일 이하", "1일 발생"]],
    "case_6": [["통상/21주기 → 6주기", "1~6일", "월 2회"], ["통상/21주기 → 6주기", "7~20일", "월 1회"], ["통상/21주기 → 6주기", "21일 이상", "미발생"]],
    "note": ["지정휴무는 잔여 근무일수가 핵심 판단 기준입니다.", "근무표와 인사이동 기준을 같이 봐야 정확합니다."],
}

# =========================================================
# 데이터 - 휴가제도
# =========================================================
leave_general_data = {
    "title": "휴가 기본원칙",
    "one_line_summary": "휴가는 출근 의무가 있는 날에 사용하는 제도이며, 승인·증빙·연락체계 유지가 실무 핵심입니다.",
    "legal_meaning": ["휴가는 출근을 전제로 하며, 출근의무가 없는 휴직·정직 중인 직원은 휴가를 사용할 수 없습니다.", "휴가는 근로자가 청구하거나 특별한 사유가 충족되어 근로제공 의무가 면제된 날입니다.", "휴가신청에 대한 허가는 업무형편과 부서 사정을 고려해 시기를 변경할 수 있으나 특별한 사정이 없는 한 허가합니다."],
    "principles": ["휴가를 사용하려면 소속장 승인을 받아야 하며 필요한 경우 증빙서류를 제출해야 합니다.", "증빙서류를 바로 제출하지 못한 경우에는 휴가 종료 후 3일 이내 제출해야 합니다."],
    "cautions": ["휴가기간 중 비상시 연락 가능하도록 연락체계를 유지해야 합니다.", "정해진 기간을 초과해 사용하면 결근처리 및 감사대상이 될 수 있습니다.", "같은 날 두 종류 이상의 휴가사유가 겹치면 하나의 휴가만 허가됩니다."],
    "leave_types": [["연차휴가", "계속 근로한 직원의 근로의욕 고취", "연간 15일~25일", "회계연도 단위로 발생"], ["공가", "병역검사, 예비군 훈련 등 공적 사유 처리", "필요한 시간만큼 부여", ""], ["병가", "부상 또는 질병의 치료", "공상병가 180일 / 사상병가 60일", ""], ["청원휴가", "본인 또는 가족의 경조사 참석", "사유별 상이", "본인에는 배우자 포함"], ["보상휴가", "통상근무자의 연장근로에 대한 보상", "연간 6일 이내", ""], ["특별휴가(자녀돌봄)", "미성년자녀 학교행사·상담·진료 동행", "연 2일(자녀 셋 이상 3일)", "최소 4시간부터"], ["가족돌봄휴가", "가족의 질병·사고·노령·자녀양육 돌봄", "연 10일(무급)", ""]],
}
annual_leave_data = {
    "title": "연차휴가",
    "summary": "연차휴가는 전년도 출근율과 계속 근로연수에 따라 발생하며, 일부 대상자는 촉진일수를 별도로 계산하여 사용촉진 절차를 적용합니다.",
    "overview": ["1년 미만 연차는 입사일 기준 1개월 개근 시 1일씩 발생하며 총 11일까지 가능합니다.", "전년도 출근율에 따른 연차는 회계연도 기준으로 산정합니다.", "출근율 80% 이상이면 기본 15일에 최초 1년 초과 계속 근로연수 매 2년마다 1일 가산하며 총 25일 이내입니다.", "출근율 80% 미만이면 1개월 개근 시 1일이 발생합니다.", "통상근무자와 21주기 교대근무자의 주간근무는 반일휴가 사용이 가능합니다."],
    "promotion": ["대상자는 전 직원입니다.", "촉진일수는 연간 5일이며, 발생일수가 5일 미만이면 그 발생일수만큼 촉진합니다.", "휴직 사용자, 장기 교육 파견자, 출산전후휴가 사용자는 근무일 일할 계산 후 소수점 이하는 절사합니다."],
    "promotion_steps_general": ["휴가사용 기간 종료 6개월 전 기준으로 10일 이내 사용하지 않은 휴가일수를 알리고 사용시기 통보를 촉구합니다.", "근로자가 10일 이내 사용시기를 통보하지 않으면 기간 종료 2개월 전까지 사용시기를 정해 통보합니다.", "기간 내 사용하지 않은 휴가는 소멸하며 수당청구권이 발생하지 않습니다."],
    "promotion_steps_new_employee": ["1년 미만 연차는 사용기간 종료 3개월 전 기준으로 10일 이내 사용하지 않은 휴가일수를 알리고 사용시기 통보를 촉구합니다.", "촉구 이후 발생한 휴가에 대해서도 별도 촉구 절차를 진행합니다.", "기간 내 사용하지 않은 휴가는 소멸하며 수당청구권이 발생하지 않습니다."],
    "new_employee_table": [["1월 입사", 11, 0, 11, 5, "15 ~ 13.7", 5], ["2월 입사", 10, 1, 11, 5, "13.7 ~ 12.6", 4], ["3월 입사", 9, 2, 11, 5, "12.6 ~ 11.3", 4], ["4월 입사", 8, 3, 11, 5, "11.3 ~ 9.7", 3], ["5월 입사", 7, 4, 11, 5, "9.7 ~ 8.4", 3], ["6월 입사", 6, 5, 11, 5, "8.4 ~ 7.2", 3], ["7월 입사", 5, 6, 11, 5, "7.2 ~ 5.9", 2], ["8월 입사", 4, 7, 11, 5, "5.9 ~ 4.6", 2], ["9월 입사", 3, 8, 11, 5, "4.6 ~ 3.4", 1], ["10월 입사", 2, 9, 11, 5, "3.4 ~ 2.1", 1], ["11월 입사", 1, 10, 11, 5, "2.1 ~ 0.9", 0], ["12월 입사", 0, 11, 11, 5, "0.9 ~ 0", 0]],
}
official_leave_data = {
    "title": "공가",
    "summary": "공가는 개인적인 휴가가 아니라, 공적 사유나 법령상 필요한 사무를 처리하기 위해 부여하는 휴가입니다.",
    "concept": ["사무실에 출근하지 못하지만 사적인 일로 보기 어려운 공적 성격의 업무를 처리할 때 사용하는 휴가입니다."],
    "grant_rules": ["병역검사, 소집 또는 검열, 점호 등에 응하거나 동원훈련에 참가할 때", "법률의 규정에 따라 투표에 참가할 때", "천재지변 등 부득이한 사유로 출근이 불가능한 때", "공무로 국가기관에 소환된 때", "일반건강검진을 받을 때(연 1회)"],
    "usage_rules": ["소속장은 해당 사유에 필요한 기간(시간)만큼 공가를 허가할 수 있습니다.", "공가 사용 후 7일 이내에 증빙서류를 제출해야 합니다.", "공가 기간이 소정근로시간 내에 종료되면 즉시 복귀해야 합니다."],
    "etc_rules": ["공가 시간은 근무한 것으로 간주되어 인사상·경제상 불이익이 없도록 처리합니다."],
}
sick_leave_data = {
    "title": "병가",
    "summary": "병가는 부상 또는 질병 치료를 위해 사용하는 휴가이며, 공상병가와 사상병가를 구분하여 관리합니다.",
    "concept": ["병가는 직원이 부상 또는 질병으로 일정기간 치료가 필요할 때 사용하는 휴가입니다."],
    "grant_rules": ["공상병가: 산업재해 요양승인에 따른 병가로 연 누계 180일 범위입니다.", "사상병가: 공상병가 이외의 병가로 연 누계 60일 범위입니다."],
    "usage_rules": ["병가를 사용할 때에는 원칙적으로 의사의 진단서를 제출해야 합니다.", "3일 이내 병가는 진료확인서 또는 진료비영수증 등 병원 방문 확인 자료로 갈음할 수 있습니다.", "3일을 초과하면 진단서 기준을 함께 확인해야 합니다."],
    "etc_rules": ["공상병가와 사상병가는 각각 구분해 관리합니다.", "병가기간을 초과하면 개인 휴가 또는 휴직 검토가 필요할 수 있습니다."],
}
petition_leave_data = {
    "title": "청원휴가",
    "summary": "청원휴가는 본인 또는 가족의 경조사 참석 등을 위해 사용하는 휴가입니다.",
    "grant_rules": ["결혼-본인: 5일", "결혼-자녀: 1일", "출산-배우자: 20일", "입양-본인: 20일", "사망-배우자, 본인 및 배우자의 부모: 5일", "사망-본인 및 배우자의 조부모·외조부모: 3일", "사망-자녀와 그 자녀의 배우자: 3일", "사망-본인 및 배우자의 형제자매와 그 배우자: 1일", "사망-본인 및 배우자 부모의 형제자매와 그 배우자: 1일", "탈상-배우자, 본인 및 배우자의 부모: 1일"],
}
comp_leave_data = {
    "title": "초과근무 보상휴가",
    "summary": "보상휴가는 통상근무자가 연장·야간·휴일근로를 한 경우 임금 대신 휴가를 적치하여 사용하는 제도입니다.",
    "grant_rules": ["대상자: 통상근무자", "사용일수: 연간 6일", "연도 중 입사·퇴사·근무형태 변경·휴복직 시 일할계산하며 1일 단위 반올림합니다."],
    "usage_rules": ["적치기간: 전년도 12.1. ~ 당해연도 11.30.", "사용기간: 당해연도 상반기 3일, 하반기 3일", "기간 내 미사용 시 소멸하며 금전보상은 불가합니다."],
}
special_childcare_leave_data = {
    "title": "특별휴가(자녀돌봄)",
    "summary": "미성년 자녀의 공식 학교행사, 교사 상담, 병원 진료 동행 등을 위해 사용하는 휴가입니다.",
    "usage_rules": ["자녀 수 1~2명은 연간 2일(16시간)입니다.", "자녀 수 3명 이상이거나 특수 자녀 조건이 있으면 연간 3일(24시간)입니다.", "최소 4시간부터 1시간 단위로 사용할 수 있습니다."],
}
family_care_leave_data = {
    "title": "가족돌봄휴가",
    "summary": "가족의 질병, 사고, 노령 또는 자녀 양육으로 긴급 돌봄이 필요할 때 사용하는 무급휴가입니다.",
    "operation_rules": ["휴가일수는 연간 10일 이내이며 일 단위로 사용합니다.", "가족돌봄휴가는 무급휴가이며 자녀돌봄휴가와는 구분해 사용합니다.", "신청 시 가족관계 및 신청사유를 증빙할 수 있는 서류를 첨부해야 합니다."],
}
half_day_leave_data = {
    "title": "반일휴가 / 휴가정정",
    "summary": "반일휴가는 일부 휴가를 오전 또는 오후로 사용하는 제도이며, 휴가정정은 출력물 저장 → 삭제 → 재등록 순으로 처리합니다.",
    "usage_rules": ["반일 단위 사용이 가능한 휴가는 통상근무자의 연차휴가·보상휴가, 21주기 주간근무 시 연차휴가입니다.", "반일휴가 1회는 0.5일, 2회는 1일로 봅니다.", "근무시간의 중간대에는 사용할 수 없습니다."],
    "correction_rules": ["정정 전 휴가 출력물 저장", "휴가 삭제", "휴가 재등록"],
}

# =========================================================
# 계산 함수
# =========================================================
def calculate_promotion_days_for_special_case(work_days: int) -> int:
    if work_days < 0: return 0
    return int((5 * work_days) // 365)

def get_promotion_guide(promotion_days: int, employee_type: str) -> List[str]:
    if employee_type == "신입사원(1년 미만/2년차)":
        return annual_leave_data["promotion_steps_new_employee"]
    if promotion_days <= 0:
        return ["계산 결과 촉진일수가 0일이므로 별도 촉진일 적용 대상이 아닙니다. 최종 적용 전 인사자료와 실근무일을 다시 확인해 주세요."]
    return annual_leave_data["promotion_steps_general"]

def calculate_sick_leave_days(leave_type: str, input_days: int, already_used_days: int) -> dict:
    limit_days = 180 if leave_type == "공상병가" else 60
    remaining_days = max(limit_days - already_used_days - input_days, 0)
    total_used = already_used_days + input_days
    msg = f"{leave_type} 한도를 초과합니다. 추가 기간은 개인 휴가 또는 휴직 검토가 필요할 수 있습니다." if total_used > limit_days else f"현재 입력 기준 산입 병가일수는 {input_days}일이며 잔여 가능일수는 {remaining_days}일입니다."
    return {"limit_days": limit_days, "remaining_days": remaining_days, "message": msg}
PETITION_LEAVE_MAP = {("결혼", "본인"): 5, ("결혼", "자녀"): 1, ("출산", "배우자"): 20, ("입양", "본인"): 20, ("사망", "배우자"): 5, ("사망", "본인/배우자의 부모"): 5, ("사망", "본인/배우자의 조부모·외조부모"): 3, ("사망", "자녀/자녀의 배우자"): 3, ("사망", "본인/배우자의 형제자매 및 그 배우자"): 1, ("사망", "본인/배우자 부모의 형제자매 및 그 배우자"): 1, ("탈상", "배우자/본인/배우자의 부모"): 1}
def calculate_petition_leave(event_type: str, relation: str, is_holiday: bool):
    days = PETITION_LEAVE_MAP.get((event_type, relation), 0)
    start_note = "사유 발생일부터 기산합니다." if not is_holiday else "사유 발생일이 휴일이면 다음 근무일부터 기산합니다."
    return {"days": days, "note": start_note}
def calculate_comp_leave_hours(overtime_hours: float) -> dict:
    accumulated_hours = overtime_hours * 1.5
    accumulated_days = accumulated_hours / 8.0
    return {"accumulated_hours": round(accumulated_hours, 2), "accumulated_days": round(accumulated_days, 2)}
def calculate_childcare_leave_entitlement(child_count: int, special_child: bool) -> dict:
    return {"days": 3, "hours": 24} if child_count >= 3 or special_child else {"days": 2, "hours": 16}
def get_family_care_leave_entitlement(used_days: int) -> dict:
    max_days = 10
    return {"max_days": max_days, "used_days": used_days, "remaining_days": max(max_days - used_days, 0)}
HALF_DAY_TABLE = {
    ("통상근무", "기본", "오전"): {"leave_time": "09:00 ~ 13:30", "work_time": "13:30 ~ 18:00"},
    ("통상근무", "기본", "오후"): {"leave_time": "13:30 ~ 18:00", "work_time": "09:00 ~ 13:30"},
    ("자녀양육지원제", "9to5", "오전"): {"leave_time": "09:00 ~ 13:00", "work_time": "13:00 ~ 17:00"},
    ("자녀양육지원제", "9to5", "오후"): {"leave_time": "13:00 ~ 17:00", "work_time": "09:00 ~ 13:00"},
    ("자녀양육지원제", "10to6", "오전"): {"leave_time": "10:00 ~ 14:00", "work_time": "14:00 ~ 18:00"},
    ("자녀양육지원제", "10to6", "오후"): {"leave_time": "14:00 ~ 18:00", "work_time": "10:00 ~ 14:00"},
}
def get_half_day_leave_time(worker_type: str, schedule_type: str, leave_part: str) -> dict:
    return HALF_DAY_TABLE.get((worker_type, schedule_type, leave_part), {"leave_time": "-", "work_time": "-"})
def parse_designated_off_text(user_text: str):
    text = user_text.replace(" ", "")
    case_type = None
    prev_shift = ""
    next_shift = ""
    remaining_days = None
    if "현업일근" in text:
        case_type = "현업일근 기준"
        if "21주기" in text:
            prev_shift = "현업일근→21주기" if text.index("현업일근") < text.index("21주기") else "21주기→현업일근"
    elif "6주기" in text:
        case_type = "6주기 기준"; prev_shift = "통상/21주기→6주기"
    elif "21주기" in text:
        case_type = "21주기 기준"
        if "통상" in text and "21주기" in text:
            prev_shift = "통상→21주기"
        elif "주간" in text and "야간" in text:
            if text.index("주간") < text.index("야간"): prev_shift, next_shift = "주간", "야간"
            else: prev_shift, next_shift = "야간", "주간"
    match = re.search(r"([0-9]+)일", text)
    if match: remaining_days = int(match.group(1))
    return {"case_type": case_type, "prev_shift": prev_shift, "next_shift": next_shift, "remaining_days": remaining_days}
def calculate_designated_off(case_type: str, remaining_days: Optional[int], prev_shift: str = "", next_shift: str = ""):
    result = {"result": "계산할 수 없습니다.", "reason": "입력값이 부족하거나 현재 규칙에 없는 조합입니다.", "rule": "지정휴무 표 기준을 다시 확인하세요."}
    if case_type == "21주기 기준":
        if prev_shift == "통상→21주기": return {"result": "2일 발생", "reason": "통상에서 21주기로 변경되는 경우는 잔여근무일수와 관계없이 2일 발생 기준입니다.", "rule": "통상 → 21주기 = 2일"}
        if prev_shift == "주간" and next_shift == "야간" and remaining_days is not None:
            return {"result": "1일 발생", "reason": f"주간에서 야간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 4일 이상 기준입니다.", "rule": "주간 → 야간, 4일 이상 1일 발생"} if remaining_days >= 4 else {"result": "미발생", "reason": f"주간에서 야간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 3일 이하 기준입니다.", "rule": "주간 → 야간, 3일 이하 미발생"}
        if prev_shift == "야간" and next_shift == "주간" and remaining_days is not None:
            return {"result": "2일 발생", "reason": f"야간에서 주간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 3일 이상 기준입니다.", "rule": "야간 → 주간, 3일 이상 2일 발생"} if remaining_days >= 3 else {"result": "1일 발생", "reason": f"야간에서 주간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 2일 이하 기준입니다.", "rule": "야간 → 주간, 2일 이하 1일 발생"}
    if case_type == "현업일근 기준" and remaining_days is not None:
        return {"result": "2일 발생", "reason": f"잔여근무일수 {remaining_days}일이므로 5일 이상 기준입니다.", "rule": "현업일근↔21주기, 5일 이상 2일 발생"} if remaining_days >= 5 else {"result": "1일 발생", "reason": f"잔여근무일수 {remaining_days}일이므로 4일 이하 기준입니다.", "rule": "현업일근↔21주기, 4일 이하 1일 발생"}
    if case_type == "6주기 기준" and remaining_days is not None:
        if 1 <= remaining_days <= 6: return {"result": "월 2회", "reason": f"잔여일수 {remaining_days}일이므로 1~6일 구간입니다.", "rule": "1~6일 월 2회"}
        if 7 <= remaining_days <= 20: return {"result": "월 1회", "reason": f"잔여일수 {remaining_days}일이므로 7~20일 구간입니다.", "rule": "7~20일 월 1회"}
        return {"result": "미발생", "reason": f"잔여일수 {remaining_days}일이므로 21일 이상 구간입니다.", "rule": "21일 이상 미발생"}
    return result

# =========================================================
# 검색 인덱스/검색
# =========================================================
def build_search_index() -> List[Dict[str, str]]:
    index: List[Dict[str, str]] = []
    def add(main: str, sub: str, keywords: List[str], desc: str):
        index.append({"main": main, "sub": sub, "display_sub": next((k for k, v in DISPLAY_TO_INTERNAL.items() if v == sub), sub), "keywords": " ".join(keywords).lower(), "desc": desc})
    add("근무제도", "근무일과 휴일", ["휴일", "공휴일", "대체공휴일", "근무일", "일요일"], "근무형태별 휴일 기준과 공휴일 처리 확인")
    add("근무제도", "근무시간과 휴게시간", ["근무시간", "휴게시간", "탄력근로", "52시간", "야간근무"], "근무시간·휴게시간 기준 확인")
    add("근무제도", "휴일대체근무제도", ["연장근무", "야간근무", "휴일근무", "보상휴가Ⅱ", "대체휴일"], "초과근무 및 휴일대체 기준 확인")
    add("근무제도", "근무형태 변경시 처리", ["근무형태 변경", "21주기", "6주기", "통상근무", "교번"], "근무형태 변경 기준 확인")
    add("근무제도", "지정휴무", ["지정휴무", "잔여 근무일수", "현업일근", "21주기", "6주기"], "지정휴무 발생 기준 자동 판단")
    add("휴가제도", "일반사항", ["휴가 기본원칙", "휴가 승인", "증빙", "국외여행", "중복휴가"], "휴가의 공통 원칙과 유의사항 확인")
    add("휴가제도", "연차휴가", ["연차", "연차촉진", "신입사원 연차", "배우자 출산휴가 며칠"], "연차 발생과 사용촉진 확인")
    add("휴가제도", "공가", ["공가", "건강검진", "예비군", "투표"], "공가 기준과 처리 안내")
    add("휴가제도", "병가", ["병가", "병가 3일 넘으면 뭐 필요해", "진단서", "공상병가", "사상병가"], "병가 기준과 필요서류 확인")
    add("휴가제도", "청원휴가", ["청원휴가", "배우자 출산휴가 며칠", "경조사", "부고", "탈상"], "경조사 휴가 일수 확인")
    add("휴가제도", "보상휴가", ["보상휴가", "초과근무", "연장근무 2시간", "적치"], "보상휴가 적치 계산 확인")
    add("휴가제도", "특별휴가(자녀돌봄)", ["자녀돌봄", "학교 행사", "교사 상담", "병원 진료 동행"], "자녀돌봄 특별휴가 기준 확인")
    add("휴가제도", "가족돌봄휴가", ["가족돌봄", "무급", "10일", "노령", "긴급 돌봄"], "가족돌봄휴가 기준 확인")
    add("휴가제도", "반일휴가제", ["반일휴가", "휴가정정", "오전 반차", "오후 반차", "drims 정정"], "반일휴가와 휴가정정 절차 확인")
    add("출장제도", "기본 안내", ["출장", "여비", "국외여행심사", "출장명령"], "출장제도는 다음 단계에서 상세 확장")
    return index
SEARCH_INDEX = build_search_index()
def render_global_search() -> None:
    query = st.text_input("빠른 검색", placeholder="예: 병가 3일 넘으면 뭐 필요해? / 배우자 출산휴가 며칠? / 휴가정정").strip().lower()
    if not query: return
    scored = []
    for item in SEARCH_INDEX:
        score = 0
        for token in query.split():
            if token in item["keywords"]: score += 1
        if score > 0: scored.append({**item, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    st.markdown("### 검색 결과")
    if not scored:
        st.markdown("<div class='warn-box'><b>검색 결과 없음</b><br>휴가명, 키워드, 처리명 중심으로 다시 검색해 주세요.</div>", unsafe_allow_html=True)
        return
    for item in scored[:5]:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown(f"**{item['main']} > {item['display_sub']}**")
        st.write(item["desc"])
        if st.button(f"바로 열기 · {item['display_sub']}", key=f"search_{item['main']}_{item['sub']}"):
            st.session_state["main_menu"] = item["main"]
            st.session_state["sub_menu"] = item["sub"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 홈/페이지 함수/사이드바/라우팅
# =========================================================
def render_home_dashboard():
    render_page_header("복무관리 매뉴얼", "홈", "첫번째 파일의 근무제도와 두번째 파일의 실무형 구조를 통합한 최종 버전입니다.")
    render_quick_kpis([{"label": "가장 많이 찾는 메뉴", "value": "연차 / 병가 / 청원휴가"}, {"label": "실무 처리 순서", "value": "판단 → 처리경로 → 유의사항"}, {"label": "기본 원칙", "value": "신청·승인 후 사용"}])
    st.markdown("### 자주 찾는 항목")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("근무일과 휴일", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "근무제도", "근무일과 휴일"; st.rerun()
        if st.button("지정휴무", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "근무제도", "지정휴무"; st.rerun()
    with c2:
        if st.button("연차휴가", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "휴가제도", "연차휴가"; st.rerun()
        if st.button("병가", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "휴가제도", "병가"; st.rerun()
    with c3:
        if st.button("청원휴가", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "휴가제도", "청원휴가"; st.rerun()
        if st.button("반일휴가 / 정정", use_container_width=True): st.session_state["main_menu"], st.session_state["sub_menu"] = "휴가제도", "반일휴가제"; st.rerun()
    render_drims_box("휴가정정: 셀프서비스 > 근태관리 > 휴가출장관리 > 휴가신청", "근태일이 지난 휴가 수정 시 출력물 저장 → 삭제 → 재등록 순서를 권장합니다.")

def render_workday_holiday_page():
    render_page_header("근무일과 휴일", "근무제도 > 근무일과 휴일", workday_holiday_data["one_line_summary"])
    render_quick_kpis([{"label": "먼저 확인", "value": "근무형태"}, {"label": "공휴일 처리", "value": "통상/현업/교대/교번 상이"}, {"label": "실무 주의", "value": "교대·교번은 근무표 우선"}])
    c1, c2 = st.columns(2)
    with c1: render_bullets("근무일", [workday_holiday_data["definitions"]["근무일"]])
    with c2: render_bullets("휴일(휴무일)", [workday_holiday_data["definitions"]["휴일(휴무일)"]])
    selected_type = st.selectbox("근무형태 선택", [item["name"] for item in workday_holiday_data["work_types"]])
    selected_data = next(item for item in workday_holiday_data["work_types"] if item["name"] == selected_type)
    render_bullets(f"{selected_data['name']} 휴일 기준", selected_data["holidays"])
    render_summary_box("실무 해석", selected_data["practical"])
    render_bullets("공휴일 처리", [workday_holiday_data["public_holiday_rule"]])
    render_bullets("대체공휴일", [workday_holiday_data["substitute_holiday"]])
    render_bullets("적용 시 유의사항", workday_holiday_data["mistakes"], variant="warn")

def render_worktime_break_page():
    render_page_header("근무시간과 휴게시간", "근무제도 > 근무시간과 휴게시간", worktime_break_data["one_line_summary"])
    render_quick_kpis([{"label": "기본 기준", "value": "1일 8시간 / 주 40시간"}, {"label": "먼저 확인", "value": "근무형태"}, {"label": "주의", "value": "변경·탄력근로 제한"}])
    render_bullets("기본원칙", worktime_break_data["basic_rules"])
    selected = st.selectbox("분야/근무형태 선택", [item["name"] for item in worktime_break_data["work_types"]], key="wt")
    data = next(item for item in worktime_break_data["work_types"] if item["name"] == selected)
    render_result_panel(f"근무시간 {data['time']} / 휴게시간 {data['break']}", f"실근무시간 {data['actual']} / 근무주기 {data['cycle']}", "실제 적용 시 소속 분야와 근무표를 함께 확인합니다.", "교대·교번·야간격일제는 달력보다 근무표 기준이 우선합니다.")
    render_bullets("근무 변경 기준", worktime_break_data["change_rules"], variant="warn")

def render_work_overtime_page():
    render_page_header("휴일대체근무제도", "근무제도 > 휴일대체근무제도", work_overtime_data["one_line_summary"])
    render_quick_kpis([{"label": "연장근무", "value": "1.5배 보상"}, {"label": "야간근무", "value": "0.5배 보상"}, {"label": "핵심", "value": "사전 고지 + 시간 기준"}])
    render_bullets("개요", work_overtime_data["overview"])
    st.table({"근무형태": [r[0] for r in work_overtime_data["overtime_by_type"]], "연장근무 기준": [r[1] for r in work_overtime_data["overtime_by_type"]]})
    render_bullets("연장근무 처리 기준", work_overtime_data["overtime_rules"], variant="warn")

def render_work_change_page():
    render_page_header("근무형태 변경시 처리", "근무제도 > 근무형태 변경시 처리", work_change_data["one_line_summary"])
    render_quick_kpis([{"label": "핵심", "value": "변경된 근무 즉시 적용"}, {"label": "보장", "value": "야간근무 후 휴무"}, {"label": "주휴일", "value": "주 1일 보장"}])
    render_bullets("기본원칙", work_change_data["basic_rules"])

def render_designated_off_page():
    render_page_header("지정휴무", "근무제도 > 지정휴무", work_designated_off_data["one_line_summary"])
    render_quick_kpis([{"label": "핵심 판단", "value": "잔여 근무일수"}, {"label": "먼저 확인", "value": "변경 유형"}, {"label": "실무 주의", "value": "근무표 + 인사이동 기준"}])
    c1, c2 = st.columns(2)
    with c1: render_bullets("개념", work_designated_off_data["concept"])
    with c2: render_bullets("부여 기준", work_designated_off_data["grant_rules"])
    render_bullets("사용 기준", work_designated_off_data["usage_rules"])
    tabs = st.tabs(["21주기 기준", "현업일근 기준", "6주기 기준"])
    with tabs[0]: st.table({"변경": [r[0] for r in work_designated_off_data["case_21"]], "조건": [r[1] for r in work_designated_off_data["case_21"]], "결과": [r[2] for r in work_designated_off_data["case_21"]]})
    with tabs[1]: st.table({"변경": [r[0] for r in work_designated_off_data["case_field"]], "조건": [r[1] for r in work_designated_off_data["case_field"]], "결과": [r[2] for r in work_designated_off_data["case_field"]]})
    with tabs[2]: st.table({"변경": [r[0] for r in work_designated_off_data["case_6"]], "조건": [r[1] for r in work_designated_off_data["case_6"]], "결과": [r[2] for r in work_designated_off_data["case_6"]]})
    st.markdown("### 자동 판단")
    user_text = st.text_input("예: 통상에서 21주기로 변경, 잔여 4일")
    if user_text:
        parsed = parse_designated_off_text(user_text)
        result = calculate_designated_off(parsed["case_type"], parsed["remaining_days"], parsed["prev_shift"], parsed["next_shift"])
        render_result_panel(result["result"], result["rule"], "근무표와 인사이동 기준을 함께 확인합니다.", result["reason"])
    render_bullets("먼저 확인할 사항", work_designated_off_data["note"], variant="warn")

def render_leave_general_page():
    render_page_header("휴가 기본원칙", "휴가제도 > 휴가 기본원칙", leave_general_data["one_line_summary"])
    render_quick_kpis([{"label": "사용 가능 기준", "value": "출근의무 있는 날"}, {"label": "기본 절차", "value": "신청 → 승인 → 사용"}, {"label": "먼저 확인", "value": "증빙 / 연락체계 / 중복 여부"}])
    render_drims_box("휴가 신청 후 승인 절차 진행", "휴가 종료 후 증빙 보완이 필요한 경우 기한 내 제출해야 합니다.")
    c1, c2 = st.columns(2)
    with c1: render_bullets("휴가의 법적 의미", leave_general_data["legal_meaning"])
    with c2: render_bullets("휴가실시의 원칙", leave_general_data["principles"])
    render_bullets("적용 시 유의사항", leave_general_data["cautions"], variant="warn")
    st.markdown("### 휴가 종류 한눈에 보기")
    st.table({"구분": [x[0] for x in leave_general_data["leave_types"]], "사용목적": [x[1] for x in leave_general_data["leave_types"]], "일수": [x[2] for x in leave_general_data["leave_types"]], "비고": [x[3] for x in leave_general_data["leave_types"]]})

def render_annual_leave_page():
    render_page_header("연차휴가", "휴가제도 > 연차휴가", annual_leave_data["summary"])
    render_quick_kpis([{"label": "기본 기준", "value": "출근율 + 계속근로연수"}, {"label": "촉진일수", "value": "연간 최대 5일"}, {"label": "특이 대상", "value": "신입사원 / 휴직자"}])
    render_bullets("연차휴가 개요", annual_leave_data["overview"])
    render_bullets("연차휴가 사용촉진 개요", annual_leave_data["promotion"])
    mode = st.radio("계산 유형", ["일반 직원", "휴직·파견·출산전후휴가 사용자", "신입사원(1년 미만/2년차)"], horizontal=True)
    if mode == "일반 직원":
        annual_occured_days = st.number_input("해당 연도 발생 연차일수", min_value=0.0, max_value=30.0, value=15.0, step=1.0)
        promotion_days = int(min(5, annual_occured_days))
        guide = get_promotion_guide(promotion_days, "일반직원")
        render_result_panel(f"촉진일수 {promotion_days}일", "발생 연차일수와 연간 최대 5일 기준 적용", "사용촉진 안내 절차를 진행합니다.", "최종 적용 전 인사자료와 실제 발생 연차일수를 함께 확인해 주세요.")
    elif mode == "휴직·파견·출산전후휴가 사용자":
        work_days = st.number_input("실근무일수", min_value=0, max_value=365, value=273, step=1)
        promotion_days = calculate_promotion_days_for_special_case(work_days)
        guide = get_promotion_guide(promotion_days, "일반직원")
        render_result_panel(f"촉진일수 {promotion_days}일", "5일 × 근무일수 / 365 후 소수점 이하는 절사", "계산 결과에 따라 사용촉진 절차를 적용합니다.", "수당지급 시점에는 실근무일 기준으로 다시 확정될 수 있습니다.")
    else:
        join_month = st.selectbox("입사월", [f"{i}월" for i in range(1, 13)], index=0)
        row = annual_leave_data["new_employee_table"][int(join_month.replace("월", "")) - 1]
        guide = get_promotion_guide(row[4], "신입사원(1년 미만/2년차)")
        render_result_panel(f"1년 미만 촉진일수 {row[4]}일 / 2년차 촉진일수 {row[6]}일", f"입사월 {row[0]} 기준표 적용", "신입사원용 사용촉진 절차를 적용합니다.", "입사월과 실제 발생 연차범위를 함께 확인해 주세요.")
    render_bullets("후속 처리", guide, variant="warn")

def render_official_leave_page():
    render_page_header("공가", "휴가제도 > 공가", official_leave_data["summary"])
    render_quick_kpis([{"label": "성격", "value": "공적 사유 처리"}, {"label": "핵심", "value": "필요시간만 허가"}, {"label": "증빙", "value": "7일 이내 제출"}])
    c1, c2 = st.columns(2)
    with c1: render_bullets("개념", official_leave_data["concept"]); render_bullets("부여기준", official_leave_data["grant_rules"])
    with c2: render_bullets("사용방법", official_leave_data["usage_rules"]); render_bullets("기타사항", official_leave_data["etc_rules"], variant="warn")

def render_sick_leave_page():
    render_page_header("병가", "휴가제도 > 병가", sick_leave_data["summary"])
    render_quick_kpis([{"label": "구분", "value": "공상병가 / 사상병가"}, {"label": "한도", "value": "180일 / 60일"}, {"label": "핵심 증빙", "value": "진단서 또는 방문증빙"}])
    c1, c2 = st.columns(2)
    with c1: render_bullets("개념", sick_leave_data["concept"]); render_bullets("부여기준", sick_leave_data["grant_rules"])
    with c2: render_bullets("사용방법", sick_leave_data["usage_rules"]); render_bullets("적용 시 유의사항", sick_leave_data["etc_rules"], variant="warn")
    leave_type = st.selectbox("병가 종류", ["공상병가", "사상병가"])
    input_days = st.number_input("이번에 사용할 병가일수", min_value=0, max_value=365, value=3, step=1)
    already_used_days = st.number_input("해당 연도 기존 사용 병가일수", min_value=0, max_value=365, value=0, step=1)
    result = calculate_sick_leave_days(leave_type, input_days, already_used_days)
    render_result_panel(f"잔여 가능일수 {result['remaining_days']}일", f"{leave_type} 한도 {result['limit_days']}일 기준 적용", "증빙서류와 동일 질병 여부를 함께 확인합니다.", result["message"])

def render_petition_leave_page():
    render_page_header("청원휴가", "휴가제도 > 청원휴가", petition_leave_data["summary"])
    render_quick_kpis([{"label": "대상", "value": "본인 / 가족 경조사"}, {"label": "핵심 기준", "value": "사유별 일수 상이"}, {"label": "먼저 확인", "value": "관계 / 사유 발생일"}])
    render_bullets("주요 부여기준", petition_leave_data["grant_rules"])
    event_type = st.selectbox("사유 구분", ["결혼", "출산", "입양", "사망", "탈상"])
    relation_options = {"결혼": ["본인", "자녀"], "출산": ["배우자"], "입양": ["본인"], "사망": ["배우자", "본인/배우자의 부모", "본인/배우자의 조부모·외조부모", "자녀/자녀의 배우자", "본인/배우자의 형제자매 및 그 배우자", "본인/배우자 부모의 형제자매 및 그 배우자"], "탈상": ["배우자/본인/배우자의 부모"]}
    relation = st.selectbox("대상 관계", relation_options[event_type])
    is_holiday = st.checkbox("사유 발생일이 휴일 또는 공휴일임", value=False)
    result = calculate_petition_leave(event_type, relation, is_holiday)
    render_result_panel(f"부여 일수 {result['days']}일", f"{event_type} / {relation} 기준 적용", "증빙자료와 사유 발생일 기준으로 휴가를 신청합니다.", result["note"])

def render_comp_leave_page():
    render_page_header("초과근무 보상휴가", "휴가제도 > 초과근무 보상휴가", comp_leave_data["summary"])
    render_quick_kpis([{"label": "대상", "value": "통상근무자"}, {"label": "연간 한도", "value": "6일"}, {"label": "산출 기준", "value": "초과근로 × 1.5"}])
    c1, c2 = st.columns(2)
    with c1: render_bullets("부여기준", comp_leave_data["grant_rules"])
    with c2: render_bullets("사용방법", comp_leave_data["usage_rules"])
    overtime_hours = st.number_input("연장·야간·휴일근로 시간(시간)", min_value=0.0, max_value=500.0, value=2.0, step=0.5)
    result = calculate_comp_leave_hours(overtime_hours)
    render_result_panel(f"적치시간 {result['accumulated_hours']}시간 / 적치일수 {result['accumulated_days']}일", "초과근로시간 + 50% 가산시간 적치", "상·하반기 사용 가능일수와 실제 적치 누계를 같이 확인합니다.", "기간 내 미사용 시 소멸하며 금전보상은 불가합니다.")

def render_special_childcare_leave_page():
    render_page_header("특별휴가(자녀돌봄)", "휴가제도 > 특별휴가(자녀돌봄)", special_childcare_leave_data["summary"])
    render_quick_kpis([{"label": "자녀 1~2명", "value": "연 2일(16시간)"}, {"label": "자녀 3명 이상", "value": "연 3일(24시간)"}, {"label": "사용 단위", "value": "최소 4시간"}])
    render_bullets("사용기준", special_childcare_leave_data["usage_rules"])
    child_count = st.number_input("가족으로 등록된 만 19세 미만 자녀 수", min_value=1, max_value=10, value=1, step=1)
    special_child = st.checkbox("중증장애인 또는 희귀난치성질환 자녀가 있음", value=False)
    entitlement = calculate_childcare_leave_entitlement(child_count, special_child)
    render_result_panel(f"연간 {entitlement['days']}일 / {entitlement['hours']}시간 사용 가능", "자녀 수 및 특수 자녀 조건 기준 적용", "학교행사, 상담, 병원 진료 동행 등 사유와 증빙을 확인합니다.", "학교 밖 체험활동이나 학원 관련 일정은 대상이 아닐 수 있습니다.")

def render_family_care_leave_page():
    render_page_header("가족돌봄휴가", "휴가제도 > 가족돌봄휴가", family_care_leave_data["summary"])
    render_quick_kpis([{"label": "연간 한도", "value": "10일"}, {"label": "급여", "value": "무급"}, {"label": "먼저 확인", "value": "가족관계 / 증빙"}])
    render_bullets("운영방법 및 사용기준", family_care_leave_data["operation_rules"])
    used_days = st.number_input("해당 연도 이미 사용한 가족돌봄휴가 일수", min_value=0, max_value=10, value=0, step=1)
    entitlement = get_family_care_leave_entitlement(used_days)
    render_result_panel(f"잔여 사용 가능일수 {entitlement['remaining_days']}일", "연간 10일 기준 적용", "가족관계 및 신청사유 증빙자료를 첨부해 신청합니다.", "가족돌봄휴가는 무급휴가이며 자녀돌봄휴가와 구분해 사용해야 합니다.")

def render_half_day_leave_page():
    render_page_header("반일휴가 / 휴가정정", "휴가제도 > 반일휴가 / 휴가정정", half_day_leave_data["summary"])
    render_quick_kpis([{"label": "반일 기준", "value": "1회 0.5일"}, {"label": "사용 구분", "value": "오전 / 오후"}, {"label": "정정 절차", "value": "저장 → 삭제 → 재등록"}])
    tab1, tab2 = st.tabs(["반일휴가 안내", "휴가정정 방법"])
    with tab1:
        render_bullets("사용기준", half_day_leave_data["usage_rules"])
        worker_type = st.selectbox("대상자 구분", ["통상근무", "자녀양육지원제"])
        schedule_type = "기본" if worker_type == "통상근무" else st.selectbox("근무유형", ["9to5", "10to6"])
        leave_part = st.selectbox("반일 구분", ["오전", "오후"])
        result = get_half_day_leave_time(worker_type, schedule_type, leave_part)
        render_result_panel(f"휴가시간 {result['leave_time']} / 근무시간 {result['work_time']}", f"{worker_type} / {schedule_type} / {leave_part} 기준 적용", "근무표와 휴게시간 조정 여부를 확인한 뒤 신청합니다.", "근무시간의 중간대에는 사용할 수 없습니다.")
    with tab2:
        render_drims_box("셀프서비스 > 근태관리 > 휴가출장관리 > 휴가신청", "근태일이 경과한 휴가 수정 시 출력물 저장 → 삭제 → 재등록 순으로 처리합니다.")
        render_bullets("휴가정정 순서", half_day_leave_data["correction_rules"], variant="warn")

def render_trip_page():
    render_page_header("출장제도", "출장제도 > 기본 안내", "출장제도는 다음 단계에서 데이터 블록 + 자동 판단 함수 + 페이지 함수 + PAGE_RENDERERS 연결 구조로 계속 확장합니다.")
    render_quick_kpis([{"label": "핵심", "value": "출장명령 후 수행"}, {"label": "먼저 확인", "value": "출장 목적 / 기간 / 여비"}, {"label": "처리 흐름", "value": "신청 → 승인 → 수행"}])
    render_bullets("현재 안내", ["첫번째 파일과 두번째 파일을 통합하면서 기존 근무제도와 휴가제도를 먼저 복원했습니다.", "출장제도는 이 최종 구조 위에서 다음 단계부터 페이지 함수 방식으로 추가하면 됩니다.", "여비 지급, 공무국외여행심사, 참고 여비업무 처리지침은 출장제도 파일을 주시면 같은 방식으로 바로 붙일 수 있습니다."])

def render_placeholder_page(main: str, sub: Optional[str]):
    breadcrumb = main if not sub else f"{main} > {sub}"
    render_page_header("준비 중", breadcrumb, "해당 메뉴는 다음 단계에서 연결 예정입니다.")
    st.info("현재는 핵심 실무 메뉴를 우선 정리하고 있습니다.")

def render_sidebar() -> tuple[str, Optional[str]]:
    with st.sidebar:
        st.title("📘 복무관리")
        st.caption("현장용 조회 · 판단 도구")
        main_keys = list(MENU_CONFIG.keys())
        default_main = st.session_state.get("main_menu", "홈")
        main_index = main_keys.index(default_main) if default_main in main_keys else 0
        main_menu = st.radio("메뉴 선택", main_keys, index=main_index)
        if main_menu == "홈":
            sub_menu = None
        else:
            display_subs = MENU_CONFIG[main_menu]
            internal_subs = [DISPLAY_TO_INTERNAL.get(x, x) for x in display_subs]
            default_sub = st.session_state.get("sub_menu", internal_subs[0] if internal_subs else None)
            display_default = next((d for d in display_subs if DISPLAY_TO_INTERNAL.get(d, d) == default_sub), display_subs[0])
            sub_index = display_subs.index(display_default)
            selected_display = st.radio("세부 항목", display_subs, index=sub_index)
            sub_menu = DISPLAY_TO_INTERNAL.get(selected_display, selected_display)
        st.session_state["main_menu"] = main_menu
        st.session_state["sub_menu"] = sub_menu
        st.markdown("---")
        st.caption("자주 쓰는 기능")
        st.write("- 근무일과 휴일 확인")
        st.write("- 지정휴무 자동 판단")
        st.write("- 연차휴가 자동 판단")
        st.write("- 병가일수 계산")
        st.write("- 휴가정정 절차 확인")
    return main_menu, sub_menu

PAGE_RENDERERS: Dict[tuple[str, Optional[str]], Callable[[], None]] = {
    ("홈", None): render_home_dashboard,
    ("근무제도", "근무일과 휴일"): render_workday_holiday_page,
    ("근무제도", "근무시간과 휴게시간"): render_worktime_break_page,
    ("근무제도", "휴일대체근무제도"): render_work_overtime_page,
    ("근무제도", "근무형태 변경시 처리"): render_work_change_page,
    ("근무제도", "지정휴무"): render_designated_off_page,
    ("휴가제도", "일반사항"): render_leave_general_page,
    ("휴가제도", "연차휴가"): render_annual_leave_page,
    ("휴가제도", "공가"): render_official_leave_page,
    ("휴가제도", "병가"): render_sick_leave_page,
    ("휴가제도", "청원휴가"): render_petition_leave_page,
    ("휴가제도", "보상휴가"): render_comp_leave_page,
    ("휴가제도", "특별휴가(자녀돌봄)"): render_special_childcare_leave_page,
    ("휴가제도", "가족돌봄휴가"): render_family_care_leave_page,
    ("휴가제도", "반일휴가제"): render_half_day_leave_page,
    ("출장제도", "기본 안내"): render_trip_page,
}

main_menu, sub_menu = render_sidebar()
render_global_search()
renderer = PAGE_RENDERERS.get((main_menu, sub_menu))
if renderer:
    renderer()
else:
    render_placeholder_page(main_menu, sub_menu)
