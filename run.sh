#!/bin/bash

# PDF to Markdown Parser - 啟動腳本

echo "==================================="
echo "PDF to Markdown Parser with Gemini 2.5 Pro"
echo "==================================="
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 找不到 Python3，請先安裝 Python"
    exit 1
fi

# 建立虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo "建立虛擬環境..."
    python3 -m venv venv
    echo "虛擬環境建立完成"
    echo ""
fi

# 啟動虛擬環境
echo "啟動虛擬環境..."
source venv/bin/activate

# 安裝/更新相依套件
echo "安裝相依套件..."
pip install -r requirements.txt --quiet
echo "相依套件安裝完成"
echo ""

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo "警告: 找不到 .env 檔案"
    echo "請建立 .env 檔案並設定以下環境變數："
    echo "  GEMINI_API_KEY=your_key_here"
    echo "  LLAMA_CLOUD_API_KEY=your_key_here"
    echo ""
    read -p "按 Enter 繼續或 Ctrl+C 取消..."
fi

# 建立必要的目錄
mkdir -p medical_journals
mkdir -p parsed_journals

# 執行 Streamlit 網頁介面
echo "==================================="
echo "啟動 Streamlit 網頁介面..."
echo "==================================="
echo ""
streamlit run streamlit_app.py
