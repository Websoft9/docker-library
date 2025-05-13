## Create User
1. Self-registration mode: Requires SMTP server configuration and email verification. 
2. Admin-added users: Can be marked as "Email Verified" to skip email verification.

## TLS Modes
1. There are three modes of operation: disabled, external, enabled.(default: disabled).
2. SSL Configuration via Websoft9: Requires setting the mode to External, which involves modifying the docker-compose file:
```
command: 'start-from-init --masterkey "MasterkeyNeedsToHave32Characters" --tlsMode external'
```
3. HTTP/2 must be explicitly enabled.
