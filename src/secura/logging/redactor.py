"""Sensitive data redactor for sanitizing logs, audit events, and command histories."""

import re
from typing import Any


class Redactor:
    """Detects and redacts secrets, credentials, API keys, and tokens from text and structures."""

    # Pre-compiled regex patterns for common credentials
    PATTERNS: list[tuple[str, re.Pattern]] = [
        # Private Keys
        (
            "PRIVATE_KEY",
            re.compile(
                r"-----BEGIN [A-Z\s]+PRIVATE KEY-----[\s\S]+?-----END [A-Z\s]+PRIVATE KEY-----",
                re.MULTILINE,
            ),
        ),
        # Command line password flags and protocol commands (e.g. PASS secret, -p secret, --password secret)
        (
            "CLI_PASSWORD",
            re.compile(
                r"((?:^|\s)(?:--?(?:password|pass|passwd|pwd)|-[pP])(?:[=:]\s*|\s+)|\bPASS\s+)([^\s\"';]+)",
                re.IGNORECASE,
            ),
        ),
        # JSON Web Tokens (JWT)
        (
            "JWT_TOKEN",
            re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]+\b"),
        ),
        # Basic/Bearer HTTP Authorization headers (with or without Authorization: prefix)
        (
            "AUTH_HEADER",
            re.compile(
                r"((?:Authorization\s*:\s*)?(?:Bearer|Basic)\s+)([A-Za-z0-9._~+/-]+=*)",
                re.IGNORECASE,
            ),
        ),
        # AWS Access Key ID
        (
            "AWS_KEY",
            re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        ),
        # GitHub Personal Access Token
        (
            "GITHUB_PAT",
            re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b"),
        ),
        # Stripe API Keys
        (
            "STRIPE_KEY",
            re.compile(r"\bsk_(?:live|test)_[0-9a-zA-Z]{24,99}\b"),
        ),
        # Generic Secret / Key assignments in strings (e.g., api_key="secret", token='secret')
        (
            "GENERIC_ASSIGNMENT",
            re.compile(
                r"(?i)\b(api[_-]?key|secret|token|access[_-]?token|password|auth[_-]?token)\s*([=:]\s*[\"']?)(?!\[REDACTED_)([^\s\"';,]+)([\"']?)",
            ),
        ),
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Scrub known secret and credential patterns from a string."""
        if not text or not isinstance(text, str):
            return text

        redacted = text

        for name, pattern in cls.PATTERNS:
            if name == "PRIVATE_KEY":
                redacted = pattern.sub("[REDACTED_PRIVATE_KEY]", redacted)
            elif name == "CLI_PASSWORD":
                redacted = pattern.sub(r"\1[REDACTED_SECRET]", redacted)
            elif name == "JWT_TOKEN":
                redacted = pattern.sub("[REDACTED_JWT]", redacted)
            elif name == "AUTH_HEADER":
                redacted = pattern.sub(r"\1[REDACTED_TOKEN]", redacted)
            elif name == "AWS_KEY":
                redacted = pattern.sub("[REDACTED_AWS_KEY]", redacted)
            elif name == "GITHUB_PAT":
                redacted = pattern.sub("[REDACTED_GITHUB_TOKEN]", redacted)
            elif name == "STRIPE_KEY":
                redacted = pattern.sub("[REDACTED_STRIPE_KEY]", redacted)
            elif name == "GENERIC_ASSIGNMENT":
                redacted = pattern.sub(r"\1\2[REDACTED_SECRET]\4", redacted)

        return redacted

    @classmethod
    def redact_list(cls, items: list[Any]) -> list[Any]:
        """Redact array of items, detecting separated command-line flags (e.g. ['-p', 'secret'])."""
        redacted_items: list[Any] = []
        skip_next = False
        for i, item in enumerate(items):
            if skip_next:
                redacted_items.append("[REDACTED_SECRET]")
                skip_next = False
                continue

            if isinstance(item, str):
                item_lower = item.lower()
                if item_lower in (
                    "-p",
                    "--password",
                    "--pass",
                    "--passwd",
                    "--pwd",
                    "-pwd",
                    "--token",
                    "--api-key",
                    "pass",
                ):
                    redacted_items.append(item)
                    if i + 1 < len(items):
                        skip_next = True
                    continue
                redacted_items.append(cls.redact_text(item))
            else:
                redacted_items.append(cls.redact_data(item))

        return redacted_items

    @classmethod
    def redact_data(cls, data: Any) -> Any:
        """Recursively redact secrets across dictionaries, lists, and strings."""
        if isinstance(data, str):
            return cls.redact_text(data)
        elif isinstance(data, list):
            return cls.redact_list(data)
        elif isinstance(data, tuple):
            return tuple(cls.redact_list(list(data)))
        elif isinstance(data, dict):
            redacted_dict = {}
            for k, v in data.items():
                # If key name itself implies credentials, redact the value entirely
                if isinstance(k, str):
                    key_norm = k.lower().replace("_", "").replace("-", "")
                    if any(
                        secret_word in key_norm
                        for secret_word in [
                            "password",
                            "secret",
                            "token",
                            "apikey",
                            "privatekey",
                            "auth",
                        ]
                    ):
                        redacted_dict[k] = "[REDACTED_CREDENTIAL]"
                        continue
                redacted_dict[k] = cls.redact_data(v)
            return redacted_dict
        return data
