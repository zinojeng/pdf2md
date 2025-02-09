# LlamaParse with Gemini 2.0 Flash: Advanced PDF Parsing

使用 LlamaParse 結合 Gemini 2.0 Flash 技術進行多模態文件解析，特別針對醫療期刊進行優化。此工具整合兩大技術優勢，提供高效且精確的 PDF 轉 Markdown 解決方案。

> LlamaParse 現已支援 Gemini 2.0 Flash 🔥 - 目前最具成本效益的高品質文件處理模型。未來的通用文件處理和工作流程將大量依賴視覺語言模型(VLM)和大型語言模型(LLM)。

## 重要特點

- **成本效益**：Gemini 2.0 Flash 提供最經濟的文件處理解決方案
- **表格圖表處理**：特別擅長理解表格和圖表內容
- **客製化能力**：可通過解析指令優化特定領域的解析效果
- **密集文本處理**：針對密集排版的文件提供優化處理

> **注意事項**：
> - Premium 模式（15 credits/頁）仍然提供最佳的解析品質
> - Gemini 2.0 Flash 在處理密集文本時可能會有所取捨
> - 建議使用自定義解析指令來優化特定領域的解析效果

## 功能特色

- **多模態解析**：精確解析文字、表格和圖表
- **醫學專業**：支援複雜的醫學術語和公式
- **結構保留**：自動保持文件的章節結構
- **跨頁處理**：智能處理跨頁的表格和內容

## Gemini 2.0 Flash 優勢

- **超快速處理**：針對大規模文件處理進行優化
- **高精度解析**：
  - 準確識別複雜的頁面佈局
  - 智能處理多欄文本
  - 精確解析表格結構
- **多語言支持**：支援多種語言的文件解析
- **成本效益**：相比其他模型具有更好的性價比
- **批量處理**：能夠高效處理大量文件
- **版面分析**：
  - 智能識別頁眉頁腳
  - 正確處理文檔的層級結構
  - 保持原始格式的完整性

## LlamaParse 強大功能

- **多種文件格式支援**：除了 PDF，還支援 .pptx、.docx、.rtf、.pages、.epub 等格式
- **智能內容提取**：
  - 表格轉換為 Markdown 格式
  - 圖表內容詳細描述
  - 數學公式轉換
  - 參考文獻自動提取
- **自定義解析指令**：可以通過提示詞優化解析效果
- **結構化輸出**：
  - 保持文件的層級結構
  - 智能識別標題和子標題
  - 維持內容的邏輯關係
- **元數據保留**：保存圖片大小、位置等重要信息

## 技術整合優勢

- **Gemini 2.0 Flash + LlamaParse**：
  - 結合兩者優勢，提供更完整的解析方案
  - 提高處理速度和準確度
  - 優化醫療文獻的特殊需求
  - 支援大規模文件批處理

## 安裝需求

1. Python 3.7 或更高版本
2. 必要的 Python 套件：

   ```bash
   pip install -r requirements.txt
   ```

## API 金鑰設置

使用前需要取得兩個 API 金鑰：

1. **Gemini API Key**
   - 訪問 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - 使用 Google 帳號登入並創建 API 金鑰

2. **Llama Cloud API Key**
   - 訪問 [LlamaCloud](https://cloud.llamaindex.ai/)
   - 註冊/登入帳號後在控制台中獲取免費的 API 金鑰

## 使用方式

### 使用 Streamlit 網頁界面

1. 運行 Streamlit 應用：

   ```bash
   streamlit run streamlit_app.py
   ```

2. 在瀏覽器中開啟顯示的網址
3. 輸入必要的 API 金鑰
4. 上傳 PDF 文件並開始解析
5. 下載解析結果的 Markdown 文件

### 使用命令列界面

直接處理 PDF 文件：

```bash
python medical_journal_parser.py
```

## 目錄結構

```
.
├── medical_journal_parser.py  # PDF 解析核心程式
├── streamlit_app.py          # 網頁界面程式
├── requirements.txt          # 依賴套件列表
└── README.md                 # 本文件
```

## 技術細節

- 使用 LlamaParse 結合 Gemini 2.0 Flash 的多模態能力
- 特別優化醫療期刊的解析效果
- 支援表格、圖表和複雜格式的轉換

## 參考資料

- [Gemini 2.0 Flash 技術說明](https://www.sergey.fyi/articles/gemini-flash-2)
- [LlamaParse: Advanced PDF Parsing](https://medium.com/kx-systems/rag-llamaparse-advanced-pdf-parsing-for-retrieval-c393ab29891b)

## 作者

Code by Doctor Tseng  
Endocrinologist at Tungs' Taichung Metroharbor Hospital

## 授權

MIT License 