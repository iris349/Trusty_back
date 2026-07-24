import csv
import json
import time
from pathlib import Path

from app.services.llm_service import analyze_text


TEST_FILE = Path("data/test_data.csv")
RESULT_FILE = Path("data/test_results.json")


def run_test():
    total = 0
    risk_correct = 0
    scam_type_correct = 0
    results = []

    with TEST_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            input_text = row["input_text"].strip()
            expected_risk = row["expected_risk_level"].strip()
            expected_type = row["expected_scam_type"].strip()

            try:
                result = analyze_text(input_text)

                predicted_risk = result["risk_level"]
                predicted_type = result["scam_type"]

                risk_match = predicted_risk == expected_risk
                type_match = predicted_type == expected_type

                total += 1

                if risk_match:
                    risk_correct += 1

                if type_match:
                    scam_type_correct += 1

                test_result = {
                    "id": row.get("id"),
                    "input_text": input_text,
                    "expected_risk_level": expected_risk,
                    "predicted_risk_level": predicted_risk,
                    "risk_correct": risk_match,
                    "expected_scam_type": expected_type,
                    "predicted_scam_type": predicted_type,
                    "scam_type_correct": type_match,
                    "score": result.get("score"),
                    "reason": result.get("reason")
                }

                results.append(test_result)

                print(
                    f"[{total}] "
                    f"risk: {expected_risk} → {predicted_risk} "
                    f"{'✅' if risk_match else '❌'} | "
                    f"type: {expected_type} → {predicted_type} "
                    f"{'✅' if type_match else '❌'}"
                )

                # API 요청 제한 완화
                time.sleep(1)

            except Exception as error:
                total += 1

                results.append({
                    "id": row.get("id"),
                    "input_text": input_text,
                    "error": str(error)
                })

                print(f"[{total}] 분석 실패: {error}")

    risk_accuracy = risk_correct / total if total else 0
    type_accuracy = scam_type_correct / total if total else 0

    summary = {
        "total": total,
        "risk_correct": risk_correct,
        "risk_accuracy": risk_accuracy,
        "scam_type_correct": scam_type_correct,
        "scam_type_accuracy": type_accuracy,
        "results": results
    }

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n==============================")
    print(f"전체 문장 수: {total}")
    print(f"위험도 정확도: {risk_accuracy:.2%}")
    print(f"사기 유형 정확도: {type_accuracy:.2%}")
    print(f"결과 저장: {RESULT_FILE}")


if __name__ == "__main__":
    run_test()