# Testing SMTP (Brevo) before deploying

Confirm email delivery works **before** buying a domain or provisioning a
server. SMTP is independent of the domain, so this is a good early check. Two
tests, simplest first:

1. **Standalone test** — proves the Brevo credentials work, with no app running.
2. **Through-the-app test** — proves the full path (app → worker → SMTP) works
   on the local dev stack.

Do #1 first (instant confidence), then #2 if you want to validate the whole
chain. Neither requires a domain.

---

## Prerequisites (one-time, in Brevo)

1. Sign up at https://www.brevo.com and stay on the **Free** plan (skip any paid
   upsell — the free tier includes SMTP and 300 emails/day).
2. **Verify a sender:** Brevo → *Senders, domains, IPs* → *Senders* → *Add a
   sender*. Use an email you control; click the confirmation link Brevo sends.
   This address is your `SMTP_FROM_EMAIL`. (Verifying a whole domain comes
   later, once you own it.)
3. **Get SMTP credentials:** Brevo → *Settings* → *SMTP & API* → *SMTP* tab.
   - `SMTP_HOST` = `smtp-relay.brevo.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USERNAME` = the **Login** shown there (e.g. `1a2b3c001@smtp-brevo.com`)
   - Click **Generate SMTP key**, name it, and **copy the key once shown** →
     that is your `SMTP_PASSWORD` (not your account password).
4. Have a **test inbox** you can open (any email you can read) for the `--to`
   recipient.

> Do NOT commit these values anywhere. Export them in your shell for the test,
> or keep them in a gitignored file.

---

## Test 1 — Standalone (no app)

`scripts/test_smtp.py` sends one email using the exact same smtplib sequence the
app uses (SMTP → STARTTLS → login → send), so a pass predicts the app will work.

Run it from the repo root on your Mac (Python 3 only, no dependencies):

```bash
export SMTP_HOST=smtp-relay.brevo.com
export SMTP_PORT=587
export SMTP_USERNAME='PASTE_BREVO_LOGIN'          # e.g. 1a2b3c001@smtp-brevo.com
export SMTP_PASSWORD='PASTE_BREVO_SMTP_KEY'
export SMTP_FROM_EMAIL='your-verified-sender@example.com'
export SMTP_USE_TLS=true

python3 scripts/test_smtp.py --to you@example.com
```

Expected:

```
Connecting to smtp-relay.brevo.com:587 (TLS=True) as 1a2b3c001@smtp-brevo.com ...
PASS: message accepted by smtp-relay.brevo.com for delivery to you@example.com.
```

Then **check that inbox (and spam)** for an "Inventzo SMTP test" email.

Common failures the script explains for you:
- **authentication rejected** → `SMTP_USERNAME`/`SMTP_PASSWORD` wrong. Username
  is the Brevo *Login*, password is the *generated SMTP key*.
- **sender refused** → `SMTP_FROM_EMAIL` is not a verified sender in Brevo.
- **could not send / timeout** → network/firewall blocking outbound port 587.

> Tip: when your shell history is a concern, put the exports in a gitignored
> file and run `python3 scripts/test_smtp.py --env-file that-file --to you@example.com`.

---

## Test 2 — Through the app (local dev stack)

This proves the worker actually delivers a password-reset email end to end.

1. Put the Brevo values into the local `.env` (gitignored). The dev stack reads
   `.env`. Set:

   ```
   SMTP_HOST=smtp-relay.brevo.com
   SMTP_PORT=587
   SMTP_USERNAME=PASTE_BREVO_LOGIN
   SMTP_PASSWORD=PASTE_BREVO_SMTP_KEY
   SMTP_FROM_EMAIL=your-verified-sender@example.com
   SMTP_USE_TLS=true
   ```

2. Recreate backend + worker so they pick up the new env (the dev stack does not
   hot-reload env):

   ```bash
   docker compose up -d --force-recreate backend worker
   ```

3. Create a test user whose email is a real inbox you can check, then trigger a
   reset. The password-reset request endpoint is public:

   ```bash
   # From the repo root — request a reset for that user's email
   curl -s -X POST http://localhost:8000/api/v1/auth/reset-password \
     -H 'Content-Type: application/json' \
     -d '{"email":"your-test-inbox@example.com"}'
   # Always returns a generic message (no account enumeration)
   ```

4. Check the worker logs and the inbox:

   ```bash
   docker compose logs worker | tail -30
   ```

   A successful send shows the job completing without a `TransientJobError`.
   The reset email should arrive in the inbox (check spam).

> The dev stack runs with `ENVIRONMENT=development`, so if `SMTP_HOST` is unset
> it uses a console sender that does **not** send real mail — that's why you set
> the Brevo values in `.env` for this test.

---

## After testing

- Leave the local `.env` SMTP values in place or clear them — either way they're
  gitignored and never leave your machine.
- On the server, the same Brevo `SMTP_USERNAME` / `SMTP_PASSWORD` / verified
  `SMTP_FROM_EMAIL` go into each customer's `customers/<slug>/.env`
  (`scripts/provision_customer.sh` pre-fills host/port/TLS for Brevo). See
  `DEPLOY_HETZNER.md`.
- Once you own the product domain, verify it in Brevo and switch
  `SMTP_FROM_EMAIL` to `no-reply@yourdomain.com` for better deliverability.
