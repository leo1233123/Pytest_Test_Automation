import os
import webbrowser
from datetime import datetime
from collections import defaultdict

REPORT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(REPORT_FOLDER, exist_ok=True)


# -----------------------------
# Helper
# -----------------------------
def pretty_format(data: dict, indent: int = 0) -> str:
    if not data:
        return "N/A"

    lines = []
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append("  " * indent + f"{k}:")
            lines.append(pretty_format(v, indent + 1))
        else:
            lines.append("  " * indent + f"{k}: {v}")
    return "\n".join(lines)


# -----------------------------
# Filename Generator
# -----------------------------
def get_next_filename():
    existing_files = [
        f for f in os.listdir(REPORT_FOLDER)
        if f.startswith("result") and f.endswith(".html")
    ]

    numbers = []
    for f in existing_files:
        try:
            numbers.append(int(f.replace("result", "").replace(".html", "")))
        except ValueError:
            pass

    next_number = max(numbers) + 1 if numbers else 1
    return f"result{next_number}.html"


# -----------------------------
# Generate HTML
# -----------------------------
def generate_html(results):

    grouped_results = defaultdict(list)
    for r in results:
        grouped_results[r["scenario"]].append(r)

    filename = get_next_filename()
    output_file = os.path.join(REPORT_FOLDER, filename)

    html = f"""
    <html>
    <head>
        <title>Test Report</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>

        /* ================= GLOBAL ================= */

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin:0;
            padding:0;
        }}

        /* ================= HEADER ================= */

        .header {{
            background: linear-gradient(135deg, #1e3a8a, #0f172a);
            color:white;
            padding:25px;
            text-align:center;
            font-size:18px;
            font-weight:600;
        }}

        /* ================= SUMMARY ================= */

        .summary {{
            padding:20px;
            display:flex;
            justify-content:space-evenly;
            flex-wrap:wrap;
            background-color:#e2e8f0;
            border-bottom:1px solid #cbd5e1;
        }}

        .summary div {{
            text-align:center;
            padding:12px 20px;
            border-radius:10px;
            font-weight:600;
            margin:6px;
            min-width:150px;
            box-shadow:0 2px 6px rgba(0,0,0,0.05);
        }}

        .summary .passed {{ background-color:#dcfce7; color:#166534; }}
        .summary .failed {{ background-color:#fee2e2; color:#991b1b; }}
        .summary .total {{ background-color:#e0f2fe; color:#0c4a6e; }}
        .summary .rate {{ background-color:#fef9c3; color:#854d0e; }}

        /* ================= TABLE ================= */

        table {{
            width:95%;
            margin:25px auto;
            border-collapse:collapse;
            table-layout:fixed;
            background:white;
            border-radius:12px;
            overflow:hidden;
            box-shadow:0 6px 20px rgba(0,0,0,0.05);
        }}

        col.col-assertion {{ width:18%; }}
        col.col-action {{ width:18%; }}
        col.col-status {{ width:10%; }}
        col.col-timestamp {{ width:14%; }}
        col.col-payload {{ width:20%; }}
        col.col-response {{ width:20%; }}

        th, td {{
            border:1px solid #e2e8f0;
            padding:12px;
            text-align:left;
            word-wrap:break-word;
            overflow-wrap:break-word;
        }}

        th {{
            background-color:#0f172a;
            color:white;
            font-size:13px;
            letter-spacing:0.5px;
            text-transform:uppercase;
            position:sticky;
            top:0;
        }}

        tr:hover {{
            background-color:#f1f5f9;
            transition:0.2s ease-in-out;
        }}

        tr.passed td {{ background-color:#f0fdf4; }}
        tr.failed td {{ background-color:#fef2f2; }}

        /* ================= STATUS BADGE ================= */

        .status-badge {{
            display:inline-block;
            padding:5px 12px;
            border-radius:20px;
            font-size:11px;
            font-weight:bold;
        }}

        .status-badge.passed {{
            background-color:#16a34a;
            color:white;
        }}

        .status-badge.failed {{
            background-color:#dc2626;
            color:white;
        }}

        /* ================= PRE BLOCK ================= */

        pre {{
            white-space:pre-wrap;
            word-wrap:break-word;
            background-color:#f1f5f9;
            padding:10px;
            border-radius:8px;
            font-size:12px;
            margin:0;
            max-height:250px;
            overflow-y:auto;
        }}

        /* ================= MOBILE ================= */

        @media screen and (max-width:768px) {{

            table, thead, tbody, th, td, tr {{
                display:block;
                width:100%;
            }}

            thead tr {{
                display:none;
            }}

            tr {{
                margin-bottom:15px;
                border-radius:12px;
                padding:12px;
                background:white;
                box-shadow:0 4px 12px rgba(0,0,0,0.05);
            }}

            td {{
                text-align:right;
                padding-left:50%;
                position:relative;
                border:none;
                border-bottom:1px solid #e2e8f0;
            }}

            td::before {{
                content: attr(data-label);
                position:absolute;
                left:15px;
                width:45%;
                font-weight:bold;
                text-align:left;
                color:#475569;
            }}
        }}

        </style>
    </head>
    <body>

        <div class="header">
            <h1>Test Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """

    # ================= TABLE PER SCENARIO =================

    for scenario, scenario_results in grouped_results.items():

        total = len(scenario_results)
        passed_count = sum(1 for r in scenario_results if r["passed"])
        failed_count = total - passed_count
        success_rate = f"{(passed_count/total*100):.2f}%" if total > 0 else "N/A"

        html += f"""
        <div class="summary">
            <div class="total">Total: {total}</div>
            <div class="passed">Passed: {passed_count}</div>
            <div class="failed">Failed: {failed_count}</div>
            <div class="rate">Success Rate: {success_rate}</div>
        </div>

        <h2 style="text-align:center;">Scenario: {scenario}</h2>

        <table>
            <colgroup>
                <col class="col-timestamp">
                <col class="col-assertion">
                <col class="col-action">
                <col class="col-status">
                <col class="col-payload">
                <col class="col-response">
            </colgroup>

            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Assertion / Step</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Payload</th>
                    <th>Response</th>
                </tr>
            </thead>

            <tbody>
        """

        for r in scenario_results:

            status_class = "passed" if r["passed"] else "failed"
            step_description = r.get("step_description", "")
            action = r.get("action", "N/A")
            timestamp = r.get("timestamp", "N/A")
            payload = pretty_format(r.get("payload")) if r.get("payload") else "N/A"
            response = pretty_format(r.get("response")) if r.get("response") else "N/A"

            html += f"""
            <tr class="{status_class}">
                <td data-label="Timestamp">{timestamp}</td>
                <td data-label="Assertion / Step">{step_description}</td>
                <td data-label="Action">{action}</td>
                <td data-label="Status">
                    <span class="status-badge {status_class}">
                        {'PASSED' if r['passed'] else 'FAILED'}
                    </span>
                </td>
                <td data-label="Payload"><pre>{payload}</pre></td>
                <td data-label="Response"><pre>{response}</pre></td>
            </tr>
            """

        html += """
            </tbody>
        </table>
        """

    html += """
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nResponsive HTML report generated: {output_file}")

    try:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        print("Report opened in browser.")
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")