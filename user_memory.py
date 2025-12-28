"""
User Memory & Profile System
Stores user information long-term across all conversations
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class UserMemory:
    """Manages long-term user memory and profile"""
    
    def __init__(self):
        self.memory_file = os.path.join(os.path.expanduser("~"), "AI_Workspace", "user_memory.json")
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_default_memory()
        return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict:
        """Create default memory structure"""
        return {
            "profile": {
                "name": None,
                "occupation": None,
                "interests": [],
                "skills": [],
                "preferences": {},
                "location": None
            },
            "facts": [],  # List of facts about user
            "preferences": {},  # User preferences
            "history_summary": [],  # Key moments from conversations
            "last_updated": None
        }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def extract_and_store_info(self, user_message: str, ai_response: str):
        """Extract information from conversation and store it"""
        message_lower = user_message.lower()
        
        # Extract name
        if any(phrase in message_lower for phrase in ['my name is', 'mera naam', 'i am', 'main hoon']):
            name = self._extract_name(user_message)
            if name:
                self.memory['profile']['name'] = name
                self._save_memory()
        
        # Extract occupation
        if any(phrase in message_lower for phrase in ['i work as', 'i am a', 'main', 'kaam karta', 'kaam karti']):
            occupation = self._extract_occupation(user_message)
            if occupation:
                self.memory['profile']['occupation'] = occupation
                self._save_memory()
        
        # Extract interests
        if any(phrase in message_lower for phrase in ['i like', 'i love', 'mujhe pasand', 'interested in']):
            interests = self._extract_interests(user_message)
            if interests:
                for interest in interests:
                    if interest not in self.memory['profile']['interests']:
                        self.memory['profile']['interests'].append(interest)
                self._save_memory()
        
        # Store as fact
        if self._is_personal_info(user_message):
            fact = {
                "content": user_message,
                "timestamp": datetime.now().isoformat(),
                "context": ai_response[:100] if ai_response else ""
            }
            self.memory['facts'].append(fact)
            self.memory['last_updated'] = datetime.now().isoformat()
            self._save_memory()
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from text"""
        import re
        
        patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"mera naam (\w+)",
            r"main (\w+) hoon",
            r"call me (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).capitalize()
        return None
    
    def _extract_occupation(self, text: str) -> Optional[str]:
        """Extract occupation from text"""
        import re
        
        patterns = [
            r"i work as (?:a |an )?(.+?)(?:\.|$)",
            r"i am (?:a |an )?(.+?)(?:\.|$)",
            r"main (.+?) hoon",
            r"kaam karta hoon (.+?)(?:\.|$)",
            r"kaam karti hoon (.+?)(?:\.|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                occupation = match.group(1).strip()
                # Filter out common words
                if len(occupation) > 2 and occupation not in ['student', 'working']:
                    return occupation
        return None
    
    def _extract_interests(self, text: str) -> List[str]:
        """Extract interests from text"""
        import re
        
        patterns = [
            r"i like (.+?)(?:\.|$)",
            r"i love (.+?)(?:\.|$)",
            r"mujhe (.+?) pasand",
            r"interested in (.+?)(?:\.|$)"
        ]
        
        interests = []
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                interest = match.group(1).strip()
                interests.append(interest)
        
        return interests
    
    def _is_personal_info(self, text: str) -> bool:
        """Check if message contains personal information"""
        personal_keywords = [
            'my name', 'i am', 'i work', 'i like', 'i love',
            'mera naam', 'main hoon', 'mujhe pasand', 'kaam karta', 'kaam karti'
        ]
        return any(keyword in text.lower() for keyword in personal_keywords)
    
    def get_context_for_ai(self) -> str:
        """Get user context to send to AI"""
        if not self.memory['profile']['name'] and not self.memory['facts']:
            return ""
        
        context = "**User Information (Remember this):**\n"
        
        # Profile
        if self.memory['profile']['name']:
            context += f"- Name: {self.memory['profile']['name']}\n"
        
        if self.memory['profile']['occupation']:
            context += f"- Occupation: {self.memory['profile']['occupation']}\n"
        
        if self.memory['profile']['interests']:
            context += f"- Interests: {', '.join(self.memory['profile']['interests'])}\n"
        
        # Recent facts (last 5)
        if self.memory['facts']:
            context += "\n**Previous conversations:**\n"
            for fact in self.memory['facts'][-5:]:
                context += f"- {fact['content']}\n"
        
        return context
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        return self.memory['profile']
    
    def clear_memory(self):
        """Clear all memory"""
        self.memory = self._create_default_memory()
        self._save_memory()
    
    def get_memory_summary(self) -> str:
        """Get a summary of stored memory"""
        profile = self.memory['profile']
        facts_count = len(self.memory['facts'])
        
        summary = "**Your AI knows about you:**\n\n"
        
        if profile['name']:
            summary += f"✅ Name: {profile['name']}\n"
        else:
            summary += "❌ Name: Not set\n"
        
        if profile['occupation']:
            summary += f"✅ Occupation: {profile['occupation']}\n"
        else:
            summary += "❌ Occupation: Not set\n"
        
        if profile['interests']:
            summary += f"✅ Interests: {', '.join(profile['interests'])}\n"
        else:
            summary += "❌ Interests: Not set\n"
        
        summary += f"\n📝 Total facts stored: {facts_count}\n"
        
        if self.memory['last_updated']:
            summary += f"🕐 Last updated: {self.memory['last_updated']}\n"
        
        return summary
