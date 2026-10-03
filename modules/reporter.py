import json
from dataclasses import asdict

class Reporter:
    def __init__(self, findings):
        self.findings = findings
    def write_json(self, path="report.json"):
        data = [asdict(finding) for finding in self.findings]
        with open(path, "w") as file:
            json.dump(data,file,indent = 2)
        print(f"[REPORT] JSON written to {path}")
