import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from bs4 import BeautifulSoup
from database import SessionLocal, ProductList
from sqlalchemy.exc import IntegrityError
import ssl, certifi
ssl._create_default_https_context = lambda *args, **kwargs: ssl.create_default_context(cafile=certifi.where())


BASE_URL = "https://www.chewy.com/b/food-332"
PAGE_URL_TEMPLATE = "https://www.chewy.com/b/food_c332_p{page}"

class ChewyScraperUCD:
    def __init__(self):
        self.driver = None
        self._init_driver()
        
    def _init_driver(self):
        """Initialize or reinitialize the Chrome driver"""
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
        except:
            pass
            
        chrome_opts = uc.ChromeOptions()
        # Basic options that are safe and compatible with undetected_chromedriver
        chrome_opts.add_argument("--start-maximized")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        
        # Note: undetected_chromedriver already handles stealth features internally,
        # so we don't need to add excludeSwitches or useAutomationExtension

        # 🚀 Launch REAL Chrome
        self.driver = uc.Chrome(options=chrome_opts)
        # Ensure we have at least one window
        if len(self.driver.window_handles) == 0:
            raise Exception("Failed to create browser window")
        
    def _is_driver_alive(self):
        """Check if driver and window are still valid"""
        try:
            if self.driver is None:
                return False
            # Try to get window handles - this will fail if driver is dead
            handles = self.driver.window_handles
            return len(handles) > 0
        except (WebDriverException, NoSuchWindowException, AttributeError):
            return False
    
    def _ensure_window(self):
        """Ensure we have a valid window, recreate driver if needed"""
        if not self._is_driver_alive():
            print("⚠️  Browser window closed unexpectedly, reinitializing...")
            self._init_driver()
            time.sleep(2)
        
    # ----------------------------------------
    # ⭐ Human-like random mouse movement
    # ----------------------------------------
    def human_mouse_move(self):
        try:
            self._ensure_window()
            actions = ActionChains(self.driver)
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")

            for _ in range(random.randint(3, 6)):
                x = random.randint(0, width - 10)
                y = random.randint(0, height - 10)
                actions.move_to_element_with_offset(
                    self.driver.find_element(By.TAG_NAME, "body"),
                    x, y
                ).perform()
                time.sleep(random.uniform(0.2, 0.4))
        except Exception as e:
            print(f"⚠️  Error in mouse movement: {e}")
            # Don't fail completely, just skip mouse movement


    # ----------------------------------------
    # ⭐ Slow human-like scrolling
    # ----------------------------------------
    def slow_scroll(self):
        try:
            self._ensure_window()
            for _ in range(random.randint(6, 10)):
                self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(250, 450))
                time.sleep(random.uniform(0.3, 0.7))
        except Exception as e:
            print(f"⚠️  Error in scrolling: {e}")
            # Don't fail completely, just skip scrolling

    # ----------------------------------------
    # ⭐ Load a Chewy page with retries
    # ----------------------------------------
    def load_page(self, url: str):
        for attempt in range(3):
            try:
                print(f"Loading page: {url} (attempt {attempt+1})")
                
                # Ensure driver and window are valid before proceeding
                self._ensure_window()
                
                # Switch to the first window if multiple exist
                if len(self.driver.window_handles) > 0:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                
                self.driver.get(url)
                time.sleep(random.uniform(2.5, 4.0))

                # Verify page loaded successfully
                if not self._is_driver_alive():
                    raise NoSuchWindowException("Window closed after page load")

                # self.human_mouse_move()
                # self.slow_scroll()

                # Check again before getting page source
                if not self._is_driver_alive():
                    raise NoSuchWindowException("Window closed during interaction")

                html = self.driver.page_source
                # print(html)

                # Detect Akamai block
                # if "captcha" in html.lower() or len(html) < 5000:
                #     print("⚠ Blocked or incomplete page — retrying…")
                #     time.sleep(2)
                #     continue

                return html

            except (NoSuchWindowException, WebDriverException) as e:
                error_msg = str(e).lower()
                if "no such window" in error_msg or "target window already closed" in error_msg or "web view not found" in error_msg:
                    print(f"⚠️  Browser window closed (attempt {attempt+1}/3), reinitializing...")
                    # Reinitialize driver for next attempt
                    try:
                        self._init_driver()
                        time.sleep(3)  # Give browser time to fully initialize
                    except Exception as init_error:
                        print(f"❌ Failed to reinitialize driver: {init_error}")
                        if attempt == 2:  # Last attempt
                            return None
                else:
                    print(f"Error loading page: {e}")
                    if attempt < 2:
                        time.sleep(2)
            except Exception as e:
                print(f"Unexpected error loading page: {e}")
                if attempt < 2:
                    time.sleep(2)

        print("❌ FAILED to load page after retries")
        return None

    # ----------------------------------------
    # ⭐ Extract product cards using BeautifulSoup
    # ----------------------------------------
    def extract_products(self, html: str, page_num: int):
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".kib-product-card")

        print(f"Found {len(cards)} products on page {page_num}")

        products = []

        for c in cards:
            title = c.select_one(".kib-product-title")
            if not title:
                continue

            link = title.get("href") or ""
            if link.startswith("/"):
                link = "https://www.chewy.com" + link

            if "/dp/" not in link and "/p/" not in link:
                continue

            img_el = c.select_one(".kib-product-image img")
            image_url = img_el.get("src") if img_el else None

            products.append({
                "product_url": link,
                "page": page_num,
                "image_url": image_url
            })

        return products

    # ----------------------------------------
    # ⭐ Scrape a single page
    # ----------------------------------------
    def scrape_page(self, page_num: int):
        url = BASE_URL if page_num == 1 else PAGE_URL_TEMPLATE.format(page=page_num)
        html = self.load_page(url)

        if not html:
            return []

        return self.extract_products(html, page_num)

    # ----------------------------------------
    # ⭐ Save products to database
    # ----------------------------------------
    def save_products_to_db(self, products: list):
        """Save products to database, skipping duplicates"""
        if not products:
            return 0
        
        db = SessionLocal()
        saved_count = 0
        skipped_count = 0
        
        try:
            for product_data in products:
                try:
                    # Check if product already exists
                    existing = db.query(ProductList).filter_by(product_url=product_data["product_url"]).first()
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new product
                    product = ProductList(
                        product_url=product_data["product_url"],
                        page_num=product_data["page"],
                        product_image_url=product_data.get("image_url"),
                        scraped=False
                    )
                    db.add(product)
                    saved_count += 1
                except IntegrityError:
                    # Handle race condition where product was added between check and insert
                    db.rollback()
                    skipped_count += 1
                    continue
            
            db.commit()
            print(f"✅ Saved {saved_count} products to database (skipped {skipped_count} duplicates)")
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving products to database: {e}")
        finally:
            db.close()
        
        return saved_count

    # ----------------------------------------
    # ⭐ Scrape all pages
    # ----------------------------------------
    def scrape_all(self, start=1, end=5):
        all_products = []

        for page_num in range(start, end + 1):
            print(f"\n--- Scraping page {page_num} ---")
            products = self.scrape_page(page_num)
            
            if products:
                # Save products to database immediately after scraping each page
                self.save_products_to_db(products)
                all_products.extend(products)
            else:
                print(f"⚠️  No products found on page {page_num}")
            
            time.sleep(random.uniform(1.5, 2.5))

        print(f"\n✅ Total products scraped: {len(all_products)}")
        return all_products

    # ----------------------------------------
    # ⭐ Cleanup
    # ----------------------------------------
    def close(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        finally:
            self.driver = None


# ----------------------------------------
# ⭐ Run the scraper
# ----------------------------------------
if __name__ == "__main__":
    scraper = ChewyScraperUCD()
    products = scraper.scrape_all(start=1, end=1)  # test page 1 only
    scraper.close()

    for p in products:
        print(p)
