from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class MemoryManager:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    
    def add_message(self, user_id: str, role: str, content: str, session_id: str = None):
        """Store message in Supabase with session tracking"""
        try:
            self.supabase.table('chat_history').insert({
                'user_id': user_id,
                'session_id': session_id or 'default',
                'role': role,
                'content': content,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error saving message: {e}")
    
    def get_session_history(self, user_id: str, session_id: str, limit: int = 10):
        """Get messages for specific session"""
        try:
            response = self.supabase.table('chat_history')\
                .select('role, content')\
                .eq('user_id', user_id)\
                .eq('session_id', session_id)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            messages = [{"role": msg['role'], "content": msg['content']} 
                       for msg in response.data]
            return messages
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def get_recent_history(self, user_id: str, limit: int = 100):
        """Get all recent messages (for history page)"""
        try:
            response = self.supabase.table('chat_history')\
                .select('role, content')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            messages = [{"role": msg['role'], "content": msg['content']} 
                       for msg in reversed(response.data)]
            return messages
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def clear_history(self, user_id: str):
        """Clear user's chat history"""
        try:
            self.supabase.table('chat_history')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
