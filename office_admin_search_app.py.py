import streamlit as st

st.set_page_config(page_title="복무관리 매뉴얼 앱", page_icon="📘", layout="wide")

# -----------------------------
# 데이터
# -----------------------------
APP_TITLE = "복무관리 메뉴얼 앱"
APP_SUBTITLE = "근무제도 > 근무일과 휴일"

workday_holiday_data = {
    "title": "근무일과 휴일",
    "one_line_summary": "근무일은 휴일·휴무일을 제외한 날이고, 휴일은 근무형태에 따라 다르게 적용됩니다.",
    "definitions": {
        "근무일": "취업규칙상 정해진 근무시간 중 휴일 및 휴무일을 제외한 날",
        "휴일(휴무일)": "취업규칙에 따라 근로의무가 없는 날"
    },
    "work_types": [
        {
            "name": "통상근무",
            "summary": "가장 일반적인 형태",
            "holidays": ["토요일(무급휴일)", "일요일"],
            "practical": "사무직처럼 달력 기준으로 이해하면 가장 쉽습니다."
        },
        {
            "name": "현업일근",
            "summary": "요일 고정형이 아니라 지정형 휴무",
            "holidays": ["지정휴무: 주 2일", "연중지휴: 월 1일"],
            "practical": "달력보다 소속 부서의 지정 기준과 운영계획을 먼저 확인해야 합니다."
        },
        {
            "name": "교대근무",
            "summary": "요일보다 근무주기와 근무표가 중요",
            "holidays": [
                "6주기: 근무형태에서 발생되는 6주기당 2일",
                "지정휴무: 월 2일(주A 1일, 주B 1일)",
                "분기지휴: 8일(분기당 2일)",
                "21주기: 지정휴무 21주기당 2일(야간 2일 지정 불가)",
                "야간근무 후 휴일",
                "분기지휴: 4일(분기당 1일)"
            ],
            "practical": "일요일이라고 무조건 쉬는 개념이 아니라 근무표상 휴일인지 먼저 봐야 합니다."
        },
        {
            "name": "교번근무",
            "summary": "기관사 등 근무표 기반 운영",
            "holidays": ["근무표에 의한 휴일", "대기휴무 등 발생된 휴일", "분기지휴: 4일(분기당 1일)"],
            "practical": "근무표가 사실상 기준표 역할을 합니다."
        }
    ],
    "public_holiday_rule": "법령 및 정부에서 정한 공휴일과 공사창립일은 유급휴일로 부여하되, 교대·교번근무자는 근무형태에서 발생된 휴일로, 현업일근자는 지정된 휴무일로 대체합니다. 단, 근로자의 날(5.1)은 휴일근무수당 지급 대상입니다.",
    "substitute_holiday": "명절휴일이 공휴일과 겹치거나 3·1절, 광복절, 개천절, 한글날, 어린이날이 토요일 또는 다른 공휴일과 겹치면 다음 첫 번째 비공휴일을 공휴일로 합니다. 이 기준은 통상근무자 이해에 특히 중요합니다.",
    "mistakes": [
        "공휴일이면 모든 직원이 같은 방식으로 쉬는 것은 아닙니다.",
        "교대·교번근무는 달력보다 근무표가 우선입니다.",
        "근로자의 날은 일반 공휴일과 동일하게 보면 실무상 오류가 생길 수 있습니다."
    ],
    "faq": [
        {
            "q": "일요일이면 무조건 휴일인가요?",
            "a": "통상근무자는 일반적으로 그렇지만, 교대·교번근무자는 근무표에 따라 일요일에도 근무할 수 있습니다."
        },
        {
            "q": "공휴일은 현업일근도 그냥 쉬나요?",
            "a": "아닙니다. 현업일근은 지정된 휴무일로 대체되는 구조를 먼저 확인해야 합니다."
        },
        {
            "q": "제일 먼저 뭘 확인해야 하나요?",
            "a": "해당 직원의 근무형태가 통상근무인지, 현업일근인지, 교대근무인지, 교번근무인지부터 확인하는 것이 가장 중요합니다."
        }
    ]
}

worktime_break_data = {
    "title": "근무시간과 휴게시간",
    "one_line_summary": "기본은 1일 8시간, 1주 40시간이며, 근무형태별로 근무시간과 휴게시간이 다르고 변경·탄력근로 운용에도 제한이 있습니다.",
    "basic_rules": [
        "근무시간은 1일 8시간, 1주 40시간입니다.",
        "1주는 휴일을 포함한 7일(월~일) 기준입니다.",
        "휴게시간은 업무에 지장을 초래하지 않는 범위 내에서 자유롭게 사용할 수 있습니다.",
        "분야별 근무형태, 근무시간 및 휴게시간은 취업규칙 별표 1에 따르며, 계절 변화나 업무 특수사정이 있으면 조정할 수 있습니다."
    ],
    "work_types": [
        {"name": "통상근무", "time": "월~금 09:00~18:00", "break": "1시간 (12:00~13:00)", "actual": "8시간", "cycle": "일반 주간근무"},
        {"name": "현업일근", "time": "09:00~18:00", "break": "1시간 (12:00~13:00)", "actual": "8시간", "cycle": "주 단위"},
        {"name": "3호선 역순회요원 (3조2교대)", "time": "주간A 05:20~14:50 / 주간B 14:00~24:30", "break": "각 1시간", "actual": "주간A 8.5시간 / 주간B 9.5시간", "cycle": "6일 주기"},
        {"name": "역무·관제·통신·변전·차량운영·전자(AFC)", "time": "주간 09:00~18:00 / 야간 18:00~익일 09:00", "break": "주간 1시간 / 야간 4시간 30분", "actual": "주간 8시간 / 야간 10.5시간", "cycle": "21일 주기"},
        {"name": "전자(PSD)·전기·신호·건축·토목·기계", "time": "주간 09:00~18:00 / 야간 18:00~익일 09:00", "break": "주간 1시간 / 야간 4시간 30분", "actual": "주간 8시간 / 야간 10.5시간", "cycle": "21일 주기"},
        {"name": "차량검수", "time": "주간 09:00~18:00 / 야간 18:00~익일 09:00", "break": "주간 1시간 / 야간 4시간 30분", "actual": "주간 8시간 / 야간 10.5시간", "cycle": "21일 주기"},
        {"name": "운행관리(운용)", "time": "주간 09:00~18:00 / 야간 18:00~익일 09:00", "break": "주간 1시간 / 야간 4시간 30분", "actual": "주간 8시간 / 야간 10.5시간", "cycle": "21일 주기"},
        {"name": "야간격일제", "time": "18:00~익일 09:00", "break": "4시간 30분", "actual": "10.5시간", "cycle": "2일 주기"},
        {"name": "교번근무 (1,2호선 차량운영 기관사)", "time": "기관사 근무표에 의함", "break": "교번운용표에 의함", "actual": "교번운용표에 의함", "cycle": "교번운용표 기준"}
    ],
    "change_rules": [
        "단위기간 내 지정된 근무일과 근로시간은 원칙적으로 변경이 제한됩니다.",
        "현업 운영상 부득이하여 변경하지 않으면 본래 업무를 달성할 수 없는 경우에만 예외적으로 변경할 수 있습니다.",
        "기본적인 근무형태가 1주일 이상 변경되면 노무복지팀장 협조결재 후 변경 가능합니다.",
        "탄력근로 범위 내에서도 1일 최대근로시간은 12시간을 넘지 않아야 합니다.",
        "휴게시간은 반드시 근무시간 도중에 주어져야 하며, 현업상 부득이한 경우 소속부서장이 조정운용할 수 있습니다."
    ],
    "flex_rules": [
        "공사는 1개월 단위 탄력적 근로시간제를 운영합니다. 단, 교번근무자 및 3호선 차량검수 분야는 3개월 이내 단위입니다.",
        "단위기간 평균 1주 40시간을 초과하지 않는 범위에서 특정 주 52시간, 특정 일 12시간까지 근무할 수 있습니다.",
        "업무상 필요 시 연장근무, 야간근무, 휴일근무를 명할 수 있으며 보수규정에 따라 수당이 지급됩니다.",
        "야간근무는 오후 10시부터 오전 6시까지 사이의 근로를 뜻합니다."
    ],
    "overtime_notes": [
        "휴일대체 및 평일 연장근무는 해당 주 총근로시간이 주52시간 범위 내여야 합니다.",
        "해당 1개월을 평균한 1주 소정근로시간도 평균 40시간 이내여야 합니다.",
        "휴일대체는 직원에게 사전 24시간 이전에 교체할 휴일을 특정하여 고지해야 합니다.",
        "평일(무급휴무일 포함) 8시간 미만 연장근무 시에는 범위 초과근로가 발생하지 않는 범위 내에서 근로시간의 1.5배만큼 면제할 수 있습니다.",
        "관리·감독업무 수행 관리자 등은 초과근무수당 지급 제외 대상이므로 근로시간면제 대상에서도 제외됩니다."
    ],
    "restriction_table": [
        ["남성근로자", "1주 40시간(1일 8시간)", "1주 12시간", "가능", "합의"],
        ["여성근로자", "1주 40시간(1일 8시간)", "1주 12시간", "동의", "동의"],
        ["임신 중인 여성근로자", "1주 40시간(1일 8시간)", "금지", "명시적 청구 + 노동부 인가", "명시적 청구 + 노동부 인가"],
        ["출산 후 1년 이하 여성근로자", "1주 40시간(1일 8시간)", "1주 6시간 (1일 2시간, 1년 150시간)", "동의 + 노동부 인가", "동의 + 노동부 인가"],
        ["18세 미만자(연소자)", "1주 35시간(1일 7시간)", "1주 5시간(1일 1시간)", "동의 + 노동부 인가", "동의 + 노동부 인가"],
        ["단시간근로자", "1주 40시간(1일 8시간)", "1주 12시간", "가능", "합의"],
        ["임신기근로시간 단축", "1일 2시간 이내 단축(최저 1일 6시간)", "금지", "명시적 청구 + 노동부 인가", "명시적 청구 + 노동부 인가"],
        ["육아기근로시간 단축", "1주 15시간~35시간", "1주 12시간", "가능", "합의"]
    ],
    "faq": [
        {"q": "기본 근무시간은 무조건 09:00~18:00인가요?", "a": "아닙니다. 통상근무와 현업일근은 그렇지만 교대·교번·야간격일제는 분야별 근무표와 주기에 따라 다릅니다."},
        {"q": "휴게시간은 꼭 점심시간처럼 한 번에 줘야 하나요?", "a": "원칙은 근무시간 도중 부여이며, 현업 운영상 부득이한 경우에는 소속부서장이 조정하거나 일정 부분 단속적으로 부여할 수 있습니다."},
        {"q": "탄력근로를 하면 마음대로 오래 근무해도 되나요?", "a": "아닙니다. 평균 주40시간, 특정 주52시간, 특정 일12시간 한도 안에서만 가능합니다."}
    ]
}

work_overtime_data = {
    "title": "휴일대체근무제도",
    "one_line_summary": "연장근무·야간근무·휴일근무는 시간대와 근무시간에 따라 보상휴가Ⅱ 또는 대체휴일로 처리되며, 사전 고지와 시간 기준 확인이 핵심입니다.",
    "overview": [
        "연장근무는 정해진 근로시간을 초과하는 시간이며 해당 시간의 1.5배를 보상합니다.",
        "야간근무는 22:00부터 06:00까지의 근로시간이며 해당 시간의 0.5배를 보상합니다.",
        "연장근로이면서 야간근로에 해당하면 연장·야간 모두 보상합니다."
    ],
    "overtime_by_type": [
        ["통상근무자", "8시간을 초과하는 시간"],
        ["교대 21일·8일주기", "주간 8시간 초과 / 야간 10.5시간 초과"],
        ["교대 6일주기", "주간A 8.5시간 초과 / 주간B 9.5시간 초과"]
    ],
    "overtime_rules": [
        "연장근무는 1주 12시간을 초과할 수 없습니다.",
        "휴게시간은 4시간에 30분 이상, 8시간에 1시간 이상을 준수해야 합니다.",
        "연장근무 사유가 생기면 휴게시간을 조정해 가급적 연장근무가 발생하지 않도록 해야 합니다.",
        "조정이 불가하면 보상휴가Ⅱ를 부여합니다.",
        "취업규칙에 정한 시간 외의 야간근무는 보상휴가Ⅱ 부여가 원칙이고, 야간수당은 근무계획 수립 시 노무복지팀 협조를 받은 경우 지급 가능합니다."
    ],
    "comp_leave": [
        "연장·야간근무에 가산율을 적용해 휴가를 부여합니다.",
        "연장근무: 해당 시간의 1.5배",
        "야간근무: 해당 시간의 0.5배",
        "연장근무와 야간근무 중복 시: 2.0배",
        "사유별 발생 휴가는 적치 가능합니다.",
        "당해연도 발생 휴가는 익년도 12월 31일까지 사용합니다.",
        "휴가는 '일' 또는 '반일' 사용이 원칙이며, 시간 단위 사용 시 출퇴근 시간 조정을 시행합니다."
    ],
    "holiday_substitution": [
        "통상근무자의 휴(무)일 근무가 예정된 경우 사전에 다른 근무일을 휴일로 지정하는 제도입니다.",
        "사전에 대체휴일을 지정하면 원래의 휴일은 근무일이 됩니다.",
        "5시간 미만 근무 시에는 휴일대체가 아니라 보상휴가Ⅱ 기준을 적용합니다.",
        "휴일대체는 당초 휴일의 24시간 전까지 직원에게 사실을 고지해야 합니다.",
        "직원의 의견을 반영해 대체할 휴일을 특정해야 합니다."
    ],
    "holiday_substitution_table": [
        ["5시간 이하 근무", "근무시간의 1.5배 보상휴가Ⅱ 적용"],
        ["6시간 초과~8시간 이하", "대체휴일 1일 부여"],
        ["8시간 초과 근무", "대체휴일 1일 + 초과시간의 1.5배 보상휴가Ⅱ"]
    ],
    "holiday_use": [
        "대체휴일은 근무일 이전 5일부터 근무일 이후 5일까지 사용합니다.",
        "교육·출장 등 부득이한 사유로 기간 내 사용이 불가하면 당초 휴일로부터 1개월 내 사용 가능합니다."
    ],
    "attendance_processing": {
        "basic": [
            "연장근로에 대한 보상휴가Ⅱ는 익일 근무에 사용합니다.",
            "초과근무가 00시 이후 종료되면 휴식시간 부여를 위해 오전근무 면제가 원칙입니다.",
            "야간근로에 대한 보상휴가Ⅱ는 적치하여 익년도 말까지 사용합니다."
        ],
        "after_midnight_start": [
            "초과근무가 00시 이후 시작되어 09시 이전 종료되면 새벽근무 당일 오전근무를 면제합니다.",
            "실근로시간만큼 새벽근무 당일 오후근무도 면제합니다.",
            "야간근로 보상휴가Ⅱ는 적치하여 익년도 말까지 사용합니다."
        ],
        "cross_midnight_workday": [
            ["2.5시간 초과", "당일 통상근무에서 초과시간만큼 제외 + 익일 근로면제 + 야간근로 보상휴가Ⅱ 적치"],
            ["2.5시간", "당일 조정 없음 + 익일 근로면제 + 야간근로 보상휴가Ⅱ 적치"],
            ["2.5시간 미만", "당일 조정 없음 + 익일 오전근무 면제 + 연장근무 보상휴가Ⅱ는 익일 오후 사용 + 야간근로 보상휴가Ⅱ 적치"]
        ],
        "cross_midnight_holiday": [
            ["2.5시간 초과", "당일 통상근무에서 초과시간만큼 제외 + 연장근무 보상휴가Ⅱ 익년도 말까지 사용 + 야간근로 보상휴가Ⅱ 적치"],
            ["2.5시간", "당일 조정 없음 + 연장근무 보상휴가Ⅱ 익년도 말까지 사용 + 야간근로 보상휴가Ⅱ 적치"],
            ["2.5시간 미만", "당일 조정 없음 + 연장근무 보상휴가Ⅱ 익년도 말까지 사용 + 야간근로 보상휴가Ⅱ 적치"]
        ]
    },
    "qa": [
        {"q": "보상휴가Ⅱ 적용 대상은?", "a": "통상근무자뿐 아니라 교대근무자도 적용 대상이며, 취업규칙 등에 정해진 근로시간보다 초과해 근무하게 될 경우 보상휴가Ⅱ를 적용할 수 있습니다."},
        {"q": "야간감독 등이 2.5시간 초과할 경우 당일 근로면제 방법은?", "a": "초과하는 시간만큼 조기퇴근, 휴게시간 조정 등 부서 내 사정에 따라 조정 가능합니다."},
        {"q": "보상휴가Ⅱ 사용방법은?", "a": "기존 보상휴가 상황관리부를 활용하여 적치 관리하고, 반일 또는 1일 단위 주간근무 사용을 원칙으로 하되 인력운용과 부서 사정을 고려해 반일 미만도 사용할 수 있습니다."},
        {"q": "오전근무, 오후근무의 기준은?", "a": "반일휴가 기준을 준용하여 오전근무는 09:00~13:30, 오후근무는 13:30~18:00으로 봅니다."}
    ]
}

work_change_data = {
    "title": "근무형태 변경시 처리",
    "one_line_summary": "근무형태 변경 시 변경된 근무를 즉시 적용하며, 변경 전 야간근무에 대한 휴무 보장과 주휴일 확보가 핵심입니다.",
    "basic_rules": [
        "근무형태 변경 시에는 변경된 근무를 그대로 적용합니다.",
        "변경 전 야간근무로 인해 발생한 휴무일은 반드시 보장합니다.",
        "근로기준법 및 취업규칙에 따라 1주(월~일)에 주휴일 1일을 반드시 보장해야 합니다."
    ],
    "case_21": [
        ["통상 → 21주기", "통상", "주간/야간/휴일", "동일 적용"],
        ["21주기 → 21주기 (주간)", "주간", "야간/휴일", "동일 적용"],
        ["21주기 → 21주기 (야간)", "야간", "주간", "휴일 전환"],
        ["21주기 → 통상", "주간/야간/휴일", "통상", "통상 또는 휴일 적용"]
    ],
    "case_6": [
        ["통상 → 6주기", "통상", "주간A/B/비번/휴일", "변경근무 적용"],
        ["6주기 → 6주기", "주A1/주A2/주B1/주B2", "순환", "근무표 기준"],
        ["6주기 → 통상", "주B2", "통상", "비번 또는 통상"]
    ],
    "case_mix": [
        ["6주기 → 21주기", "변경된 근무형태 따름", "주간A/B/비번/휴일", "동일 적용"],
        ["21주기 → 6주기 (야간)", "야간", "주간A/B/비번", "휴일 후 전환"],
        ["21주기 → 6주기 (휴일)", "휴일", "주간A/B", "동일 적용"]
    ],
    "note": [
        "주간 근무의 경우 소속장 인력운용 상황에 따라 주A, 주B를 적의 운영합니다.",
        "세부 근무 적용은 실제 근무표 및 인사이동 기준을 함께 확인해야 정확합니다."
    ]
}

work_designated_off_data = {
    "title": "지정휴무",
    "one_line_summary": "근무형태 변경 시 지정휴무는 ‘잔여 근무일수 + 변경 유형’으로 결정된다.",

    "concept": [
        "주 1회 주휴일 보장은 무조건 적용",
        "21주기 근무자는 지정휴무 2일 중 1일은 주휴 개념으로 사용"
    ],

    "grant_rules": [
        "현업일근: 주 2일 지정휴무",
        "6주기: 월 2일 (주A 1일, 주B 1일)",
        "21주기: 총 2일 (주야 구분 없음)",
        "교번근무: 분기/연간 기준 관리"
    ],

    "usage_rules": [
        "지정휴무는 해당 월 또는 주기 내 반드시 사용",
        "미사용 시 소멸 (이월 불가)",
        "사용계획은 사전 승인 필요",
        "변경 시 본인 동의 필요"
    ],

    "case_21": [
        ["통상 → 21주기", "조건 무관", "2일 발생"],
        ["주간 → 야간", "4일 이상", "1일 발생"],
        ["주간 → 야간", "3일 이하", "미발생"],
        ["야간 → 주간", "3일 이상", "2일 발생"],
        ["야간 → 주간", "2일 이하", "1일 발생"]
    ],

    "case_field": [
        ["현업일근 → 21주기", "5일 이상", "2일 발생"],
        ["현업일근 → 21주기", "4일 이하", "1일 발생"],
        ["21주기 → 현업일근", "5일 이상", "2일 발생"],
        ["21주기 → 현업일근", "4일 이하", "1일 발생"]
    ],

    "case_6": [
        ["통상/21주기 → 6주기", "1~6일", "월 2회"],
        ["통상/21주기 → 6주기", "7~20일", "월 1회"],
        ["통상/21주기 → 6주기", "21일 이상", "미발생"]
    ],

    "note": [
        "지정휴무는 ‘잔여 근무일수’가 핵심 판단 기준",
        "근무표 + 인사이동 기준 같이 봐야 정확",
        "현장에서 가장 많이 틀리는 파트"
    ]
}

import re

def parse_designated_off_text(user_text: str):
    text = user_text.replace(" ", "")
    case_type = None
    prev_shift = ""
    next_shift = ""
    remaining_days = None

    if "현업일근" in text:
        case_type = "현업일근 기준"
        if "현업일근" in text and "21주기" in text:
            if text.index("현업일근") < text.index("21주기"):
                prev_shift = "현업일근→21주기"
            else:
                prev_shift = "21주기→현업일근"
    elif "6주기" in text:
        case_type = "6주기 기준"
        prev_shift = "통상/21주기→6주기"
    elif "21주기" in text:
        case_type = "21주기 기준"
        if "통상" in text and "21주기" in text:
            prev_shift = "통상→21주기"
        elif "주간" in text and "야간" in text:
            if text.index("주간") < text.index("야간"):
                prev_shift = "주간"
                next_shift = "야간"
            else:
                prev_shift = "야간"
                next_shift = "주간"

    match = re.search(r"([0-9]+)일", text)
    if match:
        remaining_days = int(match.group(1))

    return {
        "case_type": case_type,
        "prev_shift": prev_shift,
        "next_shift": next_shift,
        "remaining_days": remaining_days,
    }


def calculate_designated_off(case_type: str, remaining_days: int, prev_shift: str = "", next_shift: str = ""):
    result = {
        "result": "계산할 수 없습니다.",
        "reason": "입력값이 부족하거나 현재 규칙에 없는 조합입니다.",
        "rule": "지정휴무 표 기준을 다시 확인하세요."
    }

    if case_type == "21주기 기준":
        if prev_shift == "통상→21주기":
            result["result"] = "2일 발생"
            result["reason"] = "통상에서 21주기로 변경되는 경우는 잔여근무일수와 관계없이 2일 발생 기준입니다."
            result["rule"] = "21주기당 지정휴무 사용기준: 통상 → 21주기(주간) 시 2일 발생"
            return result
        if prev_shift == "주간" and next_shift == "야간":
            if remaining_days >= 4:
                result["result"] = "1일 발생"
                result["reason"] = f"주간에서 야간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 4일 이상 기준에 해당합니다."
            else:
                result["result"] = "미발생"
                result["reason"] = f"주간에서 야간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 3일 이하 기준에 해당합니다."
            result["rule"] = "21주기 기준: 주간 → 야간, 4일 이상 1일 발생 / 3일 이하 미발생"
            return result
        if prev_shift == "야간" and next_shift == "주간":
            if remaining_days >= 3:
                result["result"] = "2일 발생"
                result["reason"] = f"야간에서 주간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 3일 이상 기준에 해당합니다."
            else:
                result["result"] = "1일 발생"
                result["reason"] = f"야간에서 주간으로 변경되고 잔여근무일수가 {remaining_days}일이므로 2일 이하 기준에 해당합니다."
            result["rule"] = "21주기 기준: 야간 → 주간, 3일 이상 2일 발생 / 2일 이하 1일 발생"
            return result

    if case_type == "현업일근 기준" and prev_shift in ["현업일근→21주기", "21주기→현업일근"]:
        if remaining_days >= 5:
            result["result"] = "2일 발생"
            result["reason"] = f"{prev_shift} 변경이고 잔여근무일수가 {remaining_days}일이므로 5일 이상 기준입니다."
        else:
            result["result"] = "1일 발생"
            result["reason"] = f"{prev_shift} 변경이고 잔여근무일수가 {remaining_days}일이므로 4일 이하 기준입니다."
        result["rule"] = "현업일근 기준: 5일 이상 2일 발생 / 4일 이하 1일 발생"
        return result

    if case_type == "6주기 기준" and prev_shift == "통상/21주기→6주기":
        if 1 <= remaining_days <= 6:
            result["result"] = "월 2회"
            result["reason"] = f"배치일 또는 잔여일수가 {remaining_days}일이므로 1~6일 구간입니다."
        elif 7 <= remaining_days <= 20:
            result["result"] = "월 1회"
            result["reason"] = f"배치일 또는 잔여일수가 {remaining_days}일이므로 7~20일 구간입니다."
        else:
            result["result"] = "미발생"
            result["reason"] = f"배치일 또는 잔여일수가 {remaining_days}일이므로 21일 이상 구간입니다."
        result["rule"] = "6주기 기준: 1~6일 월 2회 / 7~20일 월 1회 / 21일 이상 미발생"
        return result

    return result

import re


def parse_designated_off_text(user_text: str):
    text = user_text.replace(" ", "")
    case_type = None
    prev_shift = ""
    next_shift = ""
    remaining_days = None
    prior_used_days = None
    prior_weekday_days = None
    changed_work_type = ""

    if "현업일근" in text:
        case_type = "현업일근 기준"
        if "현업일근" in text and "21주기" in text:
            if text.index("현업일근") < text.index("21주기"):
                prev_shift = "현업일근→21주기"
            else:
                prev_shift = "21주기→현업일근"
    elif "6주기" in text:
        case_type = "6주기 기준"
        if ("통상" in text or "21주기" in text) and "6주기" in text:
            prev_shift = "통상/21주기→6주기"
        elif "6주기" in text and "21주기" in text:
            prev_shift = "6주기→21주기"
    elif "교번근무" in text or "교번" in text:
        case_type = "분기연간 기준"
        if "21주기" in text and ("교번근무" in text or "교번" in text):
            changed_work_type = "21주기↔교번"
    elif "21주기" in text:
        case_type = "21주기 기준"
        if "통상" in text and "21주기" in text:
            prev_shift = "통상→21주기"
        elif "주간" in text and "야간" in text:
            if text.index("주간") < text.index("야간"):
                prev_shift = "주간"
                next_shift = "야간"
            else:
                prev_shift = "야간"
                next_shift = "주간"
        elif "주간근무" in text and ("교대" in text or "교번" in text or "통상" in text):
            prev_shift = "21주기주간→기타"
            if "교대" in text:
                changed_work_type = "교대근무"
            elif "교번" in text:
                changed_work_type = "교번근무"
            elif "통상" in text:
                changed_work_type = "통상근무"

    day_matches = re.findall(r"([0-9]+)일", text)
    if day_matches:
        remaining_days = int(day_matches[0])
        if len(day_matches) > 1:
            prior_used_days = int(day_matches[1])
    week_matches = re.findall(r"([0-9]+)일내|([0-9]+)일이상", text)
    _ = week_matches

    if "주간근무일수" in text:
        match = re.search(r"주간근무일수[^0-9]*([0-9]+)", text)
        if match:
            prior_weekday_days = int(match.group(1))

    return {
        "case_type": case_type,
        "prev_shift": prev_shift,
        "next_shift": next_shift,
        "remaining_days": remaining_days,
        "prior_used_days": prior_used_days,
        "prior_weekday_days": prior_weekday_days,
        "changed_work_type": changed_work_type,
    }



def calculate_designated_off(case_type: str, remaining_days: int | None = None, prev_shift: str = "", next_shift: str = "", prior_used_days: int | None = None, prior_weekday_days: int | None = None, changed_work_type: str = ""):
    result = {
        "result": "계산할 수 없습니다.",
        "reason": "입력값이 부족하거나 현재 규칙에 없는 조합입니다.",
        "rule": "지정휴무 표 기준을 다시 확인하세요."
    }

    if case_type == "21주기 기준":
        if prev_shift == "통상→21주기":
            result["result"] = "2일 발생"
            result["reason"] = "통상 또는 21주기에서 21주기 주간근무로 전환되는 경우 잔여근무일수와 무관하게 2일 발생 기준입니다."
            result["rule"] = "21주기당 지정휴무 사용기준: 통상 or 21주기 ⇒ 21주기(주간) 시 2일 발생"
            return result

        if prev_shift == "주간" and next_shift == "야간" and remaining_days is not None:
            if remaining_days >= 4:
                result["result"] = "1일 발생"
                result["reason"] = f"21주기 주간에서 야간으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 4일 이상 기준입니다."
            else:
                result["result"] = "미발생"
                result["reason"] = f"21주기 주간에서 야간으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 3일 이하 기준입니다."
            result["rule"] = "21주기당 지정휴무 사용기준: 교대(주간) → 교대(야간), 4일 이상 1일 발생 / 3일 이하 미발생"
            return result

        if prev_shift == "야간" and next_shift == "주간" and remaining_days is not None:
            if remaining_days >= 3:
                result["result"] = "2일 발생"
                result["reason"] = f"21주기 야간에서 주간으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 3일 이상 기준입니다."
            else:
                result["result"] = "1일 발생"
                result["reason"] = f"21주기 야간에서 주간으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 2일 이하 기준입니다."
            result["rule"] = "21주기당 지정휴무 사용기준: 교대(야간) → 교대(주간), 3일 이상 2일 발생 / 2일 이하 1일 발생"
            return result

        if prev_shift == "21주기주간→기타" and prior_weekday_days is not None:
            if prior_weekday_days <= 3:
                result["result"] = "미발생"
                result["reason"] = f"21주기 주간근무에서 {changed_work_type}로 변경되었고 변경 전 주간 근무일수가 {prior_weekday_days}일이므로 3일 이내 기준입니다."
            elif 4 <= prior_weekday_days <= 6:
                result["result"] = "1일 발생"
                result["reason"] = f"21주기 주간근무에서 {changed_work_type}로 변경되었고 변경 전 주간 근무일수가 {prior_weekday_days}일이므로 4~6일 이내 기준입니다."
            else:
                result["result"] = "2일 발생"
                result["reason"] = f"21주기 주간근무에서 {changed_work_type}로 변경되었고 변경 전 주간 근무일수가 {prior_weekday_days}일이므로 7일 근무 기준입니다."
            result["rule"] = "21주기 ⇒ 기타근무형태: 변경 전 주간 근무일수 3일 이내 미발생 / 4~6일 이내 1일 발생 / 7일 근무 2일 발생"
            return result

    if case_type == "현업일근 기준" and prev_shift in ["현업일근→21주기", "21주기→현업일근"] and remaining_days is not None:
        if prev_shift == "현업일근→21주기":
            if prior_used_days == 2:
                result["result"] = "1일 발생"
                result["reason"] = "현업일근에서 21주기(주간)로 변경 시 변경 전 지정휴무 사용일수 2일이면 1일 발생합니다."
                result["rule"] = "현업일근 ⇒ 21주기(주간): 변경 전 지정휴무 사용일수 2일일 때 1일 발생"
                return result
            if prior_used_days is not None and prior_used_days <= 1:
                result["result"] = "2일 발생"
                result["reason"] = "현업일근에서 21주기(주간)로 변경 시 변경 전 지정휴무 사용일수 1일 이하이면 2일 발생합니다."
                result["rule"] = "현업일근 ⇒ 21주기(주간): 변경 전 지정휴무 사용일수 1일 이하일 때 2일 발생"
                return result
            if remaining_days >= 4:
                result["result"] = "1일 발생"
                result["reason"] = f"현업일근에서 21주기(야간)로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 4일 이상 기준입니다."
            else:
                result["result"] = "미발생"
                result["reason"] = f"현업일근에서 21주기(야간)로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 3일 이하 기준입니다."
            result["rule"] = "현업일근 ⇒ 21주기(야간): 4일 이상 1일 발생 / 3일 이하 미발생"
            return result

        if prev_shift == "21주기→현업일근":
            if remaining_days >= 5:
                result["result"] = "2일 발생"
                result["reason"] = f"21주기 등에서 현업일근으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 5일 이상 기준입니다."
            else:
                result["result"] = "1일 발생"
                result["reason"] = f"21주기 등에서 현업일근으로 변경되고 변경 후 잔여근무일수가 {remaining_days}일이므로 4일 이하 기준입니다."
            result["rule"] = "교대·교번근무 ⇒ 현업일근: 5일 이상 2일 발생 / 4일 이하 1일 발생"
            return result

    if case_type == "6주기 기준" and prev_shift == "통상/21주기→6주기" and remaining_days is not None:
        if 1 <= remaining_days <= 6:
            result["result"] = "월 2회"
            result["reason"] = f"통상/21주기에서 6주기로 변경 시 근무지 배치일 또는 잔여일수가 {remaining_days}일이므로 1~6일 구간입니다."
        elif 7 <= remaining_days <= 20:
            result["result"] = "월 1회"
            result["reason"] = f"통상/21주기에서 6주기로 변경 시 근무지 배치일 또는 잔여일수가 {remaining_days}일이므로 7~20일 구간입니다."
        else:
            result["result"] = "미발생"
            result["reason"] = f"통상/21주기에서 6주기로 변경 시 근무지 배치일 또는 잔여일수가 {remaining_days}일이므로 21일 이상 구간입니다."
        result["rule"] = "6주기 지정휴무 사용기준: 1~6일 월 2회 / 7~20일 월 1회 / 21일 이상 미발생"
        return result

    if case_type == "분기연간 기준":
        if changed_work_type == "21주기↔교번":
            result["result"] = "분기지정휴무일수 통합 관리 / 연간지정휴무일수 통합 관리"
            result["reason"] = "21주기와 교번 간 변경은 분기·연간 지정휴무를 각각 통합 관리합니다."
            result["rule"] = "근무형태 변경 시 분기·연간 지정휴무 사용기준: 21주기 ↔ 교번은 분기지정휴무일수 통합 관리, 연간지정휴무일수 통합 관리"
            return result

    return result

# -----------------------------
# 스타일
# -----------------------------
CUSTOM_CSS = """
<style>
.block-card {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px 20px;
    background: #ffffff;
    margin-bottom: 14px;
}
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.point-box {
    border-left: 5px solid #2563eb;
    background: #eff6ff;
    padding: 14px 16px;
    border-radius: 10px;
    margin: 10px 0 16px 0;
}
.warn-box {
    border-left: 5px solid #f59e0b;
    background: #fffbeb;
    padding: 14px 16px;
    border-radius: 10px;
    margin: 10px 0 16px 0;
}
.small-muted {
    color: #6b7280;
    font-size: 0.92rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.title("📘 복무관리")
    st.caption("앱 시안 1차")

    main_menu = st.radio(
        "메뉴 선택",
        ["근무제도", "휴가제도", "출장제도", "기타근태제도", "휴직제도"],
        index=0
    )

    if main_menu == "근무제도":
        sub_menu = st.radio(
            "세부 항목",
            [
                "근무일과 휴일",
                "근무시간과 휴게시간",
                "휴일대체근무제도",
                "근무형태 변경시 처리",
                "지정휴무"
            ],
            index=0
        )
    else:
        sub_menu = None

# -----------------------------
# 헤더
# -----------------------------
st.title(APP_TITLE)
if sub_menu:
    st.caption(f"{main_menu} > {sub_menu}")
else:
    st.caption(main_menu)

# -----------------------------
# 화면 렌더링
# -----------------------------
if main_menu == "근무제도" and sub_menu == "근무일과 휴일":
    st.markdown(f"## {workday_holiday_data['title']}")

    st.markdown(
        f"<div class='point-box'><b>한줄 핵심</b><br>{workday_holiday_data['one_line_summary']}</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>근무일이란?</div>", unsafe_allow_html=True)
        st.write(workday_holiday_data["definitions"]["근무일"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>휴일(휴무일)이란?</div>", unsafe_allow_html=True)
        st.write(workday_holiday_data["definitions"]["휴일(휴무일)"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 근무형태별 휴일 정리")
    selected_type = st.selectbox(
        "근무형태를 선택하세요",
        [item["name"] for item in workday_holiday_data["work_types"]]
    )

    selected_data = next(item for item in workday_holiday_data["work_types"] if item["name"] == selected_type)

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{selected_data['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted'>{selected_data['summary']}</div>", unsafe_allow_html=True)
    st.markdown("#### 휴일 기준")
    for holiday in selected_data["holidays"]:
        st.write(f"- {holiday}")
    st.markdown("#### 실무 해석")
    st.write(selected_data["practical"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 공휴일 처리")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.write(workday_holiday_data["public_holiday_rule"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 대체공휴일")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.write(workday_holiday_data["substitute_holiday"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 실무상 자주 틀리는 부분")
    st.markdown("<div class='warn-box'>", unsafe_allow_html=True)
    for item in workday_holiday_data["mistakes"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 자주 묻는 질문")
    for item in workday_holiday_data["faq"]:
        with st.expander(item["q"]):
            st.write(item["a"])

    

elif main_menu == "근무제도" and sub_menu == "근무시간과 휴게시간":
    st.markdown(f"## {worktime_break_data['title']}")

    st.markdown(
        f"<div class='point-box'><b>한줄 핵심</b><br>{worktime_break_data['one_line_summary']}</div>",
        unsafe_allow_html=True
    )

    st.markdown("### 기본원칙")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in worktime_break_data["basic_rules"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 근무형태별 근무시간과 휴게시간")
    selected_worktime_type = st.selectbox(
        "분야/근무형태를 선택하세요",
        [item["name"] for item in worktime_break_data["work_types"]],
        key="worktime_type"
    )
    selected_time_data = next(item for item in worktime_break_data["work_types"] if item["name"] == selected_worktime_type)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-title'>{selected_time_data['name']}</div>", unsafe_allow_html=True)
        st.write(f"**근무시간**: {selected_time_data['time']}")
        st.write(f"**휴게시간**: {selected_time_data['break']}")
        st.write(f"**실근무시간**: {selected_time_data['actual']}")
        st.write(f"**근무주기**: {selected_time_data['cycle']}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>실무 해석</div>", unsafe_allow_html=True)
        st.write("이 화면은 해당 분야의 기본 근무틀을 빠르게 확인하는 용도입니다.")
        st.write("실제 적용은 소속 분야, 근무표, 주기 운영기준까지 함께 확인해야 정확합니다.")
        st.write("특히 교대·교번·야간격일제는 달력보다 근무표가 더 중요합니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 근무일·근무형태·근무시간·휴게시간 변경")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in worktime_break_data["change_rules"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 탄력적 근로시간제")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in worktime_break_data["flex_rules"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 휴일대체 및 연장근로시 준수사항")
    st.markdown("<div class='warn-box'>", unsafe_allow_html=True)
    for item in worktime_break_data["overtime_notes"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 초과근무 제한 기준")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.table({
        "구분": [row[0] for row in worktime_break_data["restriction_table"]],
        "법정 기준근로시간": [row[1] for row in worktime_break_data["restriction_table"]],
        "연장근로": [row[2] for row in worktime_break_data["restriction_table"]],
        "야간근로": [row[3] for row in worktime_break_data["restriction_table"]],
        "휴일근로": [row[4] for row in worktime_break_data["restriction_table"]],
    })
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 자주 묻는 질문")
    for item in worktime_break_data["faq"]:
        with st.expander(item["q"]):
            st.write(item["a"])

    

elif main_menu == "근무제도" and sub_menu == "휴일대체근무제도":
    st.markdown(f"## {work_overtime_data['title']}")

    st.markdown(
        f"<div class='point-box'><b>한줄 핵심</b><br>{work_overtime_data['one_line_summary']}</div>",
        unsafe_allow_html=True
    )

    st.markdown("### 연장·야간근로 개요")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in work_overtime_data["overview"]:
        st.write(f"- {item}")
    st.markdown("#### 근무형태별 연장근무 기준")
    st.table({
        "근무형태": [row[0] for row in work_overtime_data["overtime_by_type"]],
        "연장근무 시간": [row[1] for row in work_overtime_data["overtime_by_type"]],
    })
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 연장근무 처리 기준")
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_overtime_data["overtime_rules"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("### 보상휴가Ⅱ 사용기준")
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_overtime_data["comp_leave"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 휴일근무 처리 기준")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in work_overtime_data["holiday_substitution"]:
        st.write(f"- {item}")
    st.markdown("#### 휴일대체 근무제도 사용기준")
    st.table({
        "구분": [row[0] for row in work_overtime_data["holiday_substitution_table"]],
        "사용 기준": [row[1] for row in work_overtime_data["holiday_substitution_table"]],
    })
    st.markdown("#### 대체휴일 사용방법")
    for item in work_overtime_data["holiday_use"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 통상근무자 초과근무 시 근태처리")
    tab1, tab2, tab3 = st.tabs(["기본원칙", "00시 이후 시작", "자정 걸침 처리"])

    with tab1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_overtime_data["attendance_processing"]["basic"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_overtime_data["attendance_processing"]["after_midnight_start"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("#### 익일이 근무일인 경우")
        st.table({
            "실 근로시간": [row[0] for row in work_overtime_data["attendance_processing"]["cross_midnight_workday"]],
            "근태 처리": [row[1] for row in work_overtime_data["attendance_processing"]["cross_midnight_workday"]],
        })
        st.markdown("#### 익일이 휴(무)일인 경우")
        st.table({
            "실 근로시간": [row[0] for row in work_overtime_data["attendance_processing"]["cross_midnight_holiday"]],
            "근태 처리": [row[1] for row in work_overtime_data["attendance_processing"]["cross_midnight_holiday"]],
        })

    st.markdown("### 자주 묻는 질문")
    for item in work_overtime_data["qa"]:
        with st.expander(item["q"]):
            st.write(item["a"])

    

elif main_menu == "근무제도" and sub_menu == "근무형태 변경시 처리":
    st.markdown(f"## {work_change_data['title']}")

    st.markdown(
        f"<div class='point-box'><b>한줄 핵심</b><br>{work_change_data['one_line_summary']}</div>",
        unsafe_allow_html=True
    )

    st.markdown("### 기본원칙")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in work_change_data["basic_rules"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 통상근무 ↔ 21주기 처리기준")
    st.table({
        "구분": [row[0] for row in work_change_data["case_21"]],
        "변경 전": [row[1] for row in work_change_data["case_21"]],
        "변경 당일": [row[2] for row in work_change_data["case_21"]],
        "적용": [row[3] for row in work_change_data["case_21"]]
    })

    st.markdown("### 통상근무 ↔ 6주기 처리기준")
    st.table({
        "구분": [row[0] for row in work_change_data["case_6"]],
        "변경 전": [row[1] for row in work_change_data["case_6"]],
        "변경 당일": [row[2] for row in work_change_data["case_6"]],
        "적용": [row[3] for row in work_change_data["case_6"]]
    })

    st.markdown("### 21주기 ↔ 6주기 처리기준")
    st.table({
        "구분": [row[0] for row in work_change_data["case_mix"]],
        "변경 전": [row[1] for row in work_change_data["case_mix"]],
        "변경 당일": [row[2] for row in work_change_data["case_mix"]],
        "적용": [row[3] for row in work_change_data["case_mix"]]
    })

    st.markdown("### 실무 참고")
    st.markdown("<div class='warn-box'>", unsafe_allow_html=True)
    for item in work_change_data["note"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    

elif main_menu == "근무제도" and sub_menu == "지정휴무":
    st.markdown(f"## {work_designated_off_data['title']}")

    st.markdown(
        f"<div class='point-box'><b>한줄 핵심</b><br>{work_designated_off_data['one_line_summary']}</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 개념")
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_designated_off_data["concept"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 부여 기준")
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        for item in work_designated_off_data["grant_rules"]:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 사용 기준")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    for item in work_designated_off_data["usage_rules"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 근무형태 변경 시 지정휴무 발생 기준")
    basis_tab1, basis_tab2, basis_tab3 = st.tabs(["21주기 기준", "현업일근 기준", "6주기 기준"])

    with basis_tab1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.table({
            "변경": [row[0] for row in work_designated_off_data["case_21"]],
            "조건": [row[1] for row in work_designated_off_data["case_21"]],
            "발생": [row[2] for row in work_designated_off_data["case_21"]]
        })
        st.markdown("</div>", unsafe_allow_html=True)

    with basis_tab2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.table({
            "변경": [row[0] for row in work_designated_off_data["case_field"]],
            "조건": [row[1] for row in work_designated_off_data["case_field"]],
            "발생": [row[2] for row in work_designated_off_data["case_field"]]
        })
        st.markdown("</div>", unsafe_allow_html=True)

    with basis_tab3:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.table({
            "변경": [row[0] for row in work_designated_off_data["case_6"]],
            "조건": [row[1] for row in work_designated_off_data["case_6"]],
            "발생": [row[2] for row in work_designated_off_data["case_6"]]
        })
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 지정휴무 자동 판단")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)

    auto_mode = st.radio(
        "입력 방식",
        ["선택형 입력", "문장형 입력"],
        horizontal=True,
        key="designated_input_mode"
    )

    if auto_mode == "선택형 입력":
        calc_case_type = st.selectbox(
            "기준 유형을 선택하세요",
            ["21주기 기준", "현업일근 기준", "6주기 기준", "분기연간 기준"],
            key="designated_case_type"
        )

        if calc_case_type == "21주기 기준":
            calc_prev_shift = st.selectbox(
                "변경 유형을 선택하세요",
                ["통상→21주기", "주간→야간", "야간→주간", "21주기주간→기타근무형태"],
                key="designated_prev_shift_21"
            )
            calc_next_shift = ""
            calc_changed_work_type = ""
            calc_remaining_days = None
            calc_prior_weekday_days = None

            if calc_prev_shift == "주간→야간":
                calc_data = calculate_designated_off("21주기 기준", remaining_days=st.number_input("변경 후 잔여 근무일수", min_value=0, max_value=31, value=4, step=1, key="designated_remaining_21_day_to_night"), prev_shift="주간", next_shift="야간")
            elif calc_prev_shift == "야간→주간":
                calc_data = calculate_designated_off("21주기 기준", remaining_days=st.number_input("변경 후 잔여 근무일수", min_value=0, max_value=31, value=3, step=1, key="designated_remaining_21_night_to_day"), prev_shift="야간", next_shift="주간")
            elif calc_prev_shift == "21주기주간→기타근무형태":
                calc_changed_work_type = st.selectbox("변경 후 근무형태", ["교대근무", "교번근무", "통상근무"], key="designated_changed_work_type_21_other")
                calc_prior_weekday_days = st.number_input("변경 전 주간 근무일수", min_value=0, max_value=7, value=4, step=1, key="designated_prior_weekday_days")
                calc_data = calculate_designated_off("21주기 기준", prev_shift="21주기주간→기타", prior_weekday_days=calc_prior_weekday_days, changed_work_type=calc_changed_work_type)
            else:
                calc_data = calculate_designated_off("21주기 기준", remaining_days=0, prev_shift="통상→21주기")

        elif calc_case_type == "현업일근 기준":
            calc_prev_shift = st.selectbox(
                "변경 유형을 선택하세요",
                ["현업일근→21주기(주간)", "현업일근→21주기(야간)", "21주기→현업일근"],
                key="designated_prev_shift_field"
            )
            if calc_prev_shift == "현업일근→21주기(주간)":
                calc_prior_used_days = st.number_input("변경 전 지정휴무 사용일수", min_value=0, max_value=2, value=1, step=1, key="designated_prior_used_days_field_day")
                calc_data = calculate_designated_off("현업일근 기준", remaining_days=0, prev_shift="현업일근→21주기", prior_used_days=calc_prior_used_days)
            elif calc_prev_shift == "현업일근→21주기(야간)":
                calc_remaining_days = st.number_input("변경 후 잔여 근무일수", min_value=0, max_value=31, value=4, step=1, key="designated_remaining_field_night")
                calc_data = calculate_designated_off("현업일근 기준", remaining_days=calc_remaining_days, prev_shift="현업일근→21주기")
            else:
                calc_remaining_days = st.number_input("변경 후 잔여 근무일수", min_value=0, max_value=31, value=5, step=1, key="designated_remaining_field_to_day")
                calc_data = calculate_designated_off("현업일근 기준", remaining_days=calc_remaining_days, prev_shift="21주기→현업일근")

        elif calc_case_type == "6주기 기준":
            calc_remaining_days = st.number_input(
                "근무지 배치일 또는 잔여일수",
                min_value=0,
                max_value=31,
                value=6,
                step=1,
                key="designated_remaining_6"
            )
            calc_data = calculate_designated_off("6주기 기준", remaining_days=calc_remaining_days, prev_shift="통상/21주기→6주기")

        else:
            calc_changed = st.selectbox("변경 유형", ["21주기↔교번"], key="designated_quarterly_change")
            calc_data = calculate_designated_off("분기연간 기준", changed_work_type=calc_changed)

    else:
        user_text = st.text_input(
            "문장으로 입력하세요",
            placeholder="예: 21주기 주간근무에서 교대근무로 바뀌고 변경 전 주간 근무일수는 4일이야",
            key="designated_free_text"
        )
        parsed = parse_designated_off_text(user_text)
        if parsed["case_type"]:
            calc_data = calculate_designated_off(
                parsed["case_type"],
                remaining_days=parsed["remaining_days"],
                prev_shift=parsed["prev_shift"],
                next_shift=parsed["next_shift"],
                prior_used_days=parsed["prior_used_days"],
                prior_weekday_days=parsed["prior_weekday_days"],
                changed_work_type=parsed["changed_work_type"],
            )
            st.caption(
                f"해석된 입력값: {parsed['case_type']} / {parsed['prev_shift']}"
                + (f" → {parsed['next_shift']}" if parsed["next_shift"] else "")
                + (f" / 변경 후 근무형태 {parsed['changed_work_type']}" if parsed["changed_work_type"] else "")
                + (f" / 잔여 근무일수 {parsed['remaining_days']}일" if parsed["remaining_days"] is not None else "")
                + (f" / 변경 전 주간 근무일수 {parsed['prior_weekday_days']}일" if parsed["prior_weekday_days"] is not None else "")
            )
        else:
            calc_data = {
                "result": "계산 대기",
                "reason": "문장에서 변경 유형 또는 기준 정보를 찾지 못했습니다.",
                "rule": "예시처럼 ‘21주기 주간근무에서 교대근무’, ‘주간 근무일수 4일’처럼 입력해 주세요."
            }

    st.success(f"자동 판단 결과: {calc_data['result']}")
    st.write(f"**판단 이유**: {calc_data['reason']}")
    st.write(f"**적용 근거**: {calc_data['rule']}")
    st.caption("이 계산기는 지정휴무 문서 표 기준으로 자동 판단합니다. 최종 적용 전 실제 근무표와 인사이동 기준을 함께 확인하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 실무 포인트")
    st.markdown("<div class='warn-box'>", unsafe_allow_html=True)
    for item in work_designated_off_data["note"]:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 빠른 판단 순서")
    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.write("1. 변경 전·후 근무형태를 먼저 확인합니다.")
    st.write("2. 잔여 근무일수를 확인합니다.")
    st.write("3. 21주기 / 현업일근 / 6주기 중 해당 표를 선택합니다.")
    st.write("4. 발생 여부를 확인한 뒤 실제 근무표와 인사이동 기준을 함께 검토합니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    

else:
    st.markdown("## 준비 중")
    st.write("현재는 근무제도 1-1 ~ 1-4까지 구현되었습니다.")
    st.write("다음 단계는 휴가제도(제4장)로 넘어가면 됩니다.")
