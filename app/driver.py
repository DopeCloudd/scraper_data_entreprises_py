import undetected_chromedriver as uc


class Driver:
    """
    Singleton driver Selenium avec undetected_chromedriver.
    """
    def __init__(self, headless: bool = True):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = uc.Chrome(use_subprocess=False, version_main=137, options=options)

    def get(self, url: str):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()
