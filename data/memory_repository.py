"""In-memory repository used by the prototype.

It has exactly the same methods the SQL Server repository will have, so the
rest of the program won't change when the real database is connected.
Data here is lost when the app closes.
"""
import copy

from data.seed_data import GLOSSARY, INDUSTRIES
from logic.models import Business, GlossaryTerm, Industry, UserProfile


class MemoryRepository:
    def __init__(self):
        self._profiles = []
        self._industries = []
        self._businesses = []
        self._results = []
        self._glossary = [GlossaryTerm(t, d, e) for t, d, e in GLOSSARY]
        self._next_id = {"profile": 1, "business": 1}
        for i, row in enumerate(INDUSTRIES, start=1):
            self._industries.append(Industry(i, *row))

    # ---- profiles -------------------------------------------------------
    def get_profiles(self):
        return list(self._profiles)

    def add_profile(self, username):
        profile = UserProfile(self._next_id["profile"], username)
        self._next_id["profile"] += 1
        self._profiles.append(profile)
        return profile

    # ---- industries -----------------------------------------------------
    def get_industries(self):
        return list(self._industries)

    def get_industry(self, industry_id):
        for industry in self._industries:
            if industry.industry_id == industry_id:
                return industry
        return None

    # ---- businesses -----------------------------------------------------
    def add_business(self, business: Business):
        stored = copy.copy(business)
        stored.business_id = self._next_id["business"]
        self._next_id["business"] += 1
        self._businesses.append(stored)
        return copy.copy(stored)

    def get_business(self, business_id):
        for business in self._businesses:
            if business.business_id == business_id:
                return copy.copy(business)
        return None

    def get_businesses_for_user(self, user_id):
        return [copy.copy(b) for b in self._businesses if b.user_id == user_id]

    def update_business(self, business: Business):
        for i, stored in enumerate(self._businesses):
            if stored.business_id == business.business_id:
                self._businesses[i] = copy.copy(business)
                return

    # ---- monthly results ------------------------------------------------
    def add_result(self, result):
        self._results.append(copy.copy(result))

    def get_results(self, business_id):
        """Results for one business, in month order (as the SQL ORDER BY will give)."""
        rows = [copy.copy(r) for r in self._results if r.business_id == business_id]
        # Results are only ever appended in month order, so no sort is needed.
        return rows

    def save_month(self, result, business: Business):
        """Store a month's result and the business's new position together.
        The SQL version does both in one transaction."""
        self.add_result(result)
        self.update_business(business)

    def check_connection(self):
        """Nothing to check: memory is always available."""

    def close(self):
        """Nothing to close."""

    # ---- glossary -------------------------------------------------------
    def get_glossary(self):
        return list(self._glossary)
