"""
Telephony Provider Factory
"""

from typing import Optional
from app.config import settings
from app.providers.telephony.base import TelephonyProvider
from app.providers.telephony.twilio import TwilioProvider

_PROVIDERS = {
    "twilio": TwilioProvider,
}


def get_telephony_provider(provider_name: Optional[str] = None) -> TelephonyProvider:
    name = (provider_name or settings.TELEPHONY_PROVIDER or "twilio").lower()
    cls = _PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown telephony provider: {name}")
    return cls()
