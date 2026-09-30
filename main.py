import argparse
from modules.http_client import HttpClient
from modules.auth import Auth
from modules.double_spending import DoubleSpending
from modules.idor import IDOR
from modules.session import SessionTesting
from modules.sqli import SQLInjection

def parse_args():
    parser = argparse.ArgumentParser(
        description="Security testing tool for banking web applications"
    )

    parser.add_argument("--target", default="http://localhost:8080/altoromutual",
                        help="Target URL (default: http://localhost:8080/altoromutual)")
    parser.add_argument("--username", default="jsmith",
                        help="Username (default: jsmith)")
    parser.add_argument("--password", default="demo1234",
                        help="Password (default: demo1234)")

    # Flow flags
    parser.add_argument("--all", action="store_true",
                        help="Run all flows")
    parser.add_argument("--sqli", action="store_true",
                        help="Run SQL injection testing")
    parser.add_argument("--idor", action="store_true",
                        help="Run IDOR testing")
    parser.add_argument("--session", action="store_true",
                        help="Run session and cookie testing")
    parser.add_argument("--double-spending", action="store_true",
                        help="Run double spending detection")

    return parser.parse_args()

def main():
    args = parse_args()

    print(f"\n{'='*50}")
    print(f"  Banking Security Scanner")
    print(f"  Target: {args.target}")
    print(f"{'='*50}\n")

    if args.sqli or args.all:
        client = HttpClient(args.target)
        sqli = SQLInjection(client)
        sqli.run()

    client = HttpClient(args.target)
    auth = Auth(client, args.username, args.password)
    login_success = auth.login()

    if not login_success:
        print("[ERROR] Login failed - cannot run authenticated flows")
        return

    if args.idor or args.all:
        idor = IDOR(client, auth)
        idor.run()

    if args.session or args.all:
        session = SessionTesting(client, auth)
        session.check_flags()
        session.check_data_leaks()
        session.check_session_after_logout()


    if args.double_spending or args.all:
        print("\n[INFO] Re-authenticating for double spending test...")
        client = HttpClient(args.target)
        auth = Auth(client, args.username, args.password)
        auth.login()
        ds = DoubleSpending(client, auth)
        ds.run()

    print(f"\n{'='*50}")
    print(f"  Scan Complete")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()