"""
supabase_manager.py
--------------------
Handles all database operations for the 3-table schema:
  - personal_information (main)
  - certificates         (one-to-many)
  - experiences          (one-to-many)

Operations:
  - find_existing(name, surname, dob, email) -> existing row or None
  - insert_seafarer(data, filename) -> new UUID
  - update_seafarer(uuid, data, filename)
"""

from typing import Optional, List
from supabase import create_client, Client


# Columns that exist on personal_information
PI_COLUMNS = [
    "name", "surname", "middle_name", "calling_name", "national_full_name",
    "date_of_birth", "place_of_birth", "status", "nationality", "citizen",
    "marital_status", "gender", "number_of_children",
    "phone", "mobile", "email",
    "available_from", "available_to", "fast_note", "client_date", "check_in_note",
    "personal_id", "accounting_number", "taxation_country", "taxation_id",
    "sss", "philhealth", "pag_ibig",
    "minimum_salary", "salary_currency", "salary_type",
    "current_country", "current_city",
    "notice_period", "notice_type", "rank",
]

CERT_COLUMNS = [
    "cert_id", "type", "issue_country", "issuer",
    "issued", "expires", "number", "notes", "cert_name",
]

EXP_COLUMNS = [
    "vessel_name", "flag", "year_built", "type", "imo_no", "ship_builder",
    "loa", "dwt", "gt",
    "pumping_system", "cargo_handling_gear",
    "engine_type", "engine_model", "engine_power",
    "dp_type", "dp_manufacturer", "operation_type",
    "location_port", "location_country",
    "rank", "sign_on", "sign_off", "off_reason",
    "owner_employer", "crewing_company",
]


def _clean_row(row: dict, allowed_columns: list) -> dict:
    """Keep only allowed columns, normalize empty strings to None."""
    out = {}
    for col in allowed_columns:
        v = row.get(col)
        if v == "":
            v = None
        out[col] = v
    return out


class SupabaseManager:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    # -------------------- DUPLICATE CHECK --------------------
    def find_existing(
        self,
        name: Optional[str],
        surname: Optional[str],
        date_of_birth: Optional[str],
        email: Optional[str],
    ) -> Optional[dict]:
        """
        Look for an existing seafarer by:
          1. name + surname + DOB match, OR
          2. email match
        Returns the full row dict or None.
        """
        # name + surname + DOB
        if name and surname and date_of_birth:
            res = (
                self.client.table("personal_information")
                .select("*")
                .eq("name", name)
                .eq("surname", surname)
                .eq("date_of_birth", date_of_birth)
                .limit(1)
                .execute()
            )
            if res.data:
                return res.data[0]

        # email
        if email:
            res = (
                self.client.table("personal_information")
                .select("*")
                .eq("email", email)
                .limit(1)
                .execute()
            )
            if res.data:
                return res.data[0]

        return None

    # -------------------- INSERT --------------------
    def insert_seafarer(
        self,
        personal: dict,
        certificates: List[dict],
        experiences: List[dict],
        source_filename: str = "",
    ) -> str:
        """Insert a new seafarer (with certs + experiences). Returns the new UUID."""
        pi_row = _clean_row(personal, PI_COLUMNS)
        pi_row["cv_source_filename"] = source_filename or None

        result = self.client.table("personal_information").insert(pi_row).execute()
        seafarer_id = result.data[0]["id"]

        self._insert_certificates(seafarer_id, certificates)
        self._insert_experiences(seafarer_id, experiences)

        return seafarer_id

    # -------------------- UPDATE --------------------
    def update_seafarer(
        self,
        seafarer_id: str,
        personal: dict,
        certificates: List[dict],
        experiences: List[dict],
        source_filename: str = "",
    ) -> None:
        """
        Update existing seafarer.
        Strategy:
          - Update main row (skip null values so we don't wipe existing data)
          - Replace ALL certificates and experiences with the new ones from this CV
        """
        pi_row = _clean_row(personal, PI_COLUMNS)
        pi_row = {k: v for k, v in pi_row.items() if v is not None}
        if source_filename:
            pi_row["cv_source_filename"] = source_filename

        if pi_row:
            self.client.table("personal_information").update(pi_row).eq("id", seafarer_id).execute()

        # Replace certs and experiences
        self.client.table("certificates").delete().eq("seafarer_id", seafarer_id).execute()
        self.client.table("experiences").delete().eq("seafarer_id", seafarer_id).execute()

        self._insert_certificates(seafarer_id, certificates)
        self._insert_experiences(seafarer_id, experiences)

    # -------------------- HELPERS --------------------
    def _insert_certificates(self, seafarer_id: str, certs: list) -> None:
        if not certs:
            return
        rows = []
        for c in certs:
            cleaned = _clean_row(c, CERT_COLUMNS)
            if not any(v is not None for v in cleaned.values()):
                continue
            cleaned["seafarer_id"] = seafarer_id
            rows.append(cleaned)
        if rows:
            self.client.table("certificates").insert(rows).execute()

    def _insert_experiences(self, seafarer_id: str, exps: list) -> None:
        if not exps:
            return
        rows = []
        for e in exps:
            cleaned = _clean_row(e, EXP_COLUMNS)
            if not any(v is not None for v in cleaned.values()):
                continue
            cleaned["seafarer_id"] = seafarer_id
            rows.append(cleaned)
        if rows:
            self.client.table("experiences").insert(rows).execute()
