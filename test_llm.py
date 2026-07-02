from app.services.llm_service import analyze_text

text = """
검찰입니다.

귀하의 계좌가 범죄에 이용되었습니다.

즉시 아래 계좌로 송금하십시오.
"""

result = analyze_text(text)

print(result)