"""
claude_analyzer.py
-------------------
Sends CV text to Claude API and gets back structured JSON with PLAIN TEXT
values (no codes). Codes are mapped locally afterwards by code_mapper.py.

Why text-only output:
  - Stuffing 1,200+ lookup codes into the prompt would cost more than the
    savings from skipping local mapping. Cheaper to let Claude return readable
    text and map locally.

Token optimization techniques:
  1. Claude Haiku 4.5 (cheapest, fast)
  2. Pre-extract text locally (no raw files to API)
  3. Concise schema in system prompt
  4. Pre-fill assistant turn with '{' to skip preamble
  5. Hard cap on input text length
"""

import json
from anthropic import Anthropic


SYSTEM_PROMPT = """You extract seafarer CV data into JSON. Output ONLY valid JSON matching this schema exactly. Use null for missing fields. Dates in dd.mm.yyyy format (convert any other format). Country names as 3-letter ISO codes (e.g. UKR, PHL, IDN, USA). Be precise; never invent data.

For coded fields, return the readable TEXT (the program converts to codes later).

Schema:
{
  "personal_information": {
    "name": str (first name only),
    "surname": str (last name only),
    "middle_name": str or null,
    "calling_name": str or null,
    "national_full_name": str or null,
    "date_of_birth": "dd.mm.yyyy" or null,
    "place_of_birth": str or null,
    "status_text": str or null (e.g. "seafarer", "applicant", "pool seafarer"),
    "nationality": str or null (3-letter ISO),
    "citizen_text": str or null (e.g. "Citizen", "Alien", "Non citizen"),
    "marital_status": str or null,
    "gender": "Male" or "Female" or null,
    "number_of_children": int or null,
    "phone": str or null,
    "mobile": str or null,
    "email": str or null,
    "available_from": "dd.mm.yyyy" or null,
    "available_to": "dd.mm.yyyy" or null,
    "fast_note": str or null,
    "client_date": "dd.mm.yyyy" or null,
    "check_in_note": str or null,
    "personal_id": str or null (passport-like ID),
    "accounting_number": str or null,
    "taxation_country": str or null (3-letter ISO),
    "taxation_id": str or null,
    "sss": str or null (Philippines SSS),
    "philhealth": str or null,
    "pag_ibig": str or null,
    "minimum_salary": number or null,
    "salary_currency_text": str or null ("USD","EUR","GBP","BRL"),
    "salary_type_text": str or null ("daily","monthly","annually"),
    "current_country": str or null (3-letter ISO),
    "current_city": str or null,
    "notice_period": int or null,
    "notice_type_text": str or null ("months","weeks","days"),
    "rank_text": str or null (current/latest rank, e.g. "CENG (Chief Engineer)", "DECK FITTER (DECK FITTER)", "CDAD (Cadet Deck)" )
  },
  "certificates": [
    {
      "type_text": str (category: "Travel documents"|"Certificate of Competency"|"Endorsements"|"Medical"|"Training"|"Migr"),
      "name_text": str (specific certificate name, e.g. "Passport", "Basic Safety Training"),
      "issue_country": str or null (3-letter ISO),
      "issuer": str or null,
      "issued": "dd.mm.yyyy" or null,
      "expires": "dd.mm.yyyy" or null,
      "number": str or null (certificate number),
      "notes": str or null
    }
  ],
  "experiences": [
    {
      "vessel_name": str or null,
      "flag": str or null (3-letter ISO),
      "year_built": int or null,
      "type_text": str or null (vessel type, e.g. "Bulk carrier", "Container", "Cruise Ship"),
      "imo_no": str or null,
      "ship_builder": str or null,
      "loa": number or null,
      "dwt": number or null,
      "gt": number or null,
      "pumping_system_text": str or null,
      "cargo_handling_gear_text": str or null,
      "engine_type_text": str or null (e.g. "MAN","Wartsila","Diesel"),
      "engine_model": str or null,
      "engine_power": number or null,
      "dp_type_text": str or null (e.g. "DP Class 2"),
      "dp_manufacturer_text": str or null,
      "operation_type": int or null,
      "location_port": str or null,
      "location_country": str or null (3-letter ISO),
      "rank_text": str or null (rank on this vessel),
      "sign_on": "dd.mm.yyyy" or null,
      "sign_off": "dd.mm.yyyy" or null,
      "off_reason_text": str or null (e.g. "end of contract","promotion"),
      "owner_employer": str or null,
      "crewing_company": str or null
    }
  ]
}"""


class ClaudeAnalyzer:
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}

    def analyze_cv(self, cv_text: str) -> dict:
        """
        Send CV text to Claude, get back parsed JSON dict.
        Raises ValueError if Claude doesn't return valid JSON.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Extract data from this CV:\n\n{cv_text}"},
                {"role": "assistant", "content": "{"},
            ],
        )

        self.last_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        raw_text = "{" + response.content[0].text
        json_text = self._extract_json(raw_text)

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw response (first 500 chars):\n{raw_text[:500]}")

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract the first complete JSON object from text (balanced braces)."""
        depth = 0
        start = text.find("{")
        if start == -1:
            return text
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        return text

    def estimate_cost(self) -> float:
        """Estimate USD cost of the last call (Haiku 4.5 pricing: ~$1/M in, $5/M out)."""
        return (
            self.last_usage["input_tokens"] / 1_000_000 * 1.0
            + self.last_usage["output_tokens"] / 1_000_000 * 5.0
        )
