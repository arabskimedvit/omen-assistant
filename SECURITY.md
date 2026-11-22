# Security

Omen is a personal project and has **not** been security-audited. It can open apps, read and send files, and use a camera on your PC, so please read this before running it.

## Reporting a problem

Please report vulnerabilities privately through GitHub: open the **Security** tab of this repository and choose **Report a vulnerability**. Don't post exploit details in a public issue. This is a spare-time project, so replies may take a few days.

## What I want to hear about

- Getting past the PIN login or the approval cards
- Reading, sending, or opening files in the blocked areas (Windows folders, `AppData`, key folders, Omen's own settings)
- A way to make Omen run an approval-only action without the user tapping Approve
- Path traversal or injection in the web pages

## Out of scope

- Exposing Omen directly to the internet. Don't do this. Use a private network such as Tailscale.
- Anyone with physical or administrator access to your PC, or with your PIN and `config.json`
- Mistakes made by the language model (wrong tool, invented facts). Check what it says.

## How it protects you

- Listens on `127.0.0.1` only. Phone access goes through your own private network.
- PIN login with random, revocable session tokens and growing lockouts.
- Risky actions need an on-screen approval. Typing "approved" does nothing.
- Blocked areas, no sending of password or key files, and no opening of shells or remote-control tools.
- Every action is logged in `logs/actions.log`.
- The camera is off by default.

## Known limits

- The PIN is stored in plain text in your local `config.json`. Keep that file private and never commit it.
- Text from web pages and files can try to trick a small model (prompt injection). Approval cards are the safety net, so read each card.
- Web search uses an unofficial library. Voice recognition happens in your browser and may be sent to Apple or Google.
- Windows only. Not tested on other systems.
