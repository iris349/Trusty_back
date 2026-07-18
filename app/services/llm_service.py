import json

from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def analyze_text(text: str):

    prompt = f"""
당신은 보이스피싱 탐지 AI입니다.

아래 문장을 분석하세요.

문장:
{text}

반드시 아래 JSON 형식으로만 응답하세요.

{{
    "risk_level":"HIGH | MEDIUM | LOW",
    "score":95,
    "scam_type":"기관사칭",
    "reason":"판단 이유",

    "url_risk_score":85,
    "language_pattern_score":90,
    "sender_reliability_score":30,
    "urgency_score":95,

    "recommended_actions":[
        "링크를 클릭하지 마세요",
        "송금하지 마세요",
        "경찰청 또는 금융감독원에 신고하세요"
    ]
}}

설명은 절대 쓰지 말고 JSON만 출력하세요.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if response.text is None:
        raise Exception("Gemini 응답이 비어 있습니다.")

    response_text = response.text.strip()

    # 코드블록 제거
    response_text = (
        response_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        result = json.loads(response_text)
    except Exception:
        print(response_text)
        raise Exception("Gemini가 JSON 형식으로 응답하지 않았습니다.")

    return result