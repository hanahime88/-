# AI 角色扮演聊天應用 / AI Role Playing Chat App

一個功能完整的AI角色扮演聊天應用，支援多種語言模型和豐富的互動功能。

A comprehensive AI role-playing chat application with multiple language model support and rich interactive features.

## 🌟 功能特色 / Features

### 核心功能 / Core Features
- **🤖 AI角色扮演** - 基於角色設定進行深度對話 / Deep character-based conversations
- **💬 多聊天室管理** - 創建、編輯、刪除聊天室 / Create, edit, delete chat sessions
- **🧠 過去回憶系統** - 上傳文字檔案作為記憶背景 / Upload text files as memory background
- **📝 訊息編輯** - 編輯訊息並重新生成AI回應 / Edit messages and regenerate AI responses
- **📁 檔案上傳** - 支援圖片、影片、文字檔案 / Support for images, videos, text files

### 界面功能 / Interface Features
- **📱 響應式設計** - 支援桌面端和行動裝置 / Desktop and mobile responsive
- **🎨 可縮放側邊欄** - 功能豐富的側邊欄 / Collapsible feature-rich sidebar
- **🌐 多語言界面** - 繁體中文/英文界面 / Traditional Chinese/English interface
- **🎭 頭像上傳** - 自訂使用者和角色頭像 / Custom user and character avatars

### AI功能 / AI Features
- **🔄 多模型支援** - Gemini 2.0 Flash / Gemini 1.5 Pro
- **⚙️ 自訂回覆長度** - 調整AI回應的字數 / Adjustable AI response length
- **💾 智能記憶** - AI會根據過去回憶進行回應 / AI responds based on uploaded memories

### 資料管理 / Data Management
- **💾 聊天記錄導出** - 按頁整理匯出對話內容 / Export conversations in organized format
- **🗃️ 本地資料庫** - SQLite資料庫儲存 / SQLite database storage
- **🔒 資料安全** - 本地儲存，保護隱私 / Local storage for privacy protection

## 📋 系統需求 / System Requirements

- Python 3.8+
- Google API Key (for Gemini AI)
- 現代瀏覽器 / Modern web browser

## 🚀 快速開始 / Quick Start

### 1. 下載專案 / Download Project
```bash
git clone <repository-url>
cd ai-roleplay-chat
```

### 2. 設置環境變數 / Set Environment Variables
```bash
# Linux/Mac
export GOOGLE_API_KEY="your-google-api-key"

# Windows
set GOOGLE_API_KEY=your-google-api-key
```

### 3. 啟動應用 / Start Application
```bash
python run.py
```

### 4. 訪問應用 / Access Application
在瀏覽器中開啟：http://localhost:8000
Open in browser: http://localhost:8000

## 📖 使用指南 / User Guide

### 基本操作 / Basic Operations

1. **建立聊天室 / Create Chat Session**
   - 點擊側邊欄的「新聊天」按鈕
   - 輸入聊天室名稱和選擇角色
   - Click "New Chat" in sidebar
   - Enter session name and select character

2. **設置過去回憶 / Set Up Memories**
   - 在側邊欄「過去回憶」區塊輸入文字
   - 或上傳 .txt / .docx 檔案
   - Enter text in "Memories" section in sidebar
   - Or upload .txt / .docx files

3. **開始對話 / Start Conversation**
   - 在輸入框輸入訊息並發送
   - AI會根據角色設定和回憶進行回應
   - Type message in input field and send
   - AI responds based on character and memories

4. **編輯訊息 / Edit Messages**
   - 滑鼠懸停在訊息上，點擊「編輯」
   - 修改內容後，AI會重新生成後續回應
   - Hover over message and click "Edit"
   - AI regenerates subsequent responses after editing

5. **匯出對話 / Export Conversations**
   - 點擊頂部的「匯出」按鈕
   - 系統會產生結構化的文字檔案
   - Click "Export" button in header
   - System generates structured text file

### 高級設置 / Advanced Settings

1. **AI模型選擇 / AI Model Selection**
   - 在側邊欄設定中選擇模型
   - Gemini 2.0 Flash：速度快
   - Gemini 1.5 Pro：品質高
   - Select model in sidebar settings
   - Gemini 2.0 Flash: Fast speed
   - Gemini 1.5 Pro: High quality

2. **回覆長度設定 / Response Length Setting**
   - 調整50-1000字符的回覆長度
   - 適合不同的對話需求
   - Adjust 50-1000 character response length
   - Suitable for different conversation needs

3. **語言設置 / Language Settings**
   - 支援繁體中文和英文介面
   - 可隨時切換語言
   - Support Traditional Chinese and English
   - Switch language anytime

## 🎭 角色配置 / Character Configuration

應用使用YAML格式的角色配置檔案。預設包含Damian Knight角色。

The app uses YAML format character configuration files. Includes Damian Knight character by default.

### 角色檔案結構 / Character File Structure
```yaml
character_id: unique_id
name: Character Name
basic_info:
  age: 28
  gender: male
personality: Character personality description
speech_patterns:
  neutral: "Default response pattern"
  happy: "Happy mood response pattern"
  angry: "Angry mood response pattern"
relationship_with_you: Relationship description
# ... more character details
```

## 📁 專案結構 / Project Structure

```
ai-roleplay-chat/
├── app.py                 # 主應用程式 / Main application
├── run.py                 # 啟動腳本 / Startup script
├── requirements.txt       # 依賴包列表 / Dependencies
├── damian_knight_dusk.yaml # 預設角色檔案 / Default character
├── templates/
│   └── index.html        # 前端界面 / Frontend interface
├── static/               # 靜態檔案 / Static files
├── uploads/              # 上傳檔案儲存 / Upload storage
└── data/                 # 資料庫檔案 / Database files
```

## 🔧 API文檔 / API Documentation

### 主要端點 / Main Endpoints

- `GET /` - 主界面 / Main interface
- `GET /api/sessions` - 取得聊天室列表 / Get chat sessions
- `POST /api/sessions` - 建立新聊天室 / Create new session
- `POST /api/chat` - 發送訊息 / Send message
- `PUT /api/messages/{id}` - 編輯訊息 / Edit message
- `GET /api/memories` - 取得回憶列表 / Get memories
- `POST /api/memories` - 新增回憶 / Add memory
- `POST /api/export/{session_id}` - 匯出對話 / Export conversation

## 🐛 故障排除 / Troubleshooting

### 常見問題 / Common Issues

1. **API Key錯誤 / API Key Error**
   - 確認已設置正確的Google API Key
   - 檢查API Key是否有Gemini權限
   - Verify correct Google API Key is set
   - Check if API Key has Gemini permissions

2. **依賴包安裝失敗 / Dependency Installation Failed**
   - 更新pip：`pip install --upgrade pip`
   - 使用虛擬環境：`python -m venv venv`
   - Update pip: `pip install --upgrade pip`
   - Use virtual environment: `python -m venv venv`

3. **資料庫錯誤 / Database Error**
   - 刪除data/資料夾重新啟動
   - 檢查檔案權限
   - Delete data/ folder and restart
   - Check file permissions

4. **上傳檔案失敗 / File Upload Failed**
   - 檢查檔案格式是否支援
   - 確認檔案大小不超過限制
   - Check if file format is supported
   - Ensure file size is within limits

## 🤝 貢獻 / Contributing

歡迎提交Issue和Pull Request！

Welcome to submit Issues and Pull Requests!

## 📄 授權 / License

此專案基於MIT授權條款。

This project is licensed under the MIT License.

## 📞 支援 / Support

如有問題，請提交Issue或聯繫開發者。

For issues, please submit an Issue or contact the developer.

---

## 🚀 立即開始使用 / Get Started Now

```bash
# 克隆專案 / Clone project
git clone <repository-url>
cd ai-roleplay-chat

# 設置API Key / Set API Key
export GOOGLE_API_KEY="your-api-key"

# 啟動應用 / Start application
python run.py
```

享受與AI角色的深度對話體驗！🎭✨

Enjoy deep conversations with AI characters! 🎭✨