"""
Browser Automation Module - Controls browser to play videos, click buttons, etc.
"""
import time
from typing import Dict, Optional

class BrowserAutomation:
    """Automates browser actions using Selenium"""
    
    def __init__(self):
        self.driver = None
    
    def _init_driver(self):
        """Initialize Chrome driver if not already initialized"""
        if self.driver is None:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options
                from webdriver_manager.chrome import ChromeDriverManager
                
                options = Options()
                options.add_argument('--start-maximized')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                return True
            except Exception as e:
                print(f"Error initializing driver: {e}")
                return False
        return True
    
    def play_youtube_video(self, search_query: str) -> Dict:
        """
        Open YouTube, search for video, and play the first result
        """
        try:
            if not self._init_driver():
                # Fallback to simple browser open
                import webbrowser
                import urllib.parse
                encoded_query = urllib.parse.quote(search_query)
                youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                webbrowser.open(youtube_url)
                return {
                    "success": True,
                    "message": f"✅ YouTube opened with search: {search_query} (Install Selenium for auto-play)",
                    "note": "Run: pip install -r browser_requirements.txt for auto-play feature"
                }
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import urllib.parse
            
            # Navigate to YouTube search
            encoded_query = urllib.parse.quote(search_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            self.driver.get(search_url)
            
            # Wait for search results to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find and click the first video
            # YouTube video thumbnails have id that starts with 'video-title'
            first_video = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
            )
            
            video_title = first_video.get_attribute("title")
            first_video.click()
            
            return {
                "success": True,
                "message": f"✅ Playing video: {video_title}",
                "video_title": video_title
            }
            
        except ImportError:
            # Selenium not installed, fallback
            import webbrowser
            import urllib.parse
            encoded_query = urllib.parse.quote(search_query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(youtube_url)
            return {
                "success": True,
                "message": f"✅ YouTube opened with search: {search_query}",
                "note": "⚠️ Install Selenium for auto-play: pip install -r browser_requirements.txt"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error: {str(e)}",
                "note": "Opened search results instead"
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                return {"success": True, "message": "✅ Browser closed"}
            except:
                pass
        return {"success": True, "message": "No browser to close"}
