import os
import json
import webbrowser
from datetime import datetime

REPORT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(REPORT_FOLDER, exist_ok=True)

# -----------------------------
# Helper: Pretty format payload
# -----------------------------
def pretty_format(data: dict, indent: int = 0) -> str:
    """Convert a dictionary to human-readable string for non-programmers."""
    lines = []
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append("  " * indent + f"{k}:")
            lines.append(pretty_format(v, indent + 1))
        else:
            lines.append("  " * indent + f"{k}: {v}")
    return "\n".join(lines)

# -----------------------------
# Generate HTML report
# -----------------------------
def get_next_filename():
    existing_files = [f for f in os.listdir(REPORT_FOLDER) if f.startswith("result") and f.endswith(".html")]
    numbers = []
    for f in existing_files:
        try:
            num = int(f.replace("result", "").replace(".html", ""))
            numbers.append(num)
        except ValueError:
            pass
    next_number = max(numbers) + 1 if numbers else 1
    return f"result{next_number}.html"

def generate_html(results):
    filename = get_next_filename()
    output_file = os.path.join(REPORT_FOLDER, filename)

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    success_rate = f"{(passed_count/total*100):.2f}%" if total > 0 else "N/A"

    html = f"""
    <html>
    <head>
        <title>Test Report</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; color: #333; margin:0; padding:0; }}
            .header {{ background-color: #2c3e50; color:#fff; padding:20px; text-align:center; }}
            .summary {{ padding:20px; display:flex; justify-content:space-around; flex-wrap:wrap; background-color:#ecf0f1; }}
            .summary div {{ text-align:center; padding:10px 20px; border-radius:5px; font-weight:bold; margin:5px; flex:1 1 150px; }}
            .summary .passed {{ background-color:#d4edda; color:#155724; }}
            .summary .failed {{ background-color:#f8d7da; color:#721c24; }}
            .summary .total {{ background-color:#d1ecf1; color:#0c5460; }}
            .summary .rate {{ background-color:#fff3cd; color:#856404; }}
            table {{ width:95%; margin:20px auto; border-collapse:collapse; box-shadow:0 2px 8px rgba(0,0,0,0.1); }}
            th, td {{ border:1px solid #ddd; padding:12px; text-align:left; }}
            th {{ background-color:#2c3e50; color:white; text-transform:uppercase; }}
            tr:hover {{ background-color:#f1f1f1; }}
            .passed {{ background-color:#d4edda; }}
            .failed {{ background-color:#f8d7da; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; background-color:#f4f4f4; padding:8px; border-radius:4px; }}
            @media screen and (max-width:768px) {{
                table, thead, tbody, th, td, tr {{ display:block; width:100%; }}
                thead tr {{ display:none; }}
                tr {{ margin-bottom:15px; border:1px solid #ccc; border-radius:5px; padding:10px; }}
                td {{ text-align:right; padding-left:50%; position:relative; }}
                td::before {{ content: attr(data-label); position:absolute; left:15px; width:45%; padding-right:10px; font-weight:bold; text-align:left; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Test Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="summary">
            <div class="total">Total: {total}</div>
            <div class="passed">Passed: {passed_count}</div>
            <div class="failed">Failed: {failed_count}</div>
            <div class="rate">Success Rate: {success_rate}</div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Scenario</th>
                    <th>Assertion / Step</th>
                    <th>Status</th>
                    <th>Payload / Response</th>
                </tr>
            </thead>
            <tbody>
    """

    for r in results:
        status_class = "passed" if r["passed"] else "failed"
        step_description = r.get("step_description", r.get("step", ""))
        data = r.get("data", {})
        payload_or_response = pretty_format(data) if data else "N/A"
        html += f"""
            <tr class="{status_class}">
                <td data-label="Scenario">{r['scenario']}</td>
                <td data-label="Assertion / Step">{step_description}</td>
                <td data-label="Status">{'PASSED' if r['passed'] else 'FAILED'}</td>
                <td data-label="Payload / Response"><pre>{payload_or_response}</pre></td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nResponsive HTML report generated: {output_file}")

    # -----------------------------
    # Auto open in browser
    # -----------------------------
    try:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        print("Report opened in the default web browser.")
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")
