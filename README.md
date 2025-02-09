# Multimodal Parsing with Gemini 2.0 Flash

使用 Gemini 2.0 Flash 技術進行多模態文件解析，特別針對醫療期刊進行優化。此工具可以將醫學期刊 PDF 文件轉換為結構化的 Markdown 格式。

## 功能特色

- **多模態解析**：精確解析文字、表格和圖表
- **醫學專業**：支援複雜的醫學術語和公式
- **結構保留**：自動保持文件的章節結構
- **跨頁處理**：智能處理跨頁的表格和內容

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

## 作者

Code by Doctor Tseng  
Endocrinologist at Tungs' Taichung Metroharbor Hospital

## 授權

MIT License 