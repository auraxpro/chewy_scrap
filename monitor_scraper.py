#!/usr/bin/env python3
"""
Scraper Monitor and Auto-Restart Script

This script monitors the scraper output in real-time and automatically
restarts it when timeout errors are detected.

Usage:
    python monitor_scraper.py [scraper arguments]
    
Examples:
    python monitor_scraper.py --details
    python monitor_scraper.py --details --limit 100
    python monitor_scraper.py --details --test-url "https://..."
"""

import subprocess
import sys
import time
import signal
import os
from datetime import datetime
from typing import Optional

# Configuration
MAX_RESTARTS = 200  # Maximum number of automatic restarts
RESTART_COOLDOWN = 50  # Seconds to wait before restarting
TIMEOUT_ERROR_KEYWORDS = [
    "timeout: Timed out receiving message from renderer",
    "timeout: Timed out",
    "Message: timeout",
    "Timed out receiving message",
]

# Errors that indicate incomplete page loads or blocking
INCOMPLETE_PAGE_ERROR_KEYWORDS = [
    "ERROR: Failed to load product page",
    "ERROR: Page load failed",
    "ERROR: Page structure incomplete",
    "ERROR: No details extracted",
    "ERROR: Page may not have loaded fully",
    "ERROR: Page structure may be missing",
    "FAILED to load page after retries",
    "Page content too short",
    "Page blocked after all retries",
    "Incomplete page detected",
]

class ScraperMonitor:
    def __init__(self, scraper_args: list, max_restarts: int = MAX_RESTARTS, cooldown: int = RESTART_COOLDOWN):
        self.scraper_args = scraper_args
        self.max_restarts = max_restarts
        self.cooldown = cooldown
        self.restart_count = 0
        self.process: Optional[subprocess.Popen] = None
        self.start_time = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "WARN": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "RESTART": "🔄"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}", flush=True)
    
    def detect_timeout_error(self, line: str) -> bool:
        """Check if the line contains a timeout error"""
        line_lower = line.lower()
        for keyword in TIMEOUT_ERROR_KEYWORDS:
            if keyword.lower() in line_lower:
                return True
        return False
    
    def detect_incomplete_page_error(self, line: str) -> bool:
        """Check if the line indicates an incomplete page load or blocking"""
        line_lower = line.lower()
        for keyword in INCOMPLETE_PAGE_ERROR_KEYWORDS:
            if keyword.lower() in line_lower:
                return True
        return False
    
    def kill_process(self):
        """Kill the scraper process and all its children"""
        if self.process:
            try:
                # Try graceful termination first
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.log("Process didn't terminate gracefully, forcing kill...", "WARN")
                    self.process.kill()
                    self.process.wait()
            except Exception as e:
                self.log(f"Error killing process: {e}", "ERROR")
            finally:
                self.process = None
    
    def run_scraper(self) -> int:
        """Run the scraper and monitor its output"""
        # Build command
        cmd = [sys.executable, "main.py"] + self.scraper_args
        
        self.log(f"Starting scraper: {' '.join(cmd)}")
        self.start_time = time.time()
        
        try:
            # Start process with unbuffered output
            # Create new process group (Unix) or use CREATE_NEW_PROCESS_GROUP (Windows)
            popen_kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'universal_newlines': True,
                'bufsize': 1,  # Line buffered
            }
            
            if sys.platform == 'win32':
                popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                popen_kwargs['preexec_fn'] = os.setsid
            
            self.process = subprocess.Popen(cmd, **popen_kwargs)
            
            # Monitor output line by line
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                
                # Print the line (pass through to console)
                print(line.rstrip(), flush=True)
                
                # Check for timeout errors
                if self.detect_timeout_error(line):
                    self.log(f"Timeout error detected: {line.strip()}", "ERROR")
                    return 1  # Signal restart needed
                
                # Check for incomplete page load errors
                if self.detect_incomplete_page_error(line):
                    self.log(f"Incomplete page error detected: {line.strip()}", "ERROR")
                    return 1  # Signal restart needed
            
            # Wait for process to complete
            return_code = self.process.wait()
            self.process = None
            
            if return_code == 0:
                elapsed = time.time() - self.start_time
                self.log(f"Scraper completed successfully in {elapsed:.1f} seconds", "SUCCESS")
                return 0
            else:
                self.log(f"Scraper exited with code {return_code}", "WARN")
                return return_code
                
        except KeyboardInterrupt:
            self.log("Interrupted by user", "WARN")
            self.kill_process()
            return 130  # Standard exit code for SIGINT
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self.kill_process()
            return 1
    
    def run(self):
        """Main monitoring loop with auto-restart"""
        self.log("=" * 60)
        self.log("Scraper Monitor Started")
        self.log("=" * 60)
        
        while True:
            # Run scraper
            return_code = self.run_scraper()
            
            # If successful or user interrupted, exit
            if return_code == 0:
                self.log("Scraping completed successfully!", "SUCCESS")
                break
            elif return_code == 130:  # KeyboardInterrupt
                self.log("Scraping interrupted by user", "WARN")
                break
            
            # Check if we've exceeded max restarts
            if self.restart_count >= self.max_restarts:
                self.log(f"Maximum restart limit ({self.max_restarts}) reached. Stopping.", "ERROR")
                sys.exit(1)
            
            # Increment restart counter
            self.restart_count += 1
            
            # Log restart
            self.log(f"Restarting scraper (attempt {self.restart_count}/{self.max_restarts})...", "RESTART")
            self.log(f"Waiting {self.cooldown} seconds before restart...", "INFO")
            time.sleep(self.cooldown)
            
            self.log("-" * 60)

def main():
    """Main entry point"""
    # Get scraper arguments (everything after script name)
    scraper_args = sys.argv[1:]
    
    # Parse monitor-specific arguments
    max_restarts = MAX_RESTARTS
    cooldown = RESTART_COOLDOWN
    
    if '--max-restarts' in sys.argv:
        idx = sys.argv.index('--max-restarts')
        try:
            max_restarts = int(sys.argv[idx + 1])
            scraper_args = [arg for arg in scraper_args if arg != '--max-restarts' and arg != sys.argv[idx + 1]]
        except (ValueError, IndexError):
            print("Error: --max-restarts requires an integer argument")
            sys.exit(1)
    
    if '--cooldown' in sys.argv:
        idx = sys.argv.index('--cooldown')
        try:
            cooldown = int(sys.argv[idx + 1])
            scraper_args = [arg for arg in scraper_args if arg != '--cooldown' and arg != sys.argv[idx + 1]]
        except (ValueError, IndexError):
            print("Error: --cooldown requires an integer argument")
            sys.exit(1)
    
    # Handle help
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nMonitor Options:")
        print("  --max-restarts N    Maximum number of automatic restarts (default: 10)")
        print("  --cooldown N        Seconds to wait before restarting (default: 5)")
        print("\nScraper Options:")
        print("  --details, -d        Scrape product details")
        print("  --test-url URL, -tu URL  Test mode with specific URL")
        print("  --limit N, -l N     Limit number of products to scrape")
        print("  --test, -t          Test mode (scrape only first page)")
        sys.exit(0)
    
    # Create and run monitor
    monitor = ScraperMonitor(scraper_args, max_restarts=max_restarts, cooldown=cooldown)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        monitor.log("Monitor interrupted by user", "WARN")
        monitor.kill_process()
        sys.exit(130)

if __name__ == "__main__":
    main()

