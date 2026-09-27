# Tool for Analysing Banking Web Applications

A security testing tool for banking and fintech web applications. Instead of checking single requests in isolation, it logs in and walks through real multi-step user flows (login, view balance, transfer money, and so on) to find logic and workflow problems that only show up across a whole sequence of actions.

## About

Most scanners look at one request at a time. Banking applications break in more interesting ways: a session that stays valid after logout, an account you can read that isn't yours, or a transfer that gets counted twice under load. This tool simulates a real user, keeps an authenticated session, and checks how the application behaves step by step.

It was built and tested against AltoroMutual (AltoroJ), an intentionally vulnerable demo banking application, so every check has something real to detect.

## What it tests

- SQL injection on the login form. Tries a set of classic bypass payloads and confirms whether any of them logs in without valid credentials.
- IDOR (broken access control). Logs in as one user and tries to read other accounts by changing the account id in the request.
- Session and cookie security. Checks cookies for the HttpOnly, Secure, and SameSite flags, looks for sensitive data leaking inside cookie values, and tests whether an old session id still works after logout.
- Double spending. Fires many concurrent transfer requests for the same amount and compares the balance before and after to see if the server processes a transaction more than once.

## Flow

The tool follows the same steps a person would:

1. Authentication. Log in and capture the session.
2. Endpoint discovery. Look for reachable paths on the target (uses gobuster).
3. Flow execution. Run the selected test flows using the authenticated session.
4. Detection. Compare responses and state, then report what looks vulnerable.

## Project structure

```
fintech-tool/
  main.py                     entry point and command-line interface
  modules/
    __init__.py
    http_client.py            wraps requests, keeps one session, logs calls
    auth.py                   login, logout, balance lookup
    sqli.py                   SQL injection login bypass checks
    idor.py                   access control checks across accounts
    session.py                cookie flags, data leaks, session after logout
    double_spending.py        concurrent transfer race-condition test
    endpoint_discovery.py     directory brute forcing with gobuster
```

## Requirements

- Python 3.8 or newer
- The requests library
- A running AltoroMutual instance (default target is `http://localhost:8080/altoromutual`)
- gobuster on your PATH, only if you use endpoint discovery

Install the Python dependency:

```
pip install requests
```

## Usage

Run everything against the default target:

```
python main.py --all
```

Run a single flow:

```
python main.py --sqli
python main.py --idor
python main.py --session
python main.py --double-spending
```

Point it at a different target or use different credentials:

```
python main.py --target http://localhost:8080/altoromutual --username jsmith --password demo1234 --all
```

If no target, username, or password is given, the tool uses the AltoroMutual defaults (`jsmith` / `demo1234`).

## Example

Running the SQL injection flow prints each payload it tries and whether the login was bypassed, then a short summary of how many payloads worked. The session flow prints each cookie with a SAFE or VULNERABLE verdict per security flag, and the double spending flow prints the balance before and after the burst of transfers so you can see if more than one went through.

## Disclaimer

This tool is for education and for testing applications you own or are explicitly allowed to test. It was written against the AltoroMutual demo application, which exists to be attacked safely. Do not run it against systems you do not have permission to test.

## Author

Diana Tarhoniy (s30930), diploma project, PJATK
GitHub: [dianatarhoniy](https://github.com/dianatarhoniy)
