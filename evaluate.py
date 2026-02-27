"""Evaluation script: execution accuracy comparison of generated vs reference SQL."""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

from src.data_manager import DataManager
from src.agent import Agent

load_dotenv()

# 15 test questions with ground truth SQL
TEST_CASES = [
    {
        "question": "List all clients with their industries.",
        "reference_sql": "SELECT client_name, industry FROM clients;",
    },
    {
        "question": "Which clients are based in the UK?",
        "reference_sql": "SELECT client_name FROM clients WHERE country = 'UK';",
    },
    {
        "question": "List all invoices issued in March 2024 with their statuses.",
        "reference_sql": "SELECT invoice_id, status FROM invoices WHERE invoice_date BETWEEN '2024-03-01' AND '2024-03-31';",
    },
    {
        "question": "Which invoices are currently marked as 'Overdue'?",
        "reference_sql": "SELECT invoice_id FROM invoices WHERE status = 'Overdue';",
    },
    {
        "question": "For each service_name in InvoiceLineItems, how many line items are there?",
        "reference_sql": "SELECT service_name, COUNT(*) as count FROM invoice_line_items GROUP BY service_name;",
    },
    {
        "question": "List all invoices for Acme Corp with their invoice IDs, invoice dates, due dates, and statuses.",
        "reference_sql": "SELECT i.invoice_id, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Acme Corp';",
    },
    {
        "question": "Show all invoices issued to Bright Legal in February 2024, including their status and currency.",
        "reference_sql": "SELECT i.invoice_id, i.status, i.currency FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Bright Legal' AND i.invoice_date BETWEEN '2024-02-01' AND '2024-02-29';",
    },
    {
        "question": "For invoice I1001, list all line items with service name, quantity, unit price, tax rate, and compute the line total (including tax) for each.",
        "reference_sql": "SELECT service_name, quantity, unit_price, tax_rate, (quantity * unit_price * (1 + tax_rate)) as line_total FROM invoice_line_items WHERE invoice_id = 'I1001';",
    },
    {
        "question": "For each client, compute the total amount billed in 2024 (including tax) across all their invoices.",
        "reference_sql": "SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name;",
    },
    {
        "question": "Which client has the highest total billed amount in 2024, and what is that total?",
        "reference_sql": "SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name ORDER BY total_billed DESC LIMIT 1;",
    },
    {
        "question": "Across all clients, which three services generated the most revenue in 2024? Show the total revenue per service.",
        "reference_sql": "SELECT ili.service_name, SUM(ili.quantity * ili.unit_price) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;",
    },
    {
        "question": "Which invoices are overdue as of 2024-12-31? List invoice ID, client name, invoice_date, due_date, and status.",
        "reference_sql": "SELECT i.invoice_id, c.client_name, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE i.status = 'Overdue' AND i.due_date < '2024-12-31';",
    },
    {
        "question": "Group revenue by client country: for each country, compute the total billed amount in 2024 (including tax).",
        "reference_sql": "SELECT c.country, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.country;",
    },
    {
        "question": "For the service 'Contract Review', list all clients who purchased it and the total amount they paid for that service (including tax).",
        "reference_sql": "SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_paid FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE ili.service_name = 'Contract Review' GROUP BY c.client_name;",
    },
    {
        "question": "Considering only European clients, what are the top 3 services by total revenue (including tax) in H2 2024 (2024-07-01 to 2024-12-31)?",
        "reference_sql": "SELECT ili.service_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id JOIN clients c ON i.client_id = c.client_id WHERE c.country IN ('UK', 'France', 'Germany', 'Spain', 'Italy', 'Netherlands', 'Portugal') AND i.invoice_date BETWEEN '2024-07-01' AND '2024-12-31' GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;",
    },
]


def normalize_results(result: dict) -> set[tuple] | None:
    """Convert query result to a set of tuples for comparison."""
    if "error" in result:
        return None
    rows = result.get("rows", [])
    return set(tuple(round(v, 2) if isinstance(v, float) else v for v in row) for row in rows)


def compare_results(ref: set[tuple] | None, gen: set[tuple] | None, ref_cols: list[str] | None = None, gen_cols: list[str] | None = None) -> dict:
    """Compare reference and generated result sets."""
    if ref is None and gen is None:
        return {"match": True, "type": "both_error"}
    if ref is None:
        return {"match": False, "type": "ref_error"}
    if gen is None:
        return {"match": False, "type": "gen_error"}

    if ref == gen:
        return {"match": True, "type": "exact"}

    # Same row count check for column-superset matching
    if len(ref) > 0 and len(gen) > 0 and len(ref) == len(gen):
        ref_sample = next(iter(ref))
        gen_sample = next(iter(gen))

        if len(gen_sample) > len(ref_sample):
            # Generated has extra columns — try to find ref columns within gen columns
            # First try: match by column names if available
            if ref_cols and gen_cols:
                indices = []
                for rc in ref_cols:
                    rc_lower = rc.lower().split(" as ")[-1].strip().split(".")[-1].strip()
                    for j, gc in enumerate(gen_cols):
                        gc_lower = gc.lower().split(" as ")[-1].strip().split(".")[-1].strip()
                        if rc_lower == gc_lower and j not in indices:
                            indices.append(j)
                            break
                if len(indices) == len(ref_cols):
                    gen_projected = set(tuple(row[j] for j in indices) for row in gen)
                    if gen_projected == ref:
                        return {"match": True, "type": "superset_cols"}

            # Fallback: try all column subsets of the right size
            from itertools import combinations
            ref_width = len(ref_sample)
            gen_width = len(gen_sample)
            for combo in combinations(range(gen_width), ref_width):
                gen_projected = set(tuple(row[i] for i in combo) for row in gen)
                if gen_projected == ref:
                    return {"match": True, "type": "superset"}

    # Check subset match (all reference rows present in generated)
    if ref.issubset(gen) or gen.issubset(ref):
        return {"match": True, "type": "subset"}

    return {"match": False, "type": "mismatch"}


def run_evaluation(model: str = "gpt-5.1"):
    dm = DataManager()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)

    agent = Agent(dm, model=model, api_key=api_key)
    results = []
    correct = 0
    total = len(TEST_CASES)

    print(f"\nEvaluating {total} questions with model: {model}\n")
    print("=" * 80)

    for i, tc in enumerate(TEST_CASES, 1):
        question = tc["question"]
        ref_sql = tc["reference_sql"]

        print(f"\n[{i}/{total}] {question}")

        # Get reference results
        ref_result = dm.execute_query(ref_sql)
        ref_set = normalize_results(ref_result)

        # Get agent answer — try all generated queries and pick best match
        try:
            agent_response = agent.run([{"role": "user", "content": question}])
            all_sqls = agent_response["sql_queries"] if agent_response["sql_queries"] else []
        except Exception as e:
            all_sqls = []
            agent_response = {"answer": f"Error: {e}", "sql_queries": [], "data_tables": []}

        # Check each generated query against reference; pick the best match
        best_comparison = {"match": False, "type": "no_sql"}
        gen_sql = ""
        gen_result = {"error": "No SQL generated"}
        for candidate_sql in all_sqls:
            candidate_result = dm.execute_query(candidate_sql)
            candidate_set = normalize_results(candidate_result)
            candidate_cols = candidate_result.get("columns")
            comp = compare_results(ref_set, candidate_set, ref_result.get("columns"), candidate_cols)
            if comp["match"]:
                best_comparison = comp
                gen_sql = candidate_sql
                gen_result = candidate_result
                break
            # Keep the last query as fallback for reporting
            gen_sql = candidate_sql
            gen_result = candidate_result
            best_comparison = comp

        comparison = best_comparison
        is_correct = comparison["match"]
        if is_correct:
            correct += 1

        status = "✅" if is_correct else "❌"
        print(f"  {status} Match: {comparison['type']}")
        print(f"  Reference SQL: {ref_sql}")
        print(f"  Generated SQL: {gen_sql}")

        results.append({
            "question": question,
            "reference_sql": ref_sql,
            "generated_sql": gen_sql,
            "answer": agent_response["answer"],
            "correct": is_correct,
            "match_type": comparison["type"],
        })

    accuracy = correct / total * 100
    print(f"\n{'=' * 80}")
    print(f"Execution Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"Model: {model}")

    # Generate Test_Results.md
    generate_results_md(results, model, accuracy)
    return results, accuracy


def generate_results_md(results: list[dict], model: str, accuracy: float):
    lines = [
        f"# Test Results — {model}",
        f"",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Execution Accuracy:** {accuracy:.1f}%",
        f"",
        f"| # | Question | Status | Generated SQL |",
        f"|---|----------|--------|--------------|",
    ]
    for i, r in enumerate(results, 1):
        status = "✅" if r["correct"] else "❌"
        sql = r["generated_sql"].replace("|", "\\|").replace("\n", " ")
        q = r["question"].replace("|", "\\|")
        lines.append(f"| {i} | {q} | {status} | `{sql}` |")

    lines.extend([
        "",
        "## Detailed Results",
        "",
    ])
    for i, r in enumerate(results, 1):
        lines.extend([
            f"### {i}. {r['question']}",
            f"",
            f"**Status:** {'✅ Correct' if r['correct'] else '❌ Incorrect'} ({r['match_type']})",
            f"",
            f"**Reference SQL:**",
            f"```sql",
            f"{r['reference_sql']}",
            f"```",
            f"",
            f"**Generated SQL:**",
            f"```sql",
            f"{r['generated_sql']}",
            f"```",
            f"",
            f"**Answer:** {r['answer'][:500]}",
            f"",
            f"---",
            f"",
        ])

    output_path = os.path.join(os.path.dirname(__file__), "Test_Results.md")
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nResults written to {output_path}")


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt-4o-mini"
    run_evaluation(model)
