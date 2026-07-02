import json
import re

from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


SYSTEM_PROMPT = """
당신은 대한민국 보이스피싱 분석 전문가입니다.

사용자가 입력한 문자나 메일 내용을 분석하세요.

다음 기준을 종합적으로 판단하세요.

1. 정부기관 사칭
2. 금융기관 사칭
3. 긴급성 표현
4. 송금 요구
5. 개인정보 요구
6. URL 포함 여부
7. 앱 설치 유도
8. 협박 표현
9. 투자 및 대출 사기 여부

반드시 아래 JSON 형식으로만 응답하세요.

{
  "risk_level":"HIGH",
  "score":95,
  "scam_type":"기관사칭",
  "reason":"정부기관을 사칭하며 긴급한 송금을 요구합니다."
}

절대로 코드블록(```)이나 설명을 추가하지 마세요.
"""


def analyze_text(text: str):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
{SYSTEM_PROMPT}

분석할 문장:

{text}
"""
    )

    result = response.text.strip()

    # 혹시 ```json ... ``` 형태로 오면 제거
    result = re.sub(r"```json|```", "", result).strip()

    return json.loads(result)