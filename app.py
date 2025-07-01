import os
import json
import sqlite3
import uuid
from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

import yaml
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import aiofiles
import google.generativeai as genai
from PIL import Image
import cv2
import magic
from docx import Document
from langdetect import detect
import re

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'your-api-key-here'))

app = FastAPI(title="AI Role Playing Chat", version="1.0.0")

# Setup directories
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"

for directory in [STATIC_DIR, TEMPLATES_DIR, UPLOAD_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Setup static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Database setup
DATABASE_PATH = DATA_DIR / "chat_data.db"

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            character_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'user' or 'assistant'
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            edited BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
    """)
    
    # Memories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Characters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data TEXT NOT NULL,  -- JSON string of character data
            avatar_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Initialize default settings
    default_settings = {
        'language': 'zh-TW',
        'model': 'gemini-2.0-flash-exp',
        'response_length': '200',
        'user_avatar': ''
    }
    
    for key, value in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Data models
class ChatMessage(BaseModel):
    content: str
    session_id: str

class EditMessage(BaseModel):
    message_id: str
    content: str

class CreateSession(BaseModel):
    name: str
    character_id: str

class UpdateSessionName(BaseModel):
    session_id: str
    name: str

class Memory(BaseModel):
    title: str
    content: str

class Settings(BaseModel):
    language: Optional[str] = None
    model: Optional[str] = None
    response_length: Optional[str] = None

# Character management
class CharacterEngine:
    """Enhanced character engine with AI integration"""
    
    def __init__(self, char_data: Dict[str, Any]):
        self.char = char_data
        self.name = char_data.get("name", "Unknown")
        self.personality = self._build_personality_prompt()
    
    def _build_personality_prompt(self) -> str:
        """Build comprehensive personality prompt from character data"""
        prompt = f"You are {self.name}.\n\n"
        
        if "basic_info" in self.char:
            basic = self.char["basic_info"]
            prompt += f"Basic Info:\n"
            for key, value in basic.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        if "personality" in self.char:
            prompt += f"Personality: {self.char['personality']}\n\n"
        
        if "background" in self.char:
            prompt += f"Background: {self.char['background']}\n\n"
        
        if "speech_patterns" in self.char:
            prompt += f"Speech Patterns:\n"
            for mood, pattern in self.char["speech_patterns"].items():
                prompt += f"- {mood}: {pattern}\n"
            prompt += "\n"
        
        if "relationship_with_you" in self.char:
            prompt += f"Relationship with user: {self.char['relationship_with_you']}\n\n"
        
        prompt += "Always stay in character and respond as this character would. Use the personality, background, and speech patterns to guide your responses."
        
        return prompt
    
    async def generate_response(self, user_message: str, conversation_history: List[Dict], memories: List[str], model_name: str, response_length: int) -> str:
        """Generate AI response using Gemini"""
        try:
            # Build context
            context = self.personality + "\n\n"
            
            if memories:
                context += "Relevant memories:\n"
                for memory in memories[-3:]:  # Use last 3 memories for context
                    context += f"- {memory}\n"
                context += "\n"
            
            # Add conversation history
            if conversation_history:
                context += "Recent conversation:\n"
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = "You" if msg["role"] == "assistant" else "User"
                    context += f"{role}: {msg['content']}\n"
                context += "\n"
            
            context += f"User: {user_message}\n"
            context += f"Respond as {self.name} in approximately {response_length} characters. Stay in character:"
            
            # Generate response
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(context)
            
            return response.text.strip()
            
        except Exception as e:
            return f"抱歉，我現在無法回應。錯誤：{str(e)}"

# Utility functions
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def get_setting(key: str, default: str = "") -> str:
    """Get setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

def set_setting(key: str, value: str):
    """Set setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_character(character_id: str) -> Optional[CharacterEngine]:
    """Load character from database or YAML file"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM characters WHERE id = ?", (character_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        char_data = json.loads(result[0])
        return CharacterEngine(char_data)
    
    # Fallback to YAML file
    yaml_path = f"{character_id}.yaml"
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            char_data = yaml.safe_load(f)
        return CharacterEngine(char_data)
    
    return None

def get_memories() -> List[str]:
    """Get all memories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM memories ORDER BY created_at DESC")
    results = cursor.fetchall()
    conn.close()
    return [result[0] for result in results]

def process_uploaded_file(file_path: str) -> str:
    """Process uploaded file and extract text content"""
    try:
        file_type = magic.from_file(file_path, mime=True)
        
        if file_type.startswith('text/'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return "無法處理此檔案格式"
    except Exception as e:
        return f"檔案處理錯誤：{str(e)}"

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/sessions")
async def get_sessions():
    """Get all chat sessions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, character_id, created_at FROM chat_sessions ORDER BY updated_at DESC")
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            "id": row[0],
            "name": row[1],
            "character_id": row[2],
            "created_at": row[3]
        })
    conn.close()
    return sessions

@app.post("/api/sessions")
async def create_session(session_data: CreateSession):
    """Create new chat session"""
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (id, name, character_id) VALUES (?, ?, ?)",
                   (session_id, session_data.name, session_data.character_id))
    conn.commit()
    conn.close()
    return {"session_id": session_id}

@app.put("/api/sessions/{session_id}/name")
async def update_session_name(session_id: str, data: dict):
    """Update session name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_sessions SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                   (data["name"], session_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete chat session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get messages for a session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, content, timestamp, edited FROM messages WHERE session_id = ? ORDER BY timestamp",
                   (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "id": row[0],
            "role": row[1],
            "content": row[2],
            "timestamp": row[3],
            "edited": bool(row[4])
        })
    conn.close()
    return messages

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Send message and get AI response"""
    try:
        # Get session info
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT character_id FROM chat_sessions WHERE id = ?", (message.session_id,))
        session_result = cursor.fetchone()
        
        if not session_result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        character_id = session_result[0]
        
        # Load character
        character = load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Save user message
        user_msg_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
                       (user_msg_id, message.session_id, "user", message.content))
        
        # Get conversation history
        cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT 20",
                       (message.session_id,))
        history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        history.reverse()
        
        # Get memories
        memories = get_memories()
        
        # Get settings
        model = get_setting("model", "gemini-2.0-flash-exp")
        response_length = int(get_setting("response_length", "200"))
        
        # Generate AI response
        ai_response = await character.generate_response(
            message.content, history, memories, model, response_length
        )
        
        # Save AI response
        ai_msg_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
                       (ai_msg_id, message.session_id, "assistant", ai_response))
        
        # Update session timestamp
        cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                       (message.session_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "user_message_id": user_msg_id,
            "ai_message_id": ai_msg_id,
            "response": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/messages/{message_id}")
async def edit_message(message_id: str, edit_data: dict):
    """Edit a message and regenerate subsequent AI responses"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get message info
        cursor.execute("SELECT session_id, role, timestamp FROM messages WHERE id = ?", (message_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Message not found")
        
        session_id, role, timestamp = result
        
        # Update message
        cursor.execute("UPDATE messages SET content = ?, edited = TRUE WHERE id = ?",
                       (edit_data["content"], message_id))
        
        # Delete subsequent messages
        cursor.execute("DELETE FROM messages WHERE session_id = ? AND timestamp > ?",
                       (session_id, timestamp))
        
        # If user message was edited, regenerate AI response
        if role == "user":
            # Get character and generate new response
            cursor.execute("SELECT character_id FROM chat_sessions WHERE id = ?", (session_id,))
            character_id = cursor.fetchone()[0]
            
            character = load_character(character_id)
            if character:
                # Get updated conversation history
                cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp",
                               (session_id,))
                history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
                
                memories = get_memories()
                model = get_setting("model", "gemini-2.0-flash-exp")
                response_length = int(get_setting("response_length", "200"))
                
                ai_response = await character.generate_response(
                    edit_data["content"], history, memories, model, response_length
                )
                
                # Save new AI response
                ai_msg_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
                               (ai_msg_id, session_id, "assistant", ai_response))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memories")
async def get_all_memories():
    """Get all memories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, created_at FROM memories ORDER BY created_at DESC")
    memories = []
    for row in cursor.fetchall():
        memories.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "created_at": row[3]
        })
    conn.close()
    return memories

@app.post("/api/memories")
async def add_memory(memory: Memory):
    """Add new memory"""
    memory_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memories (id, title, content) VALUES (?, ?, ?)",
                   (memory_id, memory.title, memory.content))
    conn.commit()
    conn.close()
    return {"memory_id": memory_id}

@app.post("/api/memories/upload")
async def upload_memory_file(file: UploadFile = File(...)):
    """Upload file as memory"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process file
        text_content = process_uploaded_file(str(file_path))
        
        # Save as memory
        memory_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memories (id, title, content) VALUES (?, ?, ?)",
                       (memory_id, file.filename, text_content))
        conn.commit()
        conn.close()
        
        # Clean up file
        os.unlink(file_path)
        
        return {"memory_id": memory_id, "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image for AI analysis"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {"file_path": str(file_path), "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return settings

@app.put("/api/settings")
async def update_settings(settings: dict):
    """Update settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    for key, value in settings.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/api/export/{session_id}")
async def export_session(session_id: str):
    """Export session as structured text file"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("SELECT name, character_id FROM chat_sessions WHERE id = ?", (session_id,))
        session_info = cursor.fetchone()
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_name, character_id = session_info
        
        # Get all messages
        cursor.execute("SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp",
                       (session_id,))
        messages = cursor.fetchall()
        
        conn.close()
        
        # Generate structured export
        export_content = f"聊天記錄導出\n"
        export_content += f"="*50 + "\n"
        export_content += f"會話名稱: {session_name}\n"
        export_content += f"角色ID: {character_id}\n"
        export_content += f"導出時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_content += f"訊息總數: {len(messages)}\n\n"
        
        # Process messages in pages of 10
        page_size = 10
        for page_num in range(0, len(messages), page_size):
            page_messages = messages[page_num:page_num + page_size]
            export_content += f"第 {page_num//page_size + 1} 頁\n"
            export_content += f"-"*30 + "\n"
            
            # Analyze page content
            user_messages = [msg for msg in page_messages if msg[0] == 'user']
            ai_messages = [msg for msg in page_messages if msg[0] == 'assistant']
            
            export_content += f"時間範圍: {page_messages[0][2]} - {page_messages[-1][2]}\n"
            export_content += f"登場角色: 使用者, {character_id}\n"
            export_content += f"互動次數: 使用者發言 {len(user_messages)} 次, AI回應 {len(ai_messages)} 次\n"
            
            # Extract key dialogues
            key_dialogues = []
            for msg in page_messages:
                role = "使用者" if msg[0] == "user" else "AI角色"
                content = msg[1][:100] + "..." if len(msg[1]) > 100 else msg[1]
                key_dialogues.append(f"{role}: {content}")
            
            export_content += f"\n重要對話:\n"
            for dialogue in key_dialogues:
                export_content += f"  {dialogue}\n"
            
            export_content += f"\n" + "="*50 + "\n\n"
        
        # Save export file
        export_filename = f"chat_export_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        export_path = UPLOAD_DIR / export_filename
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(export_content)
        
        return FileResponse(
            path=str(export_path),
            media_type='text/plain',
            filename=export_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize default character if not exists
async def init_default_character():
    """Initialize default character from YAML file"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]
    
    if count == 0 and os.path.exists("damian_knight_dusk.yaml"):
        with open("damian_knight_dusk.yaml", 'r', encoding='utf-8') as f:
            char_data = yaml.safe_load(f)
        
        char_id = char_data.get("character_id", "damian_knight_dusk")
        char_name = char_data.get("name", "Damian Knight")
        
        cursor.execute("INSERT INTO characters (id, name, data) VALUES (?, ?, ?)",
                       (char_id, char_name, json.dumps(char_data, cls=DateTimeEncoder)))
        conn.commit()
    
    conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    await init_default_character()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)