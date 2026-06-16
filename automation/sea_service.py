from difflib import SequenceMatcher
from html import unescape
from random import random
from playwright.sync_api import Page

from automation.map_cert import CERT_FIELD_MAPPING, CERT_ID_LOCATORS, CERTIFICATE_MAPPINGS, SAVE_MAPPING
from automation.map_rank import RANK_MAPPING

class SeaServicePage:
    
    def __init__(self, page: Page):
        self.page = page
        
        
    def similarity_vessel_type(self, a: str, b: str) -> float:
        return SequenceMatcher(
            None,
            a.lower().strip(),
            b.lower().strip()
        ).ratio()
        
    
    def normalize_rank(self, text: str) -> str:
        return " ".join(text.lower().strip().split())


    def similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(
            None,
            self.normalize_rank(a),
            self.normalize_rank(b)
        ).ratio()

    def resolve_rank(self, rank_text: str, available_options: list[str]):

        rank_text = self.normalize_rank(rank_text)

        # Step 1 - exact mapping
        if rank_text in RANK_MAPPING:
            mapped_rank = RANK_MAPPING[rank_text]

            for option in available_options:
                if self.normalize_rank(option) == self.normalize_rank(mapped_rank):
                    return option

        # Step 2 - fuzzy (ambil 3 terbaik)
        candidates = []

        for option in available_options:
            score = self.similarity(rank_text, option)

            candidates.append(
                {
                    "label": option,
                    "score": score
                }
            )

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        top3 = candidates[:3]

        for candidate in top3:
            print(
                f"[RANK MATCH] "
                f"{rank_text} -> {candidate['label']} "
                f"({candidate['score']:.2f})"
            )

        best = top3[0]

        if best["score"] >= 0.7:
            return best["label"]

        return None
    
    def select_rank(self, rank_text: str):

        select = self.page.locator("#rank_list")

        options = select.locator("option")

        available_options = []
        
        if rank_text is None:
            select.select_option(
                value="29"
            )
            return

        for i in range(options.count()):
            label = options.nth(i).inner_text().strip()

            if label and label != "-Choose rank-":
                available_options.append(label)

        resolved_rank = self.resolve_rank(
            rank_text,
            available_options
        )

        if resolved_rank:
            print(f"Selected rank: {resolved_rank}")

            select.select_option(
                label=resolved_rank
            )
        else:
            print(
                f"Rank '{rank_text}' tidak ditemukan, "
                f"gunakan Other (29)"
            )

            select.select_option(
                value="29"
            )
        
        
    def fill_experience(self, exp: dict):

        vessel_name = exp.get("vessel_name")
        if vessel_name:
            self.page.locator("#vessel_name").fill(vessel_name)

        flag = exp.get("flag")
        if flag:
            self.select_country(
                "#vessel_country_code",
                flag
            )

        year_built = exp.get("year_built")
        if year_built:
            self.page.locator("#vessel_year").fill(
                str(year_built)
            )

        vessel_type = exp.get("type_text")
        if vessel_type:
            self.select_vessel_type(vessel_type)
            
        loa = exp.get("loa")
        if loa:
            self.page.locator("#vessel_length").fill(str(loa))
            
        dwt = exp.get("dwt")
        if dwt:
            self.page.locator("#vessel_dwt").fill(str(dwt))
            
        gt = exp.get("gt")
        if gt:
            self.page.locator("#vessel_gt").fill(str(gt))

        sign_on = exp.get("sign_on")
        if sign_on:
            self.page.locator("#on_date").fill(sign_on)

        sign_off = exp.get("sign_off")
        if sign_off:
            self.page.locator("#off_date").fill(sign_off)

        owner = exp.get("owner_employer")
        if owner:
            self.page.locator("#owner_name").fill(owner)
            
        rank = exp.get("rank_test")
        self.select_rank(rank)
            
        
            
    def select_vessel_type(self, type_text: str):

        select = self.page.locator("#vessel_type_list")

        options = [
            text.strip()
            for text in select.locator("option").all_inner_texts()
            if text.strip()
        ]

        candidates = []

        for option in options:
            score = self.similarity_vessel_type(type_text, option)

            candidates.append(
                {
                    "label": option,
                    "score": score
                }
            )

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        top3 = candidates[:3]

        best = top3[0]

        print(
            f"VESSEL TYPE: {type_text} "
            f"-> {best['label']} "
            f"({best['score']:.2f})"
        )

        if best["score"] >= 0.75:
            select.select_option(
                label=best["label"]
            )
        else:
            # Other
            select.select_option(
                value="32"
            )
            

    def select_certificate_type(self, type_text: str):

        button_mapping = {
            "Travel documents": "#list_form > table.list > tbody > tr:nth-child(13) > td.section.r > input[type=button]",
            "Migr": "#list_form > table.list > tbody > tr:nth-child(3) > td.section.r > input[type=button]",
            "Certificate of Competency": "#list_form > table.list > tbody > tr:nth-child(5) > td.section.r > input[type=button]",
            "Endorsements": "#list_form > table.list > tbody > tr:nth-child(7) > td.section.r > input[type=button]",
            "Medical": "#list_form > table.list > tbody > tr:nth-child(9) > td.section.r > input[type=button]",
            "Training": "#list_form > table.list > tbody > tr:nth-child(11) > td.section.r > input[type=button]",
        }

        selector = button_mapping.get(type_text)

        if not selector:
            print(f"Certificate type tidak dikenali: {type_text}")
            return False
        
        print(f"Certificate type: {type_text}")

        self.page.locator(selector).click()
        self.page.wait_for_load_state("networkidle")
        self.page.locator("#cert_id").wait_for(state="visible", timeout=10000)

        return True
    
    def _normalize_certificate_type(self, text: str) -> str:
        return " ".join(unescape(text or "").strip().lower().split())
    
    def _get_select_options_cert(self, select_locator: str):
        select = self.page.locator(select_locator)
        option_locator = select.locator("option")

        options = []
        for i in range(option_locator.count()):
            opt = option_locator.nth(i)
            label = opt.inner_text().strip()
            value = opt.get_attribute("value")

            if value and value != "0" and label:
                options.append({
                    "label": label,
                    "value": value
                })

        return options

    def select_certificate_with_fallback(
        self,
        cert_name: str,
        select_locator: str,
        mapping: dict | None = None,
        threshold: float = 0.7
    ) -> bool:
        """
        Return:
            True  -> berhasil pilih option
            False -> tidak ada yang cocok, skip
        """
        select = self.page.locator(select_locator)
        cert_name_n = self._normalize_certificate_type(cert_name)

        # 1) exact mapping
        if mapping:
            mapped = mapping.get(cert_name_n)
            if mapped:
                try:
                    select.select_option(label=mapped)
                    print(f"[MAPPING] {cert_name} -> {mapped}")
                    return True
                except Exception:
                    pass

        # 2) fuzzy
        options = self._get_select_options_cert(select_locator)
        labels = [x["label"] for x in options]

        if labels:
            best_label, best_score = self._best_fuzzy_cert(cert_name, labels)

            if best_label:
                print(
                    f"[FUZZY] {cert_name} -> {best_label} "
                    f"({best_score:.2f})"
                )

                if best_score >= threshold:
                    select.select_option(label=best_label)
                    return True

        # 3) skip
        print(f"[SKIP] cert_id tidak cocok untuk: {cert_name}")
        return False
    
    def _best_fuzzy_cert(self, target: str, options: list[str]):
        target_n = self._normalize_certificate_type(target)

        best_label = None
        best_score = 0.0

        for option in options:
            score = SequenceMatcher(
                None,
                target_n,
                self._normalize_certificate_type(option)
            ).ratio()

            if score > best_score:
                best_score = score
                best_label = option

        return best_label, best_score
    
    def select_certificate_name(
        self,
        type_text: str,
        cert_name: str
    ):
        mapping = CERTIFICATE_MAPPINGS.get(
            type_text,
            {}
        )

        select_locator = CERT_ID_LOCATORS.get(
            type_text
        )

        if not select_locator:
            print(
                f"Cert locator tidak ditemukan untuk {type_text}"
            )
            return False

        self.select_certificate_with_fallback(
            cert_name=cert_name,
            select_locator=select_locator,
            mapping=mapping
        )

        return True
        
    def fill_certificate_fields(
        self,
        cert: dict,
        type_text: str
    ):
        fields = CERT_FIELD_MAPPING.get(type_text)

        if not fields:
            print(f"Field mapping belum ada untuk {type_text}")
            return

        country = cert.get("issue_country")
        if country and fields.get("country"):
            self.page.locator(
                fields["country"]
            ).fill(country)

        issuer = cert.get("issuer")
        if issuer and fields.get("issuer"):
            self.page.locator(
                fields["issuer"]
            ).fill(issuer)

        issued = cert.get("issued")
        if issued and fields.get("issued"):
            self.page.locator(
                fields["issued"]
            ).fill(issued)

        expires = cert.get("expires")
        if expires and fields.get("expires"):
            self.page.locator(
                fields["expires"]
            ).fill(expires)

        number = cert.get("number")
        if number and fields.get("number"):
            self.page.locator(
                fields["number"]
            ).fill(str(number))

        notes = cert.get("notes")
        if notes and fields.get("notes"):
            self.page.locator(
                fields["notes"]
            ).fill(notes)
    
    def fill_certificate(self, cert: dict):

        type_text = cert.get("type_text", "")
        name_text = cert.get("name_text", "")

        # buka form sesuai kategori
        if not self.select_certificate_type(type_text):
            return

        # pilih cert_id sesuai kategori
        self.select_certificate_name(
            type_text=type_text,
            cert_name=name_text
        )

        self.fill_certificate_fields(
            cert,
            type_text
        )
        
    def save_certificate(
        self,
        type_text: str
    ) -> bool:

        selector = SAVE_MAPPING.get(type_text)

        if not selector:
            print(
                f"Save button tidak ditemukan untuk {type_text}"
            )
            return False

        button = self.page.locator(selector)

        button.wait_for(
            state="visible",
            timeout=10000
        )

        button.click()

        return True