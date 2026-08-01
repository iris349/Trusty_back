import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any

from app.services.llm_service import analyze_text


# =========================================================
# 파일 경로 설정
# =========================================================

TEST_DATA_PATH = Path("data/test_data.csv")
RESULT_PATH = Path("data/test_results.json")


# =========================================================
# 기본 설정
# =========================================================

DEFAULT_DELAY_SECONDS = 15
MAX_CONSECUTIVE_FAILURES = 3


def parse_arguments() -> argparse.Namespace:
    """
    터미널에서 입력받을 실행 옵션을 설정합니다.
    """

    parser = argparse.ArgumentParser(
        description="Trusty LLM 피싱 탐지 성능 테스트"
    )

    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="테스트를 시작할 데이터 번호",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="테스트를 종료할 데이터 번호",
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=DEFAULT_DELAY_SECONDS,
        help="각 API 요청 사이의 대기 시간(초)",
    )

    parser.add_argument(
        "--failed-only",
        action="store_true",
        help="이전에 실패한 데이터만 다시 실행",
    )

    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help='특정 ID만 실행. 예: --ids "19,25,26"',
    )

    parser.add_argument(
        "--rerun-all",
        action="store_true",
        help="이전 성공 여부와 상관없이 선택 범위를 모두 다시 실행",
    )

    return parser.parse_args()


def load_test_data() -> list[dict[str, str]]:
    """
    CSV 테스트 데이터를 읽습니다.
    """

    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(
            f"테스트 파일을 찾을 수 없습니다: {TEST_DATA_PATH}"
        )

    with TEST_DATA_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    required_columns = {
        "id",
        "input_text",
        "expected_risk_level",
        "expected_scam_type",
    }

    if not rows:
        raise ValueError("테스트 CSV에 데이터가 없습니다.")

    actual_columns = set(rows[0].keys())
    missing_columns = required_columns - actual_columns

    if missing_columns:
        raise ValueError(
            "테스트 CSV에 필요한 열이 없습니다: "
            + ", ".join(sorted(missing_columns))
        )

    return rows


def empty_result_file() -> dict[str, Any]:
    """
    새로운 결과 파일의 기본 구조입니다.
    """

    return {
        "summary": {},
        "results": [],
    }


def load_previous_results() -> dict[str, Any]:
    """
    기존 test_results.json 결과를 읽습니다.

    파일이 없거나 형식에 문제가 있으면 빈 결과를 반환합니다.
    """

    if not RESULT_PATH.exists():
        return empty_result_file()

    try:
        with RESULT_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return empty_result_file()

        if "results" not in data or not isinstance(data["results"], list):
            return empty_result_file()

        return data

    except (json.JSONDecodeError, OSError):
        print("기존 결과 파일을 읽지 못해 새 결과로 시작합니다.")
        return empty_result_file()


def normalize_id(value: Any) -> str:
    """
    ID를 비교하기 쉽도록 문자열로 통일합니다.
    """

    return str(value).strip()


def make_result_map(
    previous_results: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """
    기존 결과 목록을 ID를 키로 하는 딕셔너리로 변환합니다.
    """

    result_map: dict[str, dict[str, Any]] = {}

    for result in previous_results.get("results", []):
        result_id = normalize_id(result.get("id", ""))

        if result_id:
            result_map[result_id] = result

    return result_map


def parse_selected_ids(ids_argument: str | None) -> set[str] | None:
    """
    --ids "19,25,26" 형식의 값을 집합으로 변환합니다.
    """

    if not ids_argument:
        return None

    selected_ids = {
        normalize_id(value)
        for value in ids_argument.split(",")
        if value.strip()
    }

    return selected_ids


def should_run_row(
    row: dict[str, str],
    row_number: int,
    args: argparse.Namespace,
    selected_ids: set[str] | None,
    previous_result: dict[str, Any] | None,
) -> bool:
    """
    현재 데이터를 실행해야 하는지 판단합니다.
    """

    row_id = normalize_id(row["id"])

    # 특정 ID를 지정한 경우
    if selected_ids is not None and row_id not in selected_ids:
        return False

    # 시작 번호보다 앞이면 제외
    if args.start is not None and row_number < args.start:
        return False

    # 종료 번호보다 뒤면 제외
    if args.end is not None and row_number > args.end:
        return False

    # 실패한 데이터만 재실행
    if args.failed_only:
        if previous_result is None:
            return True

        return previous_result.get("status") != "success"

    # 전체 재실행 옵션
    if args.rerun_all:
        return True

    # 기본 동작:
    # 이전에 성공한 항목은 건너뛰고,
    # 이전 결과가 없거나 실패한 항목만 실행
    if previous_result is not None:
        if previous_result.get("status") == "success":
            return False

    return True


def create_success_result(
    row: dict[str, str],
    prediction: dict[str, Any],
) -> dict[str, Any]:
    """
    성공한 분석 결과를 저장할 형식으로 만듭니다.
    """

    expected_risk = row["expected_risk_level"].strip()
    expected_type = row["expected_scam_type"].strip()

    predicted_risk = str(
        prediction.get("risk_level", "")
    ).strip()

    predicted_type = str(
        prediction.get("scam_type", "")
    ).strip()

    risk_correct = predicted_risk == expected_risk
    type_correct = predicted_type == expected_type

    return {
        "id": normalize_id(row["id"]),
        "input_text": row["input_text"],
        "expected_risk_level": expected_risk,
        "predicted_risk_level": predicted_risk,
        "expected_scam_type": expected_type,
        "predicted_scam_type": predicted_type,
        "risk_correct": risk_correct,
        "type_correct": type_correct,
        "all_correct": risk_correct and type_correct,
        "status": "success",
        "error": None,
        "analysis": prediction,
    }


def create_failure_result(
    row: dict[str, str],
    error: Exception,
) -> dict[str, Any]:
    """
    분석 실패 결과를 저장할 형식으로 만듭니다.
    """

    return {
        "id": normalize_id(row["id"]),
        "input_text": row["input_text"],
        "expected_risk_level": row[
            "expected_risk_level"
        ].strip(),
        "predicted_risk_level": None,
        "expected_scam_type": row[
            "expected_scam_type"
        ].strip(),
        "predicted_scam_type": None,
        "risk_correct": False,
        "type_correct": False,
        "all_correct": False,
        "status": "failed",
        "error": str(error),
        "analysis": None,
    }


def calculate_summary(
    test_rows: list[dict[str, str]],
    result_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    전체 테스트 결과 통계를 계산합니다.
    """

    total_count = len(test_rows)

    valid_results = []

    for row in test_rows:
        row_id = normalize_id(row["id"])
        result = result_map.get(row_id)

        if result is not None:
            valid_results.append(result)

    success_results = [
        result
        for result in valid_results
        if result.get("status") == "success"
    ]

    failed_results = [
        result
        for result in valid_results
        if result.get("status") == "failed"
    ]

    success_count = len(success_results)
    failure_count = len(failed_results)
    not_tested_count = total_count - len(valid_results)

    risk_correct_count = sum(
        1
        for result in success_results
        if result.get("risk_correct") is True
    )

    type_correct_count = sum(
        1
        for result in success_results
        if result.get("type_correct") is True
    )

    all_correct_count = sum(
        1
        for result in success_results
        if result.get("all_correct") is True
    )

    if success_count > 0:
        risk_accuracy = round(
            risk_correct_count / success_count * 100,
            2,
        )

        type_accuracy = round(
            type_correct_count / success_count * 100,
            2,
        )

        complete_accuracy = round(
            all_correct_count / success_count * 100,
            2,
        )

    else:
        risk_accuracy = 0.0
        type_accuracy = 0.0
        complete_accuracy = 0.0

    if total_count > 0:
        progress_rate = round(
            success_count / total_count * 100,
            2,
        )
    else:
        progress_rate = 0.0

    return {
        "total_count": total_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "not_tested_count": not_tested_count,
        "risk_correct_count": risk_correct_count,
        "type_correct_count": type_correct_count,
        "all_correct_count": all_correct_count,
        "risk_accuracy": risk_accuracy,
        "type_accuracy": type_accuracy,
        "complete_accuracy": complete_accuracy,
        "progress_rate": progress_rate,
    }


def sort_result_key(result: dict[str, Any]) -> tuple[int, str]:
    """
    결과를 ID 순서대로 정렬합니다.
    숫자 ID가 아닌 경우도 처리합니다.
    """

    result_id = normalize_id(result.get("id", ""))

    try:
        return 0, f"{int(result_id):010d}"
    except ValueError:
        return 1, result_id


def save_results(
    test_rows: list[dict[str, str]],
    result_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    현재까지의 결과를 JSON 파일에 저장합니다.
    """

    RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sorted_results = sorted(
        result_map.values(),
        key=sort_result_key,
    )

    summary = calculate_summary(
        test_rows=test_rows,
        result_map=result_map,
    )

    output = {
        "summary": summary,
        "results": sorted_results,
    }

    with RESULT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return summary


def print_summary(summary: dict[str, Any]) -> None:
    """
    최종 통계를 터미널에 출력합니다.
    """

    print()
    print("=" * 50)
    print(f"전체 문장 수: {summary['total_count']}")
    print(f"분석 성공: {summary['success_count']}")
    print(f"분석 실패: {summary['failure_count']}")
    print(f"아직 실행하지 않음: {summary['not_tested_count']}")
    print(
        f"전체 테스트 진행률: "
        f"{summary['progress_rate']:.2f}%"
    )
    print()
    print(
        f"위험도 정확도: "
        f"{summary['risk_accuracy']:.2f}%"
    )
    print(
        f"사기 유형 정확도: "
        f"{summary['type_accuracy']:.2f}%"
    )
    print(
        f"위험도와 유형 모두 정답: "
        f"{summary['complete_accuracy']:.2f}%"
    )
    print(f"결과 저장: {RESULT_PATH}")
    print("=" * 50)


def main() -> None:
    args = parse_arguments()

    if args.delay < 0:
        raise ValueError("--delay 값은 0 이상이어야 합니다.")

    if (
        args.start is not None
        and args.end is not None
        and args.start > args.end
    ):
        raise ValueError(
            "--start 값은 --end 값보다 클 수 없습니다."
        )

    test_rows = load_test_data()
    previous_data = load_previous_results()
    result_map = make_result_map(previous_data)
    selected_ids = parse_selected_ids(args.ids)

    rows_to_run: list[tuple[int, dict[str, str]]] = []

    for row_number, row in enumerate(
        test_rows,
        start=1,
    ):
        row_id = normalize_id(row["id"])
        previous_result = result_map.get(row_id)

        if should_run_row(
            row=row,
            row_number=row_number,
            args=args,
            selected_ids=selected_ids,
            previous_result=previous_result,
        ):
            rows_to_run.append((row_number, row))

    print("=" * 50)
    print("Trusty LLM 테스트 시작")
    print(f"전체 CSV 데이터: {len(test_rows)}개")
    print(f"이번 실행 대상: {len(rows_to_run)}개")
    print(f"요청 간격: {args.delay}초")
    print("=" * 50)

    if not rows_to_run:
        print("이번에 실행할 데이터가 없습니다.")

        summary = save_results(
            test_rows=test_rows,
            result_map=result_map,
        )

        print_summary(summary)
        return

    consecutive_failures = 0

    try:
        for execution_index, (
            row_number,
            row,
        ) in enumerate(rows_to_run, start=1):

            row_id = normalize_id(row["id"])
            input_text = row["input_text"].strip()

            expected_risk = row[
                "expected_risk_level"
            ].strip()

            expected_type = row[
                "expected_scam_type"
            ].strip()

            print()
            print(
                f"[CSV {row_number}번 / ID {row_id}] "
                f"분석 중..."
            )

            try:
                prediction = analyze_text(input_text)

                if not isinstance(prediction, dict):
                    raise TypeError(
                        "analyze_text() 결과가 "
                        "딕셔너리가 아닙니다."
                    )

                result = create_success_result(
                    row=row,
                    prediction=prediction,
                )

                result_map[row_id] = result
                consecutive_failures = 0

                predicted_risk = result[
                    "predicted_risk_level"
                ]

                predicted_type = result[
                    "predicted_scam_type"
                ]

                risk_mark = (
                    "✅"
                    if result["risk_correct"]
                    else "❌"
                )

                type_mark = (
                    "✅"
                    if result["type_correct"]
                    else "❌"
                )

                print(
                    f"risk: {expected_risk} "
                    f"→ {predicted_risk} {risk_mark}"
                )

                print(
                    f"type: {expected_type} "
                    f"→ {predicted_type} {type_mark}"
                )

            except Exception as error:
                result = create_failure_result(
                    row=row,
                    error=error,
                )

                result_map[row_id] = result
                consecutive_failures += 1

                print(
                    f"분석 실패: {error}"
                )

            # 매 요청이 끝날 때마다 즉시 저장
            save_results(
                test_rows=test_rows,
                result_map=result_map,
            )

            if (
                consecutive_failures
                >= MAX_CONSECUTIVE_FAILURES
            ):
                print()
                print(
                    f"연속 {MAX_CONSECUTIVE_FAILURES}회 "
                    "분석에 실패했습니다."
                )
                print(
                    "API 할당량이 소진됐을 가능성이 있어 "
                    "테스트를 자동으로 중단합니다."
                )
                print(
                    "나중에 --failed-only 옵션으로 "
                    "실패한 항목만 다시 실행하세요."
                )
                break

            is_last_request = (
                execution_index == len(rows_to_run)
            )

            if not is_last_request and args.delay > 0:
                print(
                    f"다음 요청까지 "
                    f"{args.delay}초 대기..."
                )
                time.sleep(args.delay)

    except KeyboardInterrupt:
        print()
        print("사용자가 테스트를 중단했습니다.")
        print("현재까지의 결과는 저장되었습니다.")

    finally:
        summary = save_results(
            test_rows=test_rows,
            result_map=result_map,
        )

        print_summary(summary)


if __name__ == "__main__":
    main()