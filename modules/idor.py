import re

from modules.finding import Finding


class IDOR:
    def __init__(self, client, auth,config):
        self.client = client
        self.auth = auth
        self.config = config

    def check_account(self, account_id):
        path = self.config["path"]
        param = self.config["param"]
        response = self.client.get(f"{path}?{param}={account_id}")

        if f"Account History - {account_id}" in response.text:
            match = re.search(r'Ending balance.*?<td align="right">(.*?)</td>',
                              response.text, re.DOTALL)
            balance = match.group(1).strip() if match else "unknown"
            return True, balance

        return False, None

    def run(self):
        own_account  = self.config["own_account"]
        accounts_to_test = self.config["accounts_to_test"]
        print("\n--- IDOR Detection ---")
        print(f"Logged in as: jsmith (owns account {own_account})")
        print(f"Testing access to other accounts...\n")

        findings = []

        for account_id in accounts_to_test:
            accessible, balance = self.check_account(account_id)

            if account_id == own_account:
                print(f"[OWN ACCOUNT] Account {account_id} - accessible (expected)")
            elif accessible:
                print(f"[VULNERABLE]  Account {account_id} - ACCESSIBLE, balance leaked: {balance}")
                findings.append(Finding(
                    check="IDOR",
                    severity="HIGH",
                    title=f"Unauthorized access to account {account_id}",
                    evidence=f"account {account_id} is accessible while logged in as jsmith;"
                             f" balance leaked: {balance}"
                ))
            else:
                print(f"[SAFE]        Account {account_id} - not accessible")

        print(f"\n[SUMMARY] {len(findings)} unauthorized accounts exposed.")
        if not findings:
            findings.append(Finding(
                check="IDOR",
                severity="SAFE",
                title="No IDOR vulnerabilities found",
                evidence="All other accounts denied access"
            ))
        return findings