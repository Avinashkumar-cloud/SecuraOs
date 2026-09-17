"""Target validation and safety analysis engine."""

import ipaddress
import re

from pydantic import BaseModel

from secura.scope.models import TargetType


class ValidationResult(BaseModel):
    """Result of validating a target string."""

    is_valid: bool
    canonical_target: str
    target_type: TargetType | None = None
    is_private: bool = True
    warning: str | None = None
    error: str | None = None


DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
HOSTNAME_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")


class TargetValidator:
    """Validates target strings, infers target type, and identifies safety warnings."""

    @classmethod
    def validate(cls, target_str: str) -> ValidationResult:
        """Validate and classify a target string."""
        raw = target_str.strip()
        if not raw:
            return ValidationResult(
                is_valid=False,
                canonical_target="",
                error="Target cannot be empty",
            )

        # 1. Check for Local Lab target prefix or syntax
        if raw.startswith("lab:") or raw.endswith(".lab") or raw.endswith(".internal"):
            return ValidationResult(
                is_valid=True,
                canonical_target=raw.lower(),
                target_type=TargetType.LOCAL_LAB,
                is_private=True,
                warning=None,
            )

        # 2. Check for IPv4 CIDR
        if "/" in raw and ":" not in raw:
            try:
                net4 = ipaddress.IPv4Network(raw, strict=False)
                is_priv = net4.is_private or net4.is_loopback or net4.is_link_local
                warning = None

                if net4.prefixlen < 16:
                    warning = f"Suspiciously broad IPv4 range /{net4.prefixlen} ({net4.num_addresses:,} addresses)."
                elif not is_priv:
                    warning = "Public IP subnet detected. Explicit authorization from network owner is mandatory."

                return ValidationResult(
                    is_valid=True,
                    canonical_target=str(net4),
                    target_type=TargetType.CIDR_V4,
                    is_private=is_priv,
                    warning=warning,
                )
            except ValueError as e:
                return ValidationResult(
                    is_valid=False,
                    canonical_target=raw,
                    error=f"Malformed IPv4 CIDR network: {str(e)}",
                )

        # 3. Check for IPv6 CIDR
        if "/" in raw and (":" in raw):
            try:
                net6 = ipaddress.IPv6Network(raw, strict=False)
                is_priv = net6.is_private or net6.is_loopback or net6.is_link_local
                warning = None

                if net6.prefixlen < 48:
                    warning = f"Suspiciously broad IPv6 range /{net6.prefixlen}."
                elif not is_priv:
                    warning = "Public IPv6 subnet detected. Explicit authorization from network owner is mandatory."

                return ValidationResult(
                    is_valid=True,
                    canonical_target=str(net6),
                    target_type=TargetType.CIDR_V6,
                    is_private=is_priv,
                    warning=warning,
                )
            except ValueError as e:
                return ValidationResult(
                    is_valid=False,
                    canonical_target=raw,
                    error=f"Malformed IPv6 CIDR network: {str(e)}",
                )

        # 4. Check for single IPv4 Address
        if ":" not in raw:
            try:
                ip4 = ipaddress.IPv4Address(raw)
                is_priv = ip4.is_private or ip4.is_loopback or ip4.is_link_local
                warning = None
                if not is_priv:
                    warning = "Public IP address detected. Explicit authorization from owner is mandatory."

                return ValidationResult(
                    is_valid=True,
                    canonical_target=str(ip4),
                    target_type=TargetType.IPV4,
                    is_private=is_priv,
                    warning=warning,
                )
            except ValueError:
                pass  # Fall through to domain check

        # 5. Check for single IPv6 Address
        if ":" in raw:
            try:
                ip6 = ipaddress.IPv6Address(raw)
                is_priv = ip6.is_private or ip6.is_loopback or ip6.is_link_local
                warning = None
                if not is_priv:
                    warning = "Public IPv6 address detected. Explicit authorization from owner is mandatory."

                return ValidationResult(
                    is_valid=True,
                    canonical_target=str(ip6),
                    target_type=TargetType.IPV6,
                    is_private=is_priv,
                    warning=warning,
                )
            except ValueError:
                pass

        # 6. Check for Domain / Hostname
        clean_name = raw.lower()
        if clean_name in ["localhost", "localhost.localdomain"]:
            return ValidationResult(
                is_valid=True,
                canonical_target=clean_name,
                target_type=TargetType.DOMAIN,
                is_private=True,
                warning=None,
            )

        if DOMAIN_REGEX.match(clean_name):
            warning = (
                "Domain target resolved over public DNS. Verify in-scope ownership before testing."
            )
            return ValidationResult(
                is_valid=True,
                canonical_target=clean_name,
                target_type=TargetType.DOMAIN,
                is_private=False,
                warning=warning,
            )

        if HOSTNAME_REGEX.match(clean_name):
            return ValidationResult(
                is_valid=True,
                canonical_target=clean_name,
                target_type=TargetType.DOMAIN,
                is_private=True,
                warning=None,
            )

        return ValidationResult(
            is_valid=False,
            canonical_target=raw,
            error="Target must be a valid IPv4, IPv6, CIDR range, domain name, or local lab identifier.",
        )
