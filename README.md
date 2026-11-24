# Acme Chatbot: PrivTrace CI demo

A live showcase of the **[PrivTrace](https://github.com/dhwani1608/PrivTrace) compliance gate** on a real
GitHub repository. Acme is a small FastAPI + Gemini RAG chatbot. Every pull request to `main` is scanned
against India's DPDP Act 2023, the CERT-In Directions and a security baseline, and the PR **cannot merge**
if it introduces new high or critical personal-data problems.

All names, numbers and keys in this repository are fake.

## See it in action

| Pull request | Change | Gate |
|---|---|---|
| [Add /health endpoint](../../pulls?q=is%3Apr+health) | harmless new endpoint | ✅ passes, score unchanged |
| [Personalised welcome SMS](../../pulls?q=is%3Apr+welcome) | logs the signup payload and sends the user's phone number to Gemini | ❌ fails: new high/critical findings, DPDP score drops |
| [Welcome SMS, privacy-safe](../../pulls?q=is%3Apr+privacy-safe) | the same feature after applying PrivTrace's AI fix prompt | ✅ passes again |

Open the failing PR to see:

- the **sticky PR comment**: score change per framework, each new finding with `file:line` evidence, and a
  copy-paste **AI fix prompt** for Claude, Cursor, Copilot or ChatGPT;
- the red **PrivTrace compliance gate** check, which is required on `main`, so the merge button stays blocked;
- **inline annotations** on the changed lines (SARIF uploaded to code scanning);
- the full HTML report as a workflow artifact.

## How it is wired

- [`.privtrace.yml`](.privtrace.yml): the frameworks Acme picked, its checklist answers, one rule turned off
  with a reason, and the gate (`min_score: 75`, DPDP at least 75, fail on any new high or critical finding).
- [`.github/workflows/privtrace.yml`](.github/workflows/privtrace.yml): checkout, the
  `dhwani1608/PrivTrace@main` action, SARIF upload. AI is off, so no code leaves the runner.
- Branch protection on `main` requires the **PrivTrace compliance gate** check.

Web app: <https://privtrace-836138728232.asia-south1.run.app>

## Use it in your own repository

1. Copy `.privtrace.yml` (or generate one with `privtrace init`) and adjust the packs and answers.
2. Copy `.github/workflows/privtrace.yml`.
3. Make **PrivTrace compliance gate** a required status check on `main`.

PrivTrace findings are engineering evidence, not legal advice.
