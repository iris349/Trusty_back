from app.services.llm_service import analyze_text


def main():
    test_messages = [
        "오늘 저녁 7시에 역 앞에서 만나자.",
        "검찰청입니다. 귀하의 계좌가 범죄에 연루되었습니다. 안전계좌로 송금하세요.",
        "택배 주소가 잘못되었습니다. 아래 링크에서 주소를 수정하세요.",
        "엄마 나 휴대폰이 고장 나서 친구 번호로 연락해. 급하게 돈 좀 보내줘.",
    ]

    for index, message in enumerate(test_messages, start=1):
        print("\n" + "=" * 70)
        print(f"[테스트 {index}]")
        print(f"입력 문장: {message}")
        print("-" * 70)

        try:
            result = analyze_text(message)

            print("분석 결과:")
            print(result)

        except Exception as error:
            print("분석 중 오류가 발생했습니다.")
            print(f"오류 내용: {error}")

    print("\n" + "=" * 70)
    print("모든 테스트가 완료되었습니다.")


if __name__ == "__main__":
    main()