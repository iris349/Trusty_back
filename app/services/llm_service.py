import json

# 나중에 Gemini 사용할 때 다시 주석 해제
# from google import genai
# from app.core.config import settings

# client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_text(text: str):

    phishing_keywords = [
        "계좌", "송금", "긴급", "검찰", "경찰", "금감원",
        "인증", "링크", "당첨", "택배", "환급"
    ]

    if any(keyword in text for keyword in phishing_keywords):
        return {
            "risk_level": "HIGH",
            "score": 92,
            "scam_type": "기관사칭",
            "reason": "피싱에서 자주 사용하는 키워드가 포함되어 있습니다.",

            "url_risk_score": 80,
            "language_pattern_score": 90,
            "sender_reliability_score": 20,
            "urgency_score": 95,

            "recommended_actions": [
                "링크를 클릭하지 마세요.",
                "송금하지 마세요.",
                "경찰청 또는 금융감독원에 신고하세요."
            ]
        }

    return {
        "risk_level": "LOW",
        "score": 15,
        "scam_type": "정상",
        "reason": "위험한 표현이 발견되지 않았습니다.",

        "url_risk_score": 0,
        "language_pattern_score": 10,
        "sender_reliability_score": 90,
        "urgency_score": 5,

        "recommended_actions": [
            "현재 특별한 위험 요소는 발견되지 않았습니다."
        ]
    }