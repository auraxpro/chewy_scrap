import asyncio
import sys
from database import init_db
from scraper import ChewyScraperUCD

def main():
    print("Initializing database...")
    init_db()
    
    print("\nStarting Chewy.com product scraper...")
    scraper = None
    try:
        scraper = ChewyScraperUCD()
        
        # Check for test mode (scrape only first page)
        test_mode = '--test' in sys.argv or '-t' in sys.argv
        
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

