#!/bin/bash

# 安裝並運行 PDF 解析器（含 MarkItDown）
# Author: Doctor Tseng

echo "========================================"
echo "PDF 解析器安裝與啟動腳本"
echo "整合 LlamaParse + Microsoft MarkItDown"
echo "========================================"
echo ""

# 檢查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 錯誤: Python 版本必須 >= 3.10 (當前: $python_version)"
    exit 1
fi

echo "✅ Python 版本檢查通過: $python_version"

# 創建虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
else
    echo "✅ 虛擬環境已存在"
fi

# 啟動虛擬環境
echo "🚀 啟動虛擬環境..."
source venv/bin/activate

# 升級 pip
echo "📦 升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  注意: 未找到 .env 文件"
    echo "創建範例 .env 文件..."
    cat > .env << 'EOF'
# API Keys Configuration
GEMINI_API_KEY=your_gemini_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
EOF
    echo "✅ 已創建 .env 範例文件，請填入您的 API 金鑰"
    echo ""
fi

# 顯示選項
echo ""
echo "========================================"
echo "請選擇要運行的版本："
echo "========================================"
echo "1) 智能備援版 (推薦) - 整合 MarkItDown"
echo "2) 修正版 - 優化 recitation 錯誤處理"
echo "3) 增強版 - 多種本地解析器"
echo "4) 原始版本"
echo "5) 退出"
echo ""
read -p "請輸入選項 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 啟動智能備援版..."
        echo "特色: 當 LlamaParse 失敗時自動切換到 MarkItDown"
        echo ""
        streamlit run streamlit_app_with_markitdown.py
        ;;
    2)
        echo ""
        echo "🚀 啟動修正版..."
        echo "特色: 優化提示詞避免 recitation 錯誤"
        echo ""
        streamlit run streamlit_app_fixed.py
        ;;
    3)
        echo ""
        echo "🚀 啟動增強版..."
        echo "特色: 整合多種本地 PDF 解析器"
        echo ""
        streamlit run streamlit_app_enhanced.py
        ;;
    4)
        echo ""
        echo "🚀 啟動原始版本..."
        echo ""
        streamlit run streamlit_app.py
        ;;
    5)
        echo "退出程式"
        exit 0
        ;;
    *)
        echo "無效的選項，啟動預設版本..."
        streamlit run streamlit_app_with_markitdown.py
        ;;
esac