from __future__ import annotations

import asyncio
import csv
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
EVALUATION_DIR = ROOT / "evaluation"
QUESTIONS_PATH = EVALUATION_DIR / "questions.csv"
RESULTS_PATH = EVALUATION_DIR / "results.csv"
REPORT_PATH = EVALUATION_DIR / "evaluation_report.csv"
DETAILS_PATH = EVALUATION_DIR / "chunk_details.csv"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from app.tools.rag_tool import query_energy_documents
from judge import configure_evaluation_credentials, judge_answer


def _read_questions() -> list[str]:
    with QUESTIONS_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row["question"].strip() for row in reader if row.get("question", "").strip()]


def _write_results(rows: list[dict[str, Any]]) -> None:
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["question", "answer", "faithfulness", "relevance", "reason"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_report(rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    faithful = sum(1 for row in rows if row["faithfulness"] == "PASS")
    relevant = sum(1 for row in rows if row["relevance"] == "PASS")
    passed = sum(
        1
        for row in rows
        if row["faithfulness"] == "PASS" and row["relevance"] == "PASS"
    )
    failed = total - passed

    def pct(value: int) -> str:
        return f"{((value / total) * 100):.2f}%" if total else "0.00%"

    with REPORT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "total_questions",
                "passed_questions",
                "failed_questions",
                "faithfulness_passed",
                "faithfulness_failed",
                "faithfulness_score",
                "relevance_passed",
                "relevance_failed",
                "relevance_score",
                "overall_score",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "total_questions": total,
                "passed_questions": passed,
                "failed_questions": failed,
                "faithfulness_passed": faithful,
                "faithfulness_failed": total - faithful,
                "faithfulness_score": pct(faithful),
                "relevance_passed": relevant,
                "relevance_failed": total - relevant,
                "relevance_score": pct(relevant),
                "overall_score": pct(passed),
                "status": "PASS" if passed >= 7 else "FAIL",
            }
        )


def _format_chunk(chunk: dict[str, Any], index: int) -> dict[str, Any]:
    metadata = chunk.get("metadata") or {}
    return {
        "rank": index,
        "id": chunk.get("id"),
        "source": chunk.get("source"),
        "page": metadata.get("page"),
        "chunk": metadata.get("chunk"),
        "distance": chunk.get("distance"),
        "text": chunk.get("text", ""),
    }


def _chunks_json(chunks: list[dict[str, Any]]) -> str:
    formatted = [_format_chunk(chunk, index) for index, chunk in enumerate(chunks, start=1)]
    return json.dumps(formatted, ensure_ascii=False)


def _write_chunk_details(rows: list[dict[str, Any]]) -> None:
    with DETAILS_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "question",
                "faithfulness",
                "relevance",
                "top_3_chunks",
                "selected_chunks",
            ],
        )
        writer.writeheader()
        for row in rows:
            chunks = row.get("chunks", [])
            writer.writerow(
                {
                    "question": row["question"],
                    "faithfulness": row["faithfulness"],
                    "relevance": row["relevance"],
                    "top_3_chunks": _chunks_json(chunks[:3]),
                    "selected_chunks": _chunks_json(chunks),
                }
            )


async def _evaluate_question(question: str) -> dict[str, Any]:
    rag_result = await query_energy_documents(question)
    answer = rag_result.get("answer", "")
    chunks = rag_result.get("context", [])
    judgment = await judge_answer(question=question, answer=answer, chunks=chunks)
    return {
        "question": question,
        "answer": answer,
        "faithfulness": judgment["faithfulness"],
        "relevance": judgment["relevance"],
        "reason": judgment["reason"],
        "chunks": chunks,
    }


async def main() -> None:
    configure_evaluation_credentials()
    rows = []
    for index, question in enumerate(_read_questions(), start=1):
        print(f"Evaluating {index}: {question}")
        row = await _evaluate_question(question)
        rows.append(row)
        print(
            "  "
            f"Faithfulness: {row['faithfulness']} | "
            f"Relevance: {row['relevance']} | "
            f"{row['reason']}"
        )

    _write_results(rows)
    _write_report(rows)
    _write_chunk_details(rows)
    print(f"Wrote {RESULTS_PATH}")
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {DETAILS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
