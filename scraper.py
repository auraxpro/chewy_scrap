from pickle import FALSE
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from database import SessionLocal, ProductList, ProductDetails
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
            for _ in range(random.randint(1, 3)):
                self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(250, 450))
                time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            print(f"⚠️  Error in scrolling: {e}")
            # Don't fail completely, just skip scrolling

    # ----------------------------------------
    # ⭐ Load a Chewy page with retries
    # ----------------------------------------
    def load_page(self, url: str):
        try:
            # Ensure driver and window are valid before proceeding
            self._ensure_window()
            
            # Switch to the first window if multiple exist
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            self.driver.get(url)
            
            # ------------------------------
            # Wait for initial network activity
            # ------------------------------
            time.sleep(random.uniform(1.0, 1.5))
                            
            # ------------------------------
            # Wait for body to appear
            # ------------------------------
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.find_element(By.TAG_NAME, "body")
                )
            except Exception as e:
                print(f"❌ ERROR: Page not loaded properly: {e}")
                return None
            
            # ------------------------------
            # Wait for JS DOM readiness
            # ------------------------------
            try:
                WebDriverWait(self.driver, 12).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception:
                # Don't fail completely if readyState check times out
                pass
            
            # Verify page loaded successfully
            if not self._is_driver_alive():
                raise NoSuchWindowException("Window closed after page load")
            
            # ------------------------------
            # Scroll to trigger lazy-loaded content
            # ------------------------------
            self.slow_scroll()
            # time.sleep(random.uniform(1.0, 1.8))
            
            # Check again before getting page source
            if not self._is_driver_alive():
                raise NoSuchWindowException("Window closed during interaction")
            
            html = self.driver.page_source
            
            # ------------------------------
            # Validate REAL Chewy product page
            # ------------------------------
            soup = BeautifulSoup(html, "html.parser")
            
            # Check for product page
            if soup.select_one("h1[data-testid='product-title-heading']"):
                print("✅ Product page loaded successfully.")
                return html
            
            # Check for category/listing page
            if soup.select_one(".kib-product-card"):
                print("✅ Category/listing page loaded successfully.")
                return html
            
            # If HTML is too short → likely blocked or incomplete
            if len(html) < 8000:
                print(f"⚠️ HTML too short ({len(html)} bytes) — retrying…")
                return None
            
            # If we got here and HTML is long enough, return it anyway
            # (might be a different page type we don't recognize)
            print("⚠️ Page loaded but structure not recognized — returning HTML anyway")
            return html
            
        except (NoSuchWindowException, WebDriverException) as e:
            error_msg = str(e).lower()
            if "no such window" in error_msg or "target window already closed" in error_msg or "web view not found" in error_msg:
                try:
                    self._init_driver()
                    time.sleep(3)  # Give browser time to fully initialize
                except Exception as init_error:
                    print(f"❌ Failed to reinitialize driver: {init_error}")
                    return None
        except Exception as e:
            print(f"❌ Unexpected error loading page: {e}")
        
        print("❌ FAILED to load page after 4 attempts")
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
    # ⭐ Extract all content
    # ----------------------------------------
    def extract_all_content(self, element):
        if element is None:
            return None
        
        result_lines = []

        # ===========================================================
        # 1. Extract ALL TABLES (preserve multi-column tables)
        # ===========================================================
        tables = element.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for tr in rows:
                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
                if cells:
                    result_lines.append(" | ".join(cells))
            result_lines.append("")  # blank line after each table

        # ===========================================================
        # 2. Extract ALL LISTS
        # ===========================================================
        for ul in element.find_all("ul"):
            for li in ul.find_all("li"):
                text = li.get_text(" ", strip=True)
                if text:
                    result_lines.append(f"- {text}")
            result_lines.append("")

        # ===========================================================
        # 3. Extract ALL PARAGRAPHS (including <strong> tags)
        # ===========================================================
        for p in element.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text:
                result_lines.append(text)
                result_lines.append("")

        # Cleanup multiple blank lines
        cleaned = "\n".join([line for line in result_lines if line.strip() != ""])

        return cleaned if cleaned else None

    # ----------------------------------------
    # ⭐ Extract Details Block (details, more_details, specifications)
    # ----------------------------------------
    def extract_details_block(self, soup):
        """
        Extracts:
          - details (benefits from first visible section)
          - more_details (description from hidden div middle sections)
          - specifications (table from hidden div last section)
        from the kib-truncation-content container.
        """
        out = {
            "details": None,
            "more_details": None,
            "specifications": None
        }

        # 1️⃣ Find the base container
        trunc = soup.select_one(".kib-truncation-content")
        if not trunc:
            return out

        # --------------------------------------------
        # 2️⃣ Extract DETAILS (from first <section>)
        # --------------------------------------------
        first_section = trunc.find("section", recursive=False)
        if first_section:
            out["details"] = self.extract_all_content(first_section)

        # --------------------------------------------
        # 3️⃣ Hidden block contains description + specs
        # --------------------------------------------
        hidden_div = None
        for child in trunc.find_all(recursive=False):
            if child.name == "div" and child.get("style", "").startswith("display:none"):
                hidden_div = child
                break

        if not hidden_div:
            return out

        # Extract ALL <section> items inside hidden div
        sections = hidden_div.find_all("section", recursive=False)
        if len(sections) == 0:
            return out

        # 🍖 First hidden section = duplicate KEY BENEFITS → ignore
        # 🧾 Last hidden section = SPECIFICATIONS → extract table
        # ✨ Middle sections = DESCRIPTION paragraphs

        # --------------------------------------------
        # 4️⃣ Extract SPECIFICATIONS (last section)
        # --------------------------------------------
        spec_section = sections[-1]
        out["specifications"] = self.extract_all_content(spec_section)

        # --------------------------------------------
        # 5️⃣ Extract MORE_DETAILS (middle sections)
        # --------------------------------------------
        middle_sections = sections[1:-1]   # exclude first (duplicate) & last (specs)
        if middle_sections:
            paras = []
            for sec in middle_sections:
                paras.append(self.extract_all_content(sec))
            out["more_details"] = "\n\n".join(paras)

        return out

    # ----------------------------------------
    # ⭐ Extract product details from HTML
    # ----------------------------------------
    def extract_product_details(self, html: str, product_url: str, img_link: str = None):
        soup = BeautifulSoup(html, "html.parser")

        out = {
            "product_url": product_url,
            "img_link": img_link,
            "product_name": None,
            "product_category": None,
            "price": None,
            "size": None,
            "details": None,               # KEY BENEFITS
            "more_details": None,          # DESCRIPTION + MULTI-PARAGRAPH TEXT
            "specifications": None,        # FULL TABLE
            "ingredients": None,
            "caloric_content": None,
            "guaranteed_analysis": None,
            "feeding_instructions": None,
            "transition_instructions": None
        }

        # ===========================================================
        # PRODUCT NAME (stable)
        # ===========================================================
        name = soup.select_one("h1[data-testid='product-title-heading']")
        if name:
            out["product_name"] = name.get_text(strip=True)
        # ===========================================================
        # CATEGORY (Breadcrumbs)
        # ===========================================================
        crumb = soup.select("ol.kib-breadcrumbs__list li a")
        if len(crumb) >= 3:
            out["product_category"] = crumb[2].get_text(strip=True)
        # ===========================================================
        # PRICE
        # ===========================================================
        dollars = soup.select_one(".kib-product-price__dollars")
        cents = soup.select_one(".kib-product-price__cents")
        if dollars and cents:
            out["price"] = f"${dollars.text.strip()}.{cents.text.strip()}"
        # ===========================================================
        # SIZE (stable swatch heading)
        # ===========================================================
        size = soup.select_one("h2.kib-swatch__heading strong")
        if size:
            out["size"] = size.get_text(strip=True)
        
        # ===========================================================
        # DETAILS BLOCK (details, more_details, specifications)
        # ===========================================================
        # Check if page loaded properly - verify key elements exist
        trunc_container = soup.select_one("div.kib-truncation-content")
        if not trunc_container:
            print(f"❌ ERROR: Page structure incomplete - missing kib-truncation-content")
            print(f"❌ ERROR: Page may not have loaded fully")
            return None
        
        # Extract details block using the new approach
        details_block = self.extract_details_block(soup)
        print(details_block)
        out["details"] = details_block["details"]
        out["more_details"] = details_block["more_details"]
        out["specifications"] = details_block["specifications"]
        
        # Verify we got at least some data (if page loaded, we should have details)
        if not details_block["details"]:
            print(f"❌ ERROR: No details extracted - page may be incomplete")
            return None
        
        # ===========================================================
        # INGREDIENTS
        # ===========================================================
        ing_section = soup.select_one("#INGREDIENTS-section")
        if ing_section:
            ing = self.extract_all_content(ing_section)
            if ing:
                out["ingredients"] = ing
        # ===========================================================
        # CALORIC CONTENT
        # ===========================================================
        cal_section = soup.select_one("#CALORIC_CONTENT-section")
        if cal_section:
            cal = self.extract_all_content(cal_section)
            if cal:
                out["caloric_content"] = cal
        # ===========================================================
        # GUARANTEED ANALYSIS
        # ===========================================================
        ga_section = soup.select_one("#GUARANTEED_ANALYSIS-section")
        if ga_section:
            ga = self.extract_all_content(ga_section)
            if ga:
                out["guaranteed_analysis"] = ga
        # ===========================================================
        # FEEDING INSTRUCTIONS
        # ===========================================================
        feed_section = soup.select_one("#FEEDING_INSTRUCTIONS-section")
        if feed_section:
            feed = self.extract_all_content(feed_section)
            if feed:
                out["feeding_instructions"] = feed
        # ===========================================================
        # TRANSITION INSTRUCTIONS
        # ===========================================================
        trans_section = soup.select_one("#TRANSITION_INSTRUCTIONS-section")
        if trans_section:
            trans = self.extract_all_content(trans_section)
            if trans:
                out["transition_instructions"] = trans

        return out

    
    # ----------------------------------------
    # ⭐ Scrape product details from a product URL
    # ----------------------------------------
    def scrape_product_details(self, product_url: str, img_link: str = None):
        """Scrape detailed product information from a product page"""
        print(f"\n📦 Scraping product details: {product_url}")
        
        html = self.load_page(product_url)
        if not html:
            print(f"❌ ERROR: Failed to load product page: {product_url}")
            print(f"❌ ERROR: Page load failed - incomplete or blocked page")
            return None
        # Reload HTML after scrolling
        html = self.driver.page_source
        
        details = self.extract_product_details(html, product_url, img_link)
        return details
    
    # ----------------------------------------
    # ⭐ Save product details to database and update scraped flag
    # ----------------------------------------
    def save_product_details(self, product_id: int, details: dict):
        """Save product details to database and update scraped flag"""
        db = SessionLocal()
        try:
            # Get the product
            product = db.query(ProductList).filter_by(id=product_id).first()
            if not product:
                print(f"❌ Product with id {product_id} not found")
                return False
            
            # Check if details already exist
            existing_details = db.query(ProductDetails).filter_by(product_id=product_id).first()
            
            if existing_details:
                # Update existing details
                for key, value in details.items():
                    if hasattr(existing_details, key):
                        setattr(existing_details, key, value)
            else:
                # Create new details
                product_details = ProductDetails(
                    product_id=product_id,
                    **details
                )
                db.add(product_details)
            
            # Update scraped flag
            product.scraped = True
            
            db.commit()
            print(f"✅ Saved product details for: {details.get('product_name', 'Unknown')}")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving product details: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    # ----------------------------------------
    # ⭐ Mark product as skipped
    # ----------------------------------------
    def mark_product_as_skipped(self, product_id: int):
        """Mark a product as skipped when details cannot be extracted"""
        db = SessionLocal()
        try:
            # Get the product
            product = db.query(ProductList).filter_by(id=product_id).first()
            if not product:
                print(f"❌ Product with id {product_id} not found")
                return False
            
            # Mark as skipped
            product.skipped = True
            db.commit()
            print(f"✅ Marked product {product_id} as skipped")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error marking product as skipped: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    # ----------------------------------------
    # ⭐ Scrape product details by URL (test mode)
    # ----------------------------------------
    def scrape_product_by_url(self, product_url: str, img_link: str = None):
        """Scrape a single product by URL (for testing) - prints results only, does not save to database"""
        details = self.scrape_product_details(product_url, img_link)
        if details:
            print("\n📊 Scraped Product Details (TEST MODE - Not Saved):")
            print("=" * 50)
            for key, value in details.items():
                if value:
                    # Print full value for test mode, truncate only very long values
                    display_value = value
                    print(f"{key}: {display_value}")
            print("=" * 50)
            print("ℹ️  TEST MODE: Data not saved to database")
        else:
            print("❌ Failed to scrape product: KEY_BENEFITS-section not found")
        
        return details
    
    # ----------------------------------------
    # ⭐ Scrape all unscraped products
    # ----------------------------------------
    def scrape_all_product_details(self, limit: int = None, offset: int = None):
        """Scrape details for all products that haven't been scraped yet"""
        db = SessionLocal()
        try:
            # Get all unscraped products (exclude skipped products)
            query = db.query(ProductList).filter_by(scraped=False, skipped=False).order_by(ProductList.id)
            if offset is not None:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            unscraped_products = query.all()
            
            total = len(unscraped_products)
            print(f"\n📦 Found {total} unscraped products")
            
            if total == 0:
                print("✅ All products have been scraped!")
                return
            
            success_count = 0
            fail_count = 0
            
            for idx, product in enumerate(unscraped_products, 1):
                print(f"\n[{idx}/{total}] Processing: {product.product_url}")
                
                try:
                    details = self.scrape_product_details(
                        product.product_url,
                        product.product_image_url
                    )
                    
                    if details:
                        if self.save_product_details(product.id, details):
                            success_count += 1
                        else:
                            fail_count += 1
                    else:
                        # If details is None, mark product as skipped and continue
                        print(f"⚠️ No details extracted for product: {product.product_url} - marking as skipped")
                        self.mark_product_as_skipped(product.id)
                        fail_count += 1
                        # Continue to next product instead of stopping
                    
                    # Random delay between products
                    time.sleep(random.uniform(2.0, 4.0))
                    
                except Exception as e:
                    fail_count += 1
                    print(f"❌ Error scraping product {product.id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n✅ Scraping completed!")
            print(f"   Success: {success_count}")
            print(f"   Failed: {fail_count}")
            
        except Exception as e:
            print(f"❌ Error in scrape_all_product_details: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()

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
