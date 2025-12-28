import os
import subprocess
import json
from typing import Dict, List, Optional

class ActionExecutor:
    """Executes actual actions on the computer"""
    
    def __init__(self):
        self.workspace = os.path.join(os.path.expanduser("~"), "AI_Workspace")
        # Create workspace if it doesn't exist
        os.makedirs(self.workspace, exist_ok=True)
        
        # Initialize browser automation (lazy loading)
        self.browser_automation = None
    
    def create_file(self, filename: str, content: str) -> Dict:
        """Create a new file with content"""
        try:
            filepath = os.path.join(self.workspace, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "success": True,
                "message": f"✅ File created: {filepath}",
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating file: {str(e)}"
            }
    
    def open_idle(self, filename: Optional[str] = None) -> Dict:
        """Open Python IDLE, optionally with a file"""
        try:
            import sys
            
            if filename:
                filepath = os.path.join(self.workspace, filename)
                # Create file if it doesn't exist
                if not os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("# New Python File\n")
                
                # Use sys.executable to ensure we use the correct Python
                subprocess.Popen([sys.executable, '-m', 'idlelib', filepath], 
                               shell=True, 
                               creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                return {
                    "success": True,
                    "message": f"✅ IDLE opened with {filename}",
                    "filepath": filepath
                }
            else:
                subprocess.Popen([sys.executable, '-m', 'idlelib'], 
                               shell=True,
                               creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                return {
                    "success": True,
                    "message": "✅ IDLE opened"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening IDLE: {str(e)}. Try: VS Code or Notepad instead"
            }
    
    def open_notepad(self, filename: Optional[str] = None) -> Dict:
        """Open Notepad, optionally with a file"""
        try:
            if filename:
                filepath = os.path.join(self.workspace, filename)
                subprocess.Popen(['notepad', filepath])
                return {
                    "success": True,
                    "message": f"✅ Notepad opened with {filename}"
                }
            else:
                subprocess.Popen(['notepad'])
                return {
                    "success": True,
                    "message": "✅ Notepad opened"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening Notepad: {str(e)}"
            }
    
    def open_vscode(self, filename: Optional[str] = None) -> Dict:
        """Open VS Code, optionally with a file"""
        try:
            if filename:
                filepath = os.path.join(self.workspace, filename)
                # Create file if it doesn't exist
                if not os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("# New Python File\n")
                subprocess.Popen(['code', filepath], shell=True)
                return {
                    "success": True,
                    "message": f"✅ VS Code opened with {filename}",
                    "filepath": filepath
                }
            else:
                subprocess.Popen(['code', self.workspace], shell=True)
                return {
                    "success": True,
                    "message": f"✅ VS Code opened workspace: {self.workspace}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening VS Code: {str(e)}. Make sure VS Code is installed."
            }
    
    def run_python_code(self, code: str) -> Dict:
        """Execute Python code and return output"""
        try:
            # Save code to temp file
            temp_file = os.path.join(self.workspace, "_temp_exec.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout if result.stdout else result.stderr
            
            return {
                "success": result.returncode == 0,
                "message": "✅ Code executed successfully" if result.returncode == 0 else "⚠️ Code executed with errors",
                "output": output,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "❌ Code execution timed out (10s limit)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error executing code: {str(e)}"
            }
    
    def execute_command(self, command: str) -> Dict:
        """Execute a system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.stdout else result.stderr
            
            return {
                "success": result.returncode == 0,
                "message": "✅ Command executed",
                "output": output,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error executing command: {str(e)}"
            }
    
    def list_files(self) -> Dict:
        """List all files in workspace"""
        try:
            files = os.listdir(self.workspace)
            return {
                "success": True,
                "message": f"✅ Found {len(files)} files",
                "files": files,
                "workspace": self.workspace
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error listing files: {str(e)}"
            }
    
    def read_file(self, filename: str) -> Dict:
        """Read file content"""
        try:
            filepath = os.path.join(self.workspace, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "message": f"✅ File read: {filename}",
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error reading file: {str(e)}"
            }
    
    
    def open_browser(self, url: str) -> Dict:
        """Open a URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            return {
                "success": True,
                "message": f"✅ Browser opened: {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening browser: {str(e)}"
            }
    
    def open_youtube(self, search_query: str) -> Dict:
        """Open YouTube and automatically play the first video"""
        try:
            # Try to use browser automation for auto-play
            if self.browser_automation is None:
                try:
                    from browser_automation import BrowserAutomation
                    self.browser_automation = BrowserAutomation()
                except ImportError:
                    pass
            
            if self.browser_automation:
                # Use browser automation to auto-play
                return self.browser_automation.play_youtube_video(search_query)
            else:
                # Fallback to simple browser open
                import webbrowser
                import urllib.parse
                
                encoded_query = urllib.parse.quote(search_query)
                youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                
                webbrowser.open(youtube_url)
                return {
                    "success": True,
                    "message": f"✅ YouTube opened with search: {search_query}",
                    "url": youtube_url,
                    "note": "⚠️ For auto-play, install: pip install -r browser_requirements.txt"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening YouTube: {str(e)}"
            }
    
    def google_search(self, query: str) -> Dict:
        """Open Google search with query"""
        try:
            import webbrowser
            import urllib.parse
            
            encoded_query = urllib.parse.quote(query)
            google_url = f"https://www.google.com/search?q={encoded_query}"
            
            webbrowser.open(google_url)
            return {
                "success": True,
                "message": f"✅ Google search opened: {query}",
                "url": google_url
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening Google: {str(e)}"
            }
    
    def open_application(self, app_name: str) -> Dict:
        """Open common applications"""
        try:
            app_commands = {
                "notepad": "notepad",
                "calculator": "calc",
                "paint": "mspaint",
                "cmd": "cmd",
                "powershell": "powershell",
                "explorer": "explorer",
                "chrome": "chrome",
                "edge": "msedge",
                "firefox": "firefox"
            }
            
            app_lower = app_name.lower()
            command = app_commands.get(app_lower, app_name)
            
            subprocess.Popen(command, shell=True)
            return {
                "success": True,
                "message": f"✅ {app_name} opened"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error opening {app_name}: {str(e)}"
            }
    
    def delete_file(self, filename: str) -> Dict:
        """Delete a file"""
        try:
            filepath = os.path.join(self.workspace, filename)
            os.remove(filepath)
            return {
                "success": True,
                "message": f"✅ File deleted: {filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error deleting file: {str(e)}"
            }
