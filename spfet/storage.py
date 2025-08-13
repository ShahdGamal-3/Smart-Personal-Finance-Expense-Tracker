from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import os

from .utils import safe_load_json, safe_write_json, user_file, iso_now
from .constants import ALLOWED_CATEGORIES

@dataclass
class Transaction:
    """Represents a single transaction."""
    amount: float
    category: str
    ttype: str  # "income" or "expense"
    date: str = field(default_factory=iso_now)

@dataclass
class UserData:
    """Stores all data related to a user."""
    auth: Dict[str, Any]
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    budgets: Dict[str, float] = field(default_factory=dict)

class UserStore:
    """Handles loading and saving a user's data file."""
    
    def __init__(self, username: str) -> None:
        self.username = username
        self.path = user_file(username)
        self.data: UserData | None = None

    def exists(self) -> bool:
        """Check if the user's file exists."""
        return os.path.exists(self.path)

    def load(self) -> None:
        """Load the user's data from file."""
        raw = safe_load_json(self.path)
        if not raw:
            self.data = None
            return
        self.data = UserData(
            auth=raw.get("auth", {}),
            transactions=raw.get("transactions", []),
            budgets=raw.get("budgets", {})
        )

    def init_new(self, auth: Dict[str, Any]) -> None:
        """Initialize a new user file."""
        self.data = UserData(
            auth=auth,
            transactions=[],
            budgets={c: 0.0 for c in ALLOWED_CATEGORIES}
        )
        self.save()

    def save(self) -> None:
        """Save current user data to file."""
        assert self.data is not None
        payload = {
            "auth": self.data.auth,
            "transactions": self.data.transactions,
            "budgets": self.data.budgets,
        }
        safe_write_json(self.path, payload)
