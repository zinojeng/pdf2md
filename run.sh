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
    echo "=========================================================="
    echo "📚 PDF to Markdown 解析器 - 版本選擇"
    echo "=========================================================="
    echo ""
    echo "  1) 🌟 智能備援版 (streamlit_app_with_markitdown.py) ⭐ 推薦"
    echo "     ✓ 整合 Microsoft MarkItDown 作為備援方案"
    echo "     ✓ 三種解析模式：智能模式、LlamaParse優先、純本地解析"
    echo "     ✓ 當 LlamaParse 失敗時自動切換到 MarkItDown"
    echo "     ✓ 不需要 API Key 也能使用（選擇本地模式）"
    echo "     ✓ 最穩定可靠，適合所有類型文件"
    echo ""
    echo "  2) 🔧 修正版 (streamlit_app_fixed.py)"
    echo "     ✓ 重新設計提示詞，要求摘要而非逐字複製"
    echo "     ✓ 預設使用 Gemini 2.0 Flash（較少觸發內容限制）"
    echo "     ✓ 使用 system_prompt 替代 deprecated 參數"
    echo "     ✓ 詳細的錯誤處理和解決方案提示"
    echo "     ✓ 適合處理可能有版權疑慮的文件"
    echo ""
    echo "  3) 💪 增強版 (streamlit_app_enhanced.py)"
    echo "     ✓ 整合多種本地解析器但不含 MarkItDown"
    echo "     ✓ 智能錯誤處理與自動重試機制"
    echo "     ✓ 支援分段處理大型文件"
    echo "     ✓ 三種解析模式可選"
    echo "     ✓ 適合需要精細控制的進階使用者"
    echo ""
    echo "  4) 📝 原始版本 (streamlit_app.py)"
    echo "     ✓ 基礎 LlamaParse + Gemini 功能"
    echo "     ✓ 簡單直接的介面"
    echo "     ✓ 適合 API 額度充足且文件單純的情況"
    echo ""
    echo "  5) ⚡ CLI 批次處理 (medical_journal_parser.py)"
    echo "     ✓ 命令列批次處理工具"
    echo "     ✓ 自動處理 medical_journals/ 目錄中的所有 PDF"
    echo "     ✓ 輸出至 parsed_journals/ 目錄"
    echo "     ✓ 適合大量文件自動化處理"
    echo ""
    echo "  6) 👋 退出"
    echo ""
    echo "=========================================================="
    echo "提示：首次使用建議選擇 1 (智能備援版)"
    echo "=========================================================="
}

# 啟動選定的版本
launch_app() {
    case $1 in
        1)
            echo ""
            echo "=========================================================="
            echo "🌟 啟動智能備援版 (推薦使用)"
            echo "=========================================================="
            echo "✨ 主要功能："
            echo "   • 當遇到 recitation 錯誤時自動切換到 MarkItDown"
            echo "   • 當 API 額度用完時自動使用本地解析"
            echo "   • 提供三種模式：智能模式、LlamaParse優先、純本地"
            echo ""
            echo "💡 使用提示："
            echo "   • 選擇「MarkItDown 本地解析」完全不需要 API Key"
            echo "   • 智能模式會自動選擇最佳解析方案"
            echo "   • 適合處理任何類型的 PDF 文件"
            echo "=========================================================="
            echo ""
            streamlit run streamlit_app_with_markitdown.py
            ;;
        2)
            echo ""
            echo "=========================================================="
            echo "🔧 啟動修正版"
            echo "=========================================================="
            echo "✨ 主要改進："
            echo "   • 提示詞要求「摘要和改寫」而非逐字複製"
            echo "   • 預設使用 Gemini 2.0 Flash（較新的模型）"
            echo "   • 修正 deprecated 參數警告"
            echo ""
            echo "💡 適用場景："
            echo "   • 處理可能有版權的文件（教科書、期刊等）"
            echo "   • LlamaParse API 額度充足"
            echo "   • 需要避免 recitation 內容政策錯誤"
            echo "=========================================================="
            echo ""
            streamlit run streamlit_app_fixed.py
            ;;
        3)
            echo ""
            echo "=========================================================="
            echo "💪 啟動增強版"
            echo "=========================================================="
            echo "✨ 整合工具："
            echo "   • PyPDF2 - 基礎文字提取"
            echo "   • pdfplumber - 表格提取專家"
            echo "   • PyMuPDF - 圖片和複雜版面處理"
            echo ""
            echo "💡 進階功能："
            echo "   • 自動重試機制（最多3次）"
            echo "   • 分段處理大型文件"
            echo "   • 多種解析策略自動切換"
            echo "=========================================================="
            echo ""
            streamlit run streamlit_app_enhanced.py
            ;;
        4)
            echo ""
            echo "=========================================================="
            echo "📝 啟動原始版本"
            echo "=========================================================="
            echo "✨ 基礎功能："
            echo "   • 標準 LlamaParse + Gemini 解析"
            echo "   • 支援模型選擇（Pro/Flash/Flash-Lite）"
            echo "   • 簡單直接的操作介面"
            echo ""
            echo "⚠️  注意："
            echo "   • 無錯誤處理機制"
            echo "   • 可能遇到 recitation 錯誤"
            echo "   • 需要有效的 API 額度"
            echo "=========================================================="
            echo ""
            streamlit run streamlit_app.py
            ;;
        5)
            echo ""
            echo "=========================================================="
            echo "⚡ 執行批次處理"
            echo "=========================================================="
            echo "📁 處理目錄: medical_journals/"
            echo "📁 輸出目錄: parsed_journals/"
            echo ""
            echo "處理中..."
            python medical_journal_parser.py
            ;;
        6)
            echo "👋 感謝使用！再見！"
            exit 0
            ;;
        *)
            echo "❌ 無效的選項，請輸入 1-6"
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