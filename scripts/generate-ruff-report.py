import html
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python generate-ruff-report.py "
            "<input-json> <output-html>"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    with input_file.open(encoding="utf-8") as file:
        findings = json.load(file)

    violations = len(findings)

    status = "PASS" if violations == 0 else "FAIL"

    rows = []

    for finding in findings:
        filename = html.escape(finding.get("filename", ""))
        code = html.escape(finding.get("code", ""))
        name = html.escape(finding.get("name", ""))
        message = html.escape(finding.get("message", ""))
        severity = html.escape(finding.get("severity", ""))

        location = finding.get("location", {})
        row = location.get("row", "")
        column = location.get("column", "")

        rows.append(
            f"""
            <tr>
                <td>{filename}</td>
                <td>{row}:{column}</td>
                <td>{code}</td>
                <td>{name}</td>
                <td>{severity}</td>
                <td>{message}</td>
            </tr>
            """
        )

    if rows:
        violations_table = "".join(rows)
    else:
        violations_table = """
        <tr>
            <td colspan="6">No lint violations found.</td>
        </tr>
        """

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ruff Lint Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #222;
        }}

        h1 {{
            margin-bottom: 30px;
        }}

        .summary {{
            margin-bottom: 30px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
        }}

        th,
        td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            font-weight: bold;
        }}

        code {{
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <h1>Ruff Lint Report</h1>

    <div class="summary">
        <table>
            <tr>
                <th>Control</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Linting</td>
                <td>{status}</td>
            </tr>
            <tr>
                <td>Tool</td>
                <td>Ruff</td>
            </tr>
            <tr>
                <td>Violations</td>
                <td>{violations}</td>
            </tr>
        </table>
    </div>

    <h2>Violations</h2>

    <table>
        <thead>
            <tr>
                <th>File</th>
                <th>Location</th>
                <th>Rule</th>
                <th>Name</th>
                <th>Severity</th>
                <th>Message</th>
            </tr>
        </thead>
        <tbody>
            {violations_table}
        </tbody>
    </table>
</body>
</html>
"""

    output_file.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
