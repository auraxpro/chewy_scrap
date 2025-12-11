import sys
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db
from app.scraper.chewy_scraper import ChewyScraperUCD


def main():
    print("Initializing database...")
    init_db()

    scraper = None
    try:
        scraper = ChewyScraperUCD()

        # Check for product detail scraping mode
        if "--details" in sys.argv or "-d" in sys.argv:
            # Product detail scraping mode
            print("\nStarting Chewy.com product detail scraper...")

            # Check for test mode with product URL
            test_url = None
            for i, arg in enumerate(sys.argv):
                if arg in ["--test-url", "-tu"] and i + 1 < len(sys.argv):
                    test_url = sys.argv[i + 1]
                    break

            if test_url:
                print(f"Running in TEST MODE - scraping product: {test_url}")
                scraper.scrape_product_by_url(test_url)
            else:
                # Scrape all unscraped products
                limit = None
                offset = None
                for i, arg in enumerate(sys.argv):
                    if arg in ["--limit", "-l"] and i + 1 < len(sys.argv):
                        try:
                            limit = int(sys.argv[i + 1])
                        except ValueError:
                            print(f"⚠️  Invalid limit value: {sys.argv[i + 1]}")
                    elif arg in ["--offset", "-o"] and i + 1 < len(sys.argv):
                        try:
                            offset = int(sys.argv[i + 1])
                        except ValueError:
                            print(f"⚠️  Invalid offset value: {sys.argv[i + 1]}")

                if offset is not None:
                    print(f"📍 Starting from offset: {offset}")
                if limit:
                    print(f"📊 Limiting to: {limit} products")

                scraper.scrape_all_product_details(limit=limit, offset=offset)

        else:
            # Product list scraping mode (default)
            print("\nStarting Chewy.com product list scraper...")

            # Check for test mode (scrape only first page)
            test_mode = "--test" in sys.argv or "-t" in sys.argv

            if test_mode:
                print("Running in TEST MODE - scraping only page 1")
                scraper.scrape_all(start=1, end=1)
            else:
                # Scrape all pages (1 to 138)
                scraper.scrape_all(start=1, end=138)

        print("\nScraping completed!")
    finally:
        if scraper:
            print("Closing browser...")
            scraper.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
