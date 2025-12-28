# Security, Verification, and Pro Mode

This project includes safety controls for file/system actions, audit logging, and optional authentication.

Authentication (PIN)
- Configure a PIN for sensitive operations stored in memory/auth.json (PBKDF2-SHA256 with salt and iterations).
- You can set it interactively by calling memory.auth.set_pin_interactive() from a Python shell, or the app will offer setup at runtime.
- A successful authentication grants a short-lived session (default 15 minutes) before asking again.

Modes
- Normal mode (default): asks before system-level actions.
- Pro mode: automatically runs low-risk actions but still confirms medium/high-risk actions.
- Mode is stored in memory/state.json and can be toggled by set_mode('normal'|'pro').

Sandboxed file operations
- Allowed directories are defined in memory/security.json. Only paths inside allowed directories are permitted.
- Protected roots like C:\ and / are blocked.
- Add allowed directories using add_allowed_directory(path).

Confirmations
- Destructive operations (delete/wipe/format) require strict confirmation (typing CONFIRM).
- In Normal mode, file/system operations also require a y/n confirmation.

Audit logging
- All actions are logged to logs/activity.log in JSON lines: timestamp, action, status, details.
- Use this to audit what the assistant did.

Notes
- Keep your PIN secret; the hash and salt are stored locally and are not transmitted.
- Logs may contain file paths and action names but do not include personal content unless part of the operation details.
