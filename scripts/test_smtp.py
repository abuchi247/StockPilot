#!/usr/bin/env python3
"""Standalone SMTP connectivity + delivery test.

Sends one real email using the same sequence the app uses in production
(smtplib SMTP -> STARTTLS -> login -> send_message), so a success here means the
credentials and provider work before you wire them into a deployment.

It reads SMTP settings from environment variables (or a --env-file), never from
source, so no secrets are committed. Nothing in the app is imported — this is a
pure connectivity check.

Usage:
  # 1) export the values (or put them in a file and use --env-file)
  export SMTP_HOST=smtp-relay.brevo.com
  export SMTP_PORT=587
  export SMTP_USERNAME='1a2b3c001@smtp-brevo.com'   # Brevo "Login"
  export SMTP_PASSWORD='xkeysib-...'                # Brevo generated SMTP key
  export SMTP_FROM_EMAIL='you@verified-sender.com'  # a sender verified in Brevo
  export SMTP_USE_TLS=true
  python3 scripts/test_smtp.py --to you@example.com

  # or read the values from a dotenv-style file (KEY=value lines):
  python3 scripts/test_smtp.py --env-file customers/bro/.env --to you@example.com

The --to inbox is where the test message is delivered; check it to confirm
receipt (and check spam). Prints clear PASS/FAIL with the failure reason.
"""

import argparse
import smtplib
import ssl
import sys
from email.message import EmailMessage


def load_env_file(path: str) -> dict:
    values = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Send one test email via SMTP.")
    parser.add_argument("--to", required=True, help="Recipient inbox to deliver the test email to.")
    parser.add_argument("--env-file", help="Optional dotenv-style file to read SMTP_* from.")
    args = parser.parse_args()

    import os
    env = dict(os.environ)
    if args.env_file:
        env.update(load_env_file(args.env_file))

    host = env.get("SMTP_HOST")
    port = int(env.get("SMTP_PORT", "587"))
    username = env.get("SMTP_USERNAME") or ""
    password = env.get("SMTP_PASSWORD") or ""
    from_email = env.get("SMTP_FROM_EMAIL")
    use_tls = str(env.get("SMTP_USE_TLS", "true")).lower() in ("1", "true", "yes")

    missing = [k for k, v in {
        "SMTP_HOST": host,
        "SMTP_FROM_EMAIL": from_email,
    }.items() if not v]
    if missing:
        print(f"FAIL: missing required setting(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    print(f"Connecting to {host}:{port} (TLS={use_tls}) as {username or '(no auth)'} ...")

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = args.to
    message["Subject"] = "StockPilot SMTP test"
    message.set_content(
        "This is a StockPilot SMTP connectivity test.\n\n"
        "If you received this, your SMTP settings work and the app will be able "
        "to send password-reset emails.\n"
    )

    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.ehlo()
            if use_tls:
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        print(f"FAIL: authentication rejected. Check SMTP_USERNAME (Brevo Login) "
              f"and SMTP_PASSWORD (the generated SMTP key). Detail: {exc.smtp_code}", file=sys.stderr)
        return 1
    except smtplib.SMTPRecipientsRefused as exc:
        print(f"FAIL: recipient refused: {exc.recipients}", file=sys.stderr)
        return 1
    except smtplib.SMTPSenderRefused as exc:
        print("FAIL: sender refused. SMTP_FROM_EMAIL must be a sender/domain "
              f"verified in your provider. Detail: {exc}", file=sys.stderr)
        return 1
    except (OSError, smtplib.SMTPException) as exc:
        print(f"FAIL: could not send. {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: message accepted by {host} for delivery to {args.to}.")
    print("Now check that inbox (and the spam folder) to confirm it actually arrived.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
