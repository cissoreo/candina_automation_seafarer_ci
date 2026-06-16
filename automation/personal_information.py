from difflib import SequenceMatcher
from playwright.sync_api import Page

from app import log_msg
from automation.map_rank import RANK_MAPPING


class PersonalInformationPage:
    def __init__(self, page: Page):
        self.page = page

    def open_new_seafarer(self):
        self.page.locator(
            "xpath=/html/body/table/tbody/tr[2]/td[1]/div[2]/div[1]"
        ).click()
        self.page.wait_for_load_state("networkidle")

        # self.page.locator("input.button-1[value='New']").click()
        # self.page.wait_for_load_state("networkidle")

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

        select = self.page.locator("#rank_id") or self.page.locator("#search_rank_id")

        options = select.locator("option")

        available_options = []

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
            
            
    def fill_search(self, data: dict):

        # ======================
        # Personal Information
        # ======================

        surname = data.get("surname")
        if surname and len(surname) > 1:
            self.page.locator("#search_surname").fill(surname)

        name = data.get("name")
        if name and len(name) > 1:
            self.page.locator("#name").fill(name)

        dob = data.get("date_of_birth")
        if dob:
            self.page.locator("#f_from_date").fill(dob)

        phone = data.get("phone")
        mobile = data.get("mobile")
        email = data.get("email")
        
        if email:
            self.page.locator("#searchForm > table > tbody > tr:nth-child(17) > td > input").fill(email) 
            return
        if phone:
            self.page.locator("#searchForm > table > tbody > tr:nth-child(17) > td > input").fill(phone)
            return
        if mobile:
            self.page.locator("#searchForm > table > tbody > tr:nth-child(17) > td > input").fill(mobile)
            return

        
    
    def fill_personal_information(self, data: dict):
        # ======================
        # Rank
        # ======================
        rank_text = data.get("rank_text", "")
        self.select_rank(rank_text)

        # ======================
        # Personal Information
        # ======================

        surname = data.get("surname")
        if surname:
            self.page.locator("#surname").fill(surname)

        name = data.get("name")
        if name:
            self.page.locator("#name").fill(name)

        dob = data.get("date_of_birth")
        if dob:
            self.page.locator("#pp_dob").fill(dob)

        nationality = data.get("nationality")
        if nationality:
            self.page.locator("#country_code").fill(nationality)

        phone = data.get("phone")
        if phone:
            self.page.locator("#address_phone").fill(phone)

        mobile = data.get("mobile")
        if mobile:
            self.page.locator("#address_fax").fill(mobile)

        email = data.get("email")
        if email:
            self.page.locator("#address_email").fill(email)

        # ======================
        # Status
        # ======================

        self.page.locator("#status").select_option(value="10")
        
        return surname if surname else name
        
        
    def search_existing_seafarer(self, data: dict) -> bool:
        self.fill_search(data)

        self.page.locator(
            "#searchForm > table > tbody > tr:nth-child(18) > td > input.button-1"
        ).click()

        try:
            self.page.locator(
                "#big > table > tbody > tr:nth-child(3) > a"
            ).wait_for(
                state="visible",
                timeout=5000
            )

            print("Data ditemukan")
            return True

        except:
            print("Data tidak ditemukan")
            return False
        #big > table > tbody > tr:nth-child(3) > td:nth-child(3) > a

        if result_row.count() > 0:
            try:
                seafarer_link = self.page.locator(
                    "#big table tbody tr:nth-child(3) td:nth-child(3) a"
                )

                seafarer_link.wait_for(
                    state="visible",
                    timeout=3000
                )

                seafarer_link.first.click()

                self.page.wait_for_load_state("networkidle")

                return True

            except TimeoutError:
                return False

        return False