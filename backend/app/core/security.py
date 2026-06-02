"""
app/core/security.py
────────────────────
Cryptographic utilities for the CarbonCalc platform.

Currently provides:
    - Password hashing    (used by POST /users/ on registration)
    - Password verification (used by POST /auth/login — Phase 2)

Why direct bcrypt instead of passlib?
    passlib 1.7.4 (latest) is incompatible with bcrypt 5.x. passlib's
    internal self-test calls bcrypt with a 72-byte vector, which bcrypt 5.x
    now rejects with ValueError (breaking change in bcrypt 5.0).

    Using the bcrypt library directly:
      - Eliminates the compatibility layer entirely
      - Is equally secure — same algorithm, same cost factor
      - Is actively maintained (bcrypt 5.x is the current release)
      - Aligns with how modern Python projects use bcrypt

Design principles:
    - All crypto is centralised here. No other module imports bcrypt directly.
    - Changing cost factor or algorithm requires editing only this file.

Future additions to this file:
    - JWT token creation / verification   (Phase 2 — Auth)
    - API key generation / hashing        (Phase 3 — Company API access)
    - Signing payloads for agent webhooks (Phase 5 — LangGraph agents)
"""

import bcrypt

# Cost factor for bcrypt. 12 is the production-appropriate default:
#   - Fast enough: ~300ms per hash (unnoticeable to users)
#   - Slow enough: GPU brute-force is computationally prohibitive
# Increase to 13 or 14 if hardware improves and latency allows.
_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Called once during user registration (POST /users/).
    The result is stored in the `hashed_password` column.
    The plaintext password is never persisted anywhere.

    Args:
        plain_password: The raw password string from the request body.

    Returns:
        A bcrypt hash string (e.g. "$2b$12$...") safe to store in PostgreSQL.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")  # Store as string in PostgreSQL VARCHAR column


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Called during login (POST /auth/login) — Phase 2.
    bcrypt.checkpw() performs timing-safe comparison internally to prevent
    timing-based side-channel attacks.

    Args:
        plain_password:   The raw password from the login request.
        hashed_password:  The stored bcrypt hash from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)

