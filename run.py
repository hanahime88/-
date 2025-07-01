#!/usr/bin/env python3
"""
AI Role Playing Chat Application
啟動腳本 - Startup Script
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    if sys.version_info < (3, 8):
        print("錯誤：需要Python 3.8或更高版本")
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def install_dependencies():
    """安裝依賴包"""
    print("正在安裝依賴包...")
    print("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依賴包安裝完成！")
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"安裝依賴包失敗：{e}")
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """設置環境變數"""
    print("設置環境變數...")
    print("Setting up environment...")
    
    # 設置Google API Key（如果沒有設置的話）
    if not os.getenv('GOOGLE_API_KEY'):
        print("\n注意：需要設置Google API Key")
        print("Note: Google API Key is required")
        print("請設置環境變數 GOOGLE_API_KEY")
        print("Please set environment variable GOOGLE_API_KEY")
        print("或在啟動應用後在設定中配置")
        print("Or configure it in settings after starting the app")
        
        # 提供預設的API Key（開發用）
        os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'

def create_directories():
    """創建必要的目錄"""
    directories = ['static', 'templates', 'uploads', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("目錄結構創建完成")
    print("Directory structure created")

def show_startup_info():
    """顯示啟動信息"""
    print("\n" + "="*60)
    print("🤖 AI 角色扮演聊天應用 - AI Role Playing Chat App")
    print("="*60)
    print("功能特色 Features:")
    print("✅ 可縮放側邊欄 - Collapsible Sidebar")
    print("✅ 多聊天室管理 - Multiple Chat Sessions")
    print("✅ 過去回憶系統 - Memory System")
    print("✅ 文件上傳支援 - File Upload Support")
    print("✅ 訊息編輯功能 - Message Editing")
    print("✅ AI模型選擇 - AI Model Selection")
    print("✅ 多語言界面 - Multilingual Interface")
    print("✅ 聊天記錄匯出 - Chat Export")
    print("✅ 響應式設計 - Responsive Design")
    print("="*60)
    print("開發者：AI Assistant")
    print("Developer: AI Assistant")
    print("="*60)

def main():
    """主函數"""
    show_startup_info()
    
    print("\n正在啟動應用...")
    print("Starting application...")
    
    # 檢查Python版本
    check_python_version()
    
    # 安裝依賴
    install_dependencies()
    
    # 設置環境
    setup_environment()
    
    # 創建目錄
    create_directories()
    
    print("\n正在啟動伺服器...")
    print("Starting server...")
    
    # 設置端口
    port = os.getenv("PORT", "8000")
    
    print(f"\n🚀 應用啟動成功！")
    print(f"🚀 Application started successfully!")
    print(f"📱 請在瀏覽器中訪問：http://localhost:{port}")
    print(f"📱 Please visit in browser: http://localhost:{port}")
    print(f"⚠️  請確保已設置Google API Key")
    print(f"⚠️  Please ensure Google API Key is configured")
    print(f"🛑 按 Ctrl+C 停止服務")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("\n" + "="*60)
    
    try:
        # 啟動FastAPI應用
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=int(port),
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 應用已停止")
        print("👋 Application stopped")
    except Exception as e:
        print(f"\n❌ 啟動失敗：{e}")
        print(f"❌ Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()