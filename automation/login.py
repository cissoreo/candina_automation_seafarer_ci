from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto(
            "https://candina.crewinspector.com/login",
            wait_until="networkidle"
        )

    def login(self, username: str, password: str):
        self.page.locator("input[name='login']").fill(username)
        self.page.locator("input[name='password']").fill(password)
        self.page.locator("#login_table > input").click()

        self.page.wait_for_load_state("networkidle")
        
    def handle_previous_session(self):
        while True:
            disconnect_btn = self.page.locator(
                "input[value='Disconnect previous login']"
            )

            if not disconnect_btn.is_visible():
                print("No previous session found.")
                break

            print("Previous session detected. Disconnecting...")

            disconnect_btn.click()

            self.page.wait_for_load_state("networkidle")