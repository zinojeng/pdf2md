# 📚 PDF 解析器安裝與使用指南

## 🎯 解決方案概覽

本專案提供多個版本來處理 PDF 解析時的 **recitation 錯誤**和 **API 額度**問題：

### 版本比較

| 版本 | 檔案名稱 | 主要特色 | 適用情況 |
|------|----------|----------|----------|
| **智能備援版** ⭐ | `streamlit_app_with_markitdown.py` | 整合 Microsoft MarkItDown 作為備援 | 推薦使用，最穩定 |
| **修正版** | `streamlit_app_fixed.py` | 優化提示詞避免 recitation | LlamaParse 額度充足時 |
| **增強版** | `streamlit_app_enhanced.py` | 多種本地 PDF 解析器 | 需要完全離線解析 |
| **原始版** | `streamlit_app.py` | 基礎功能 | 測試用途 |

## 🚀 快速開始

### 方法一：自動安裝（推薦）

```bash
# 執行安裝腳本
./install_and_run.sh
```

腳本會自動：
1. 檢查 Python 版本（需要 >= 3.10）
2. 創建虛擬環境
3. 安裝所有依賴（包括 MarkItDown）
4. 讓您選擇要運行的版本

### 方法二：手動安裝

```bash
# 1. 創建虛擬環境
python3 -m venv venv

# 2. 啟動虛擬環境
source venv/bin/activate  # macOS/Linux

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 運行智能備援版（推薦）
streamlit run streamlit_app_with_markitdown.py
```

## 🔑 API 金鑰設定

### 選項 1：創建 .env 檔案（推薦）

```bash
# 創建 .env 檔案
cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
EOF
```

### 選項 2：在網頁介面輸入

直接在 Streamlit 側邊欄輸入 API 金鑰

### 獲取 API 金鑰

- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **LlamaCloud API Key**: [LlamaCloud](https://cloud.llamaindex.ai/) （選擇性）

## 💡 解決常見問題

### 問題 1：Recitation 內容政策錯誤

**錯誤訊息**：`Gemini response was blocked due to content policy (recitation)`

**解決方案**：
1. 使用**智能備援版**（自動切換到 MarkItDown）
2. 改用 `gemini-2.0-flash` 模型
3. 避免上傳受版權保護的完整書籍

### 問題 2：LlamaParse API 額度用完

**錯誤訊息**：`You've exceeded the maximum number of credits`

**解決方案**：
1. 使用**智能備援版**（自動使用 MarkItDown）
2. 選擇「MarkItDown 本地解析」模式
3. 不需要 LlamaParse API Key

### 問題 3：安裝 MarkItDown 失敗

如果遇到安裝問題，可以直接從源碼安裝：

```bash
# Clone MarkItDown
git clone https://github.com/microsoft/markitdown.git

# 安裝
pip install -e 'markitdown/packages/markitdown[all]'
```

## 📊 功能比較

### LlamaParse vs MarkItDown

| 特性 | LlamaParse | MarkItDown |
|------|------------|------------|
| **需要 API Key** | ✅ 需要 | ❌ 不需要 |
| **需要網路** | ✅ 需要 | ❌ 完全本地 |
| **解析品質** | 🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟 |
| **速度** | 中等（依網路） | 快速 |
| **支援格式** | PDF | PDF, Word, PPT, Excel, 等 |
| **內容政策限制** | 可能觸發 | 無限制 |
| **費用** | 有免費額度 | 完全免費 |

## 🎯 使用建議

### 最佳實踐

1. **一般使用**：使用「智能備援版」+ 智能模式
2. **受版權保護文件**：直接使用 MarkItDown 本地解析
3. **醫學/科學論文**：LlamaParse 通常效果較好
4. **大量文件批次處理**：使用 MarkItDown 避免 API 限制

### 模型選擇

- **gemini-2.0-flash**：推薦，較少觸發 recitation
- **gemini-1.5-flash**：快速，但可能觸發限制
- **gemini-1.5-pro**：品質最高，但最容易觸發限制

## 📝 進階設定

### 自訂解析參數

編輯 `streamlit_app_with_markitdown.py` 中的 `content_guideline`：

```python
content_guideline = """
# 您的自訂提示詞
1. 專注於提取結構化資料
2. 摘要而非逐字複製
3. 保留技術術語和數字
"""
```

### 批次處理

使用原始的 `medical_journal_parser.py` 進行批次處理：

```bash
python medical_journal_parser.py
```

## 🆘 技術支援

如遇問題，請檢查：

1. Python 版本 >= 3.10
2. 所有依賴已正確安裝
3. API 金鑰正確設定（如使用 LlamaParse）
4. PDF 檔案未損壞

## 📄 授權

MIT License

---

**作者**: Doctor Tseng @ Tungs' Taichung MetroHarbor Hospital
**整合**: Microsoft MarkItDown + LlamaParse + Gemini API