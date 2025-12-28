import os
import re
from google import genai
from google.genai import types
from typing import Dict, Optional

class AIHandler:
    """Handles AI interactions using Google Gemini (New SDK)"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            # Initialize the new Google GenAI client
            self.client = genai.Client(api_key=self.api_key)
            # Using gemini-flash-latest - always points to latest stable flash model
            self.model_name = 'models/gemini-flash-latest'
        else:
            self.client = None
            self.model_name = None
    
    def is_configured(self) -> bool:
        """Check if AI is properly configured"""
        return self.client is not None
    
    async def process_command(self, command: str, context: Optional[str] = None) -> Dict:
        """
        Process user command and generate appropriate response
        """
        if not self.is_configured():
            return {
                "response": "⚠️ AI not configured. Please add your GEMINI_API_KEY to the .env file.",
                "code": None,
                "language": None
            }
        
        # Create enhanced prompt
        prompt = self._create_prompt(command, context)
        
        try:
            # Generate response using new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            result_text = response.text
            
            # Extract code blocks if present
            code_blocks = self._extract_code_blocks(result_text)
            
            if code_blocks:
                # If code is found, return it separately
                main_code = code_blocks[0]
                return {
                    "response": result_text,
                    "code": main_code["code"],
                    "language": main_code["language"]
                }
            else:
                # No code, just return the response
                return {
                    "response": result_text,
                    "code": None,
                    "language": None
                }
                
        except Exception as e:
            error_message = str(e)
            
            # Check if it's a quota error
            if "429" in error_message or "quota" in error_message.lower() or "RESOURCE_EXHAUSTED" in error_message:
                return {
                    "response": "⚠️ **API Quota Limit Reached!**\n\n"
                               "Your free tier limit has been exceeded. Please:\n"
                               "1. Wait 30-60 minutes and try again\n"
                               "2. Check your usage at: https://aistudio.google.com/apikey\n"
                               "3. The free tier resets every minute/day\n\n"
                               "**Free Tier Limits:**\n"
                               "- 15 requests per minute\n"
                               "- 1,500 requests per day\n"
                               "- 1 million tokens per day\n\n"
                               "**Tip:** Wait a bit before trying again! 😊",
                    "code": None,
                    "language": None
                }
            
            return {
                "response": f"❌ Error processing command: {error_message}\n\nPlease try again or check the backend logs.",
                "code": None,
                "language": None
            }
    
    def _create_prompt(self, command: str, context: Optional[str] = None) -> str:
        """Create an enhanced prompt for the AI"""
        base_prompt = f"""You are a helpful AI coding assistant. The user has given you this command:

"{command}"

Please provide a clear, helpful response. If the user is asking for code:
1. Write clean, well-commented code
2. Explain what the code does
3. Include usage examples if relevant
4. Use proper formatting with code blocks (```language)

If the user is asking a question, provide a clear and concise answer.

"""
        if context:
            base_prompt += f"\nAdditional context: {context}\n"
        
        return base_prompt
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from markdown-formatted text"""
        # Pattern to match ```language\ncode\n```
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
