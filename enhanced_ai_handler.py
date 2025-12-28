import os
import re
import json
from google import genai
from google.genai import types
from typing import Dict, Optional
from action_executor import ActionExecutor
from user_memory import UserMemory

class EnhancedAIHandler:
    """Enhanced AI that can understand commands and execute actions"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.executor = ActionExecutor()
        self.user_memory = UserMemory()  # Add user memory
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'models/gemini-flash-latest'
        else:
            self.client = None
            self.model_name = None
    
    def is_configured(self) -> bool:
        """Check if AI is properly configured"""
        return self.client is not None
    
    async def process_command(self, command: str, context: Optional[str] = None) -> Dict:
        """
        Process user command - understand intent and execute actions
        """
        if not self.is_configured():
            return {
                "response": "⚠️ AI not configured. Please add your GEMINI_API_KEY to the .env file.",
                "code": None,
                "language": None,
                "actions": []
            }
        
        
        # Get user context from memory
        user_context = self.user_memory.get_context_for_ai()
        
        # First, ask AI to understand the command and generate action plan
        analysis_prompt = f"""You are an AI assistant that can control a computer. Analyze this command and determine what actions to take:

{user_context}

Command: "{command}"

Respond in JSON format with this structure:
{{
    "intent": "what the user wants to do",
    "actions": [
        {{
            "type": "create_file" | "open_idle" | "open_vscode" | "run_code" | "execute_command" | "open_youtube" | "open_browser" | "google_search" | "open_application" | "just_respond",
            "params": {{
                "filename": "optional filename",
                "content": "optional content",
                "code": "optional code to run",
                "command": "optional system command",
                "search_query": "for YouTube search",
                "url": "for browser",
                "query": "for Google search",
                "app_name": "application name"
            }}
        }}
    ],
    "response": "friendly response to user explaining what you'll do"
}}

Examples:
- "open youtube and play saiyara song" → {{"type": "open_youtube", "params": {{"search_query": "saiyara song"}}}}
- "open idle and create even odd code" → create file with even/odd code, then open in IDLE
- "google search for python tutorials" → {{"type": "google_search", "params": {{"query": "python tutorials"}}}}
- "open calculator" → {{"type": "open_application", "params": {{"app_name": "calculator"}}}}
- "create a python file to sort list" → create file with sorting code
- "run this code: print('hello')\" → execute the code
- "explain recursion" → just respond with explanation

Be smart and helpful! Understand YouTube, browser, Google, and application commands!
Remember user information from the context above!"""

        try:
            # Get AI's analysis
            analysis_response = self.client.models.generate_content(
                model=self.model_name,
                contents=analysis_prompt
            )
            
            analysis_text = analysis_response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                # Fallback: just respond
                plan = {
                    "intent": "respond",
                    "actions": [{"type": "just_respond"}],
                    "response": analysis_text
                }
            
            # Execute actions
            action_results = []
            for action in plan.get("actions", []):
                action_type = action.get("type")
                params = action.get("params", {})
                
                if action_type == "create_file":
                    # Generate code if needed
                    if not params.get("content"):
                        code_prompt = f"Write clean, well-commented Python code for: {plan['intent']}"
                        code_response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=code_prompt
                        )
                        code_text = code_response.text
                        # Extract code from markdown
                        code_blocks = self._extract_code_blocks(code_text)
                        if code_blocks:
                            params["content"] = code_blocks[0]["code"]
                        else:
                            params["content"] = code_text
                    
                    result = self.executor.create_file(
                        params.get("filename", "script.py"),
                        params.get("content", "")
                    )
                    action_results.append(result)
                
                elif action_type == "open_idle":
                    result = self.executor.open_idle(params.get("filename"))
                    action_results.append(result)
                
                elif action_type == "open_vscode":
                    result = self.executor.open_vscode(params.get("filename"))
                    action_results.append(result)
                
                elif action_type == "run_code":
                    result = self.executor.run_python_code(params.get("code", ""))
                    action_results.append(result)
                
                elif action_type == "execute_command":
                    result = self.executor.execute_command(params.get("command", ""))
                    action_results.append(result)
                
                elif action_type == "open_youtube":
                    search_query = params.get("search_query", "")
                    result = self.executor.open_youtube(search_query)
                    action_results.append(result)
                
                elif action_type == "open_browser":
                    url = params.get("url", "")
                    result = self.executor.open_browser(url)
                    action_results.append(result)
                
                elif action_type == "google_search":
                    query = params.get("query", "")
                    result = self.executor.google_search(query)
                    action_results.append(result)
                
                elif action_type == "open_application":
                    app_name = params.get("app_name", "")
                    result = self.executor.open_application(app_name)
                    action_results.append(result)
            
            # Build final response
            final_response = plan.get("response", "Done!")
            
            # Add action results to response
            if action_results:
                final_response += "\n\n**Actions Performed:**\n"
                for result in action_results:
                    final_response += f"\n{result.get('message', '')}"
                    if result.get('output'):
                        final_response += f"\nOutput: {result['output']}"
            
            
            # Extract any code blocks for display
            code_blocks = self._extract_code_blocks(analysis_text)
            
            # Extract and store user information from this conversation
            self.user_memory.extract_and_store_info(command, final_response)
            
            return {
                "response": final_response,
                "code": code_blocks[0]["code"] if code_blocks else None,
                "language": code_blocks[0]["language"] if code_blocks else None,
                "actions": action_results
            }
                
        except Exception as e:
            error_message = str(e)
            
            if "429" in error_message or "quota" in error_message.lower() or "RESOURCE_EXHAUSTED" in error_message:
                return {
                    "response": "⚠️ **API Quota Limit Reached!**\n\n"
                               "Please wait 30-60 minutes and try again.\n"
                               "Check usage: https://aistudio.google.com/apikey",
                    "code": None,
                    "language": None,
                    "actions": []
                }
            
            return {
                "response": f"❌ Error: {error_message}",
                "code": None,
                "language": None,
                "actions": []
            }
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from markdown-formatted text"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for match in matches:
            language = match[0] if match[0] else "text"
            code = match[1].strip()
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
