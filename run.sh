#!/bin/bash

# PDF to Markdown Parser - 統一啟動腳本
# Author: Doctor Tseng

echo "========================================"
echo "PDF to Markdown 解析器 - 啟動腳本"
echo "整合 LlamaParse + Microsoft MarkItDown"
echo "========================================"
echo ""

# 檢查 Python 版本
check_python_version() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ 錯誤: 找不到 Python3，請先安裝 Python"
        exit 1
    fi

    python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    required_version="3.10"

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        echo "❌ 錯誤: Python 版本必須 >= 3.10 (當前: $python_version)"
        exit 1
    fi

    echo "✅ Python 版本檢查通過: $python_version"
}

# 設置虛擬環境
setup_venv() {
    if [ ! -d "venv" ]; then
        echo "📦 創建虛擬環境..."
        python3 -m venv venv
    else
        echo "✅ 虛擬環境已存在"
    fi

    echo "🚀 啟動虛擬環境..."
    source venv/bin/activate
}

# 安裝依賴
install_dependencies() {
    echo "📦 檢查並安裝依賴..."

    # 升級 pip
    pip install --upgrade pip --quiet

    # 檢查是否需要安裝或更新
    if [ -f "requirements.txt" ]; then
        # 檢查 markitdown 是否已安裝
        if ! pip show markitdown > /dev/null 2>&1; then
            echo "📦 安裝所有依賴套件（包括 MarkItDown）..."
            pip install -r requirements.txt
        else
            echo "✅ 依賴已安裝，檢查更新..."
            pip install -r requirements.txt --upgrade --quiet
        fi
    else
        echo "❌ 錯誤: 找不到 requirements.txt"
        exit 1
    fi
}

# 檢查並創建 .env 檔案
setup_env() {
    if [ ! -f ".env" ]; then
        echo ""
        echo "⚠️  注意: 未找到 .env 文件"
        echo "創建範例 .env 文件..."
        cat > .env << 'EOF'
# API Keys Configuration
# 從以下網址獲取 API Keys:
# Gemini: https://aistudio.google.com/app/apikey
# LlamaCloud: https://cloud.llamaindex.ai/

GEMINI_API_KEY=your_gemini_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
EOF
        echo "✅ 已創建 .env 範例文件"
        echo ""
        echo "請編輯 .env 文件並填入您的 API 金鑰"
        echo "注意: MarkItDown 本地解析模式不需要任何 API Key"
        echo ""
        read -p "按 Enter 繼續，或 Ctrl+C 取消..."
    fi
}

# 創建必要的目錄
create_directories() {
    mkdir -p medical_journals
    mkdir -p parsed_journals
    mkdir -p temp_uploads
    mkdir -p parsed_results
}

# 顯示版本選單
show_menu() {
    echo ""
    echo "========================================"
    echo "請選擇要運行的版本："
    echo "========================================"
    echo ""
    echo "  1) 智能備援版 ⭐ (推薦)"
    echo "     整合 Microsoft MarkItDown，自動處理錯誤"
    echo ""
    echo "  2) 修正版"
    echo "     優化提示詞，減少 recitation 錯誤"
    echo ""
    echo "  3) 增強版"
    echo "     多種本地 PDF 解析器"
    echo ""
    echo "  4) 原始版本"
    echo "     基礎 LlamaParse 功能"
    echo ""
    echo "  5) CLI 批次處理"
    echo "     處理 medical_journals/ 目錄中的所有 PDF"
    echo ""
    echo "  6) 退出"
    echo ""
    echo "========================================"
}

# 啟動選定的版本
launch_app() {
    case $1 in
        1)
            echo ""
            echo "🚀 啟動智能備援版..."
            echo "✨ 特色: 當 LlamaParse 失敗時自動切換到 MarkItDown"
            echo "💡 提示: 可選擇「MarkItDown 本地解析」完全不需要 API"
            echo ""
            streamlit run streamlit_app_with_markitdown.py
            ;;
        2)
            echo ""
            echo "🚀 啟動修正版..."
            echo "✨ 特色: 優化提示詞避免 recitation 錯誤"
            echo ""
            streamlit run streamlit_app_fixed.py
            ;;
        3)
            echo ""
            echo "🚀 啟動增強版..."
            echo "✨ 特色: 整合 PyPDF2, pdfplumber, PyMuPDF"
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
            echo ""
            echo "🚀 執行批次處理..."
            echo "處理 medical_journals/ 目錄中的所有 PDF 檔案"
            echo ""
            python medical_journal_parser.py
            ;;
        6)
            echo "👋 再見！"
            exit 0
            ;;
        *)
            echo "無效的選項"
            ;;
    esac
}

# 主程式
main() {
    # 檢查 Python 版本
    check_python_version

    # 設置虛擬環境
    setup_venv

    # 安裝依賴
    install_dependencies

    # 檢查 .env 檔案
    setup_env

    # 創建必要目錄
    create_directories

    # 如果有命令行參數，直接啟動對應版本
    if [ "$1" == "--smart" ] || [ "$1" == "-s" ]; then
        launch_app 1
    elif [ "$1" == "--fixed" ] || [ "$1" == "-f" ]; then
        launch_app 2
    elif [ "$1" == "--enhanced" ] || [ "$1" == "-e" ]; then
        launch_app 3
    elif [ "$1" == "--original" ] || [ "$1" == "-o" ]; then
        launch_app 4
    elif [ "$1" == "--batch" ] || [ "$1" == "-b" ]; then
        launch_app 5
    elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        echo "使用方法："
        echo "  ./run.sh              # 顯示互動選單"
        echo "  ./run.sh --smart      # 直接啟動智能備援版（推薦）"
        echo "  ./run.sh --fixed      # 直接啟動修正版"
        echo "  ./run.sh --enhanced   # 直接啟動增強版"
        echo "  ./run.sh --original   # 直接啟動原始版"
        echo "  ./run.sh --batch      # 執行批次處理"
        echo "  ./run.sh --help       # 顯示此說明"
        exit 0
    else
        # 顯示選單
        show_menu
        read -p "請輸入選項 (1-6): " choice
        launch_app $choice
    fi
}

# 執行主程式
main "$@"