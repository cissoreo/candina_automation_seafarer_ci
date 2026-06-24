
from turtle import st

from playwright.sync_api import sync_playwright
import os

from automation.login import LoginPage
from automation.personal_information import PersonalInformationPage
from automation.sea_service import SeaServicePage
import tkinter as tk

from template.errors import IsExists


class PlayWright():
    
    
    def playwright_main(data, p):
        USERNAME = os.getenv("CI_USERNAME", "")
        PASSWORD = os.getenv("CI_PASSWORD", "")
        
        name = None
        status_progress = None
        seafarer_id = None
        
        browser = p.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()

        # LOGIN
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(USERNAME, PASSWORD)
        login_page.handle_previous_session()
        
        # PERSONAL INFORMATION
        personal_info = PersonalInformationPage(page)
        
        # CEK DATA IS EXIST     
        personal_info.open_new_seafarer()

        is_exist = personal_info.search_existing_seafarer(
            data.get("personal_information", {})
        )

        # IF EXIST: TEMPORARY SKIPPED
        try:
            if is_exist:
                raise IsExists("Seafarer already exists")
                # status_progress = "is_exist"
                # return browser, name, status_progress
                
                
                # print("Update existing seafarer")
                
                # personal_info.fill_personal_information(data.get("personal_information", ""))
                
                # page.locator("#save_row > input.button-1").click()
                # self.page.wait_for_load_state("networkidle")
                
                # click SeaService
                # page.locator("#small > table > tbody > tr:nth-child(4) > td > input").click()
                

            # IF NOT EXIST
            else:
                print("Create new seafarer")
                
                page.locator("#big > table > tbody > tr:nth-child(1) > td > input").click()
                page.wait_for_load_state("networkidle")
                name = personal_info.fill_personal_information(
                    data.get("personal_information", {})
                )
                
                # click save
                page.locator("#save_row > input.button-1").click()
                page.wait_for_load_state("networkidle")
                
                # click sea service / experience
                page.locator("#small > table > tbody > tr:nth-child(4) > td > input").click()
                page.wait_for_load_state("networkidle")

                sea_service = SeaServicePage(page)

                for exp in data.get("experiences", []):
                    # click new entry
                    page.locator("#list_form > table > tbody > tr:nth-child(1) > td:nth-child(2) > input[type=button]").click()
                    page.wait_for_load_state("networkidle")

                    sea_service.fill_experience(exp)

                    # Save Sea Service
                    save_btn = page.locator("#save_button")
                    save_btn.click()

                    # Tunggu tombol bisa diklik lagi
                    save_btn.wait_for(state="visible")
                    page.wait_for_timeout(3000)
                    
                    
                # click certs
                page.locator("#small > table > tbody > tr:nth-child(7) > td > input").click()
                page.wait_for_load_state("networkidle")
                
                certificate_page = SeaServicePage(page)
                for cert in data.get("certificates", []):
                    type_text = cert.get("type_text")

                    success = certificate_page.select_certificate_type(
                        type_text
                    )

                    if not success:
                        continue
                    
                    certificate_page.fill_certificate(cert)
                    certificate_page.save_certificate(type_text)
                    page.wait_for_load_state("networkidle")
                    
                status_progress = "added"
                    
                # kembali ke menu utama
                page.locator(
                    "#small > table > tbody > tr:nth-child(2) > td > input"
                ).click()

                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                
                # ambil id
                seafarer_id = page.locator(
                    "#big > table:nth-child(14) > tbody > tr:nth-child(2) > td:nth-child(2)"
                ).inner_text().strip()
            
            
            return browser, name, status_progress, seafarer_id
        except Exception as e:
            # kembali ke menu utama
            page.locator(
                "#small > table > tbody > tr:nth-child(2) > td > input"
            ).click()

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            # ambil seafarer_id
            seafarer_id = page.locator(
                "#big > table:nth-child(14) > tbody > tr:nth-child(3) > td:nth-child(2)"
            ).inner_text().strip()

            status_progress = "added_with_errors"

            return browser, name, status_progress, seafarer_id
    