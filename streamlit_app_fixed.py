import streamlit as st
from llama_parse import LlamaParse
import os
import shutil

# 設置頁面標題
st.set_page_config(
    page_title="多模態 PDF 解析器 - Gemini 2.5",
    page_icon="📄",
    layout="wide"
)

# 側邊欄 API 金鑰輸入
st.sidebar.header("API 設定")

# API 金鑰輸入欄位
gemini_api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    help="從 Google AI Studio (https://aistudio.google.com/app/apikey) 獲取。使用 Google 帳號登入後即可創建 API 金鑰。"
)
llama_cloud_api_key = st.sidebar.text_input(
    "Llama Cloud API Key",
    type="password",
    help="從 LlamaCloud (https://cloud.llamaindex.ai/) 獲取。註冊/登入帳號後，在控制台中可獲取免費的 API 金鑰。"
)

st.sidebar.markdown("---")

# 模型選擇 - 使用較不會觸發 recitation 的模型
st.sidebar.subheader("🤖 選擇 Gemini 模型")
model_choice = st.sidebar.selectbox(
    "模型版本",
    options=[
        "gemini-2.0-flash",      # 新版本較少觸發 recitation
        "gemini-1.5-flash",      # 舊版快速模型
        "gemini-1.5-pro"         # 舊版專業模型
    ],
    index=0,
    help="選擇要使用的 Gemini 模型版本（建議使用 2.0 版本）"
)

# 模型說明
model_descriptions = {
    "gemini-2.0-flash": "⚡ 推薦：最新版本，較少觸發內容政策限制",
    "gemini-1.5-flash": "🚀 快速處理，適合一般文件",
    "gemini-1.5-pro": "🏆 高品質，但可能觸發更多內容限制"
}
st.sidebar.info(model_descriptions.get(model_choice, "標準模型"))

# 將 API 金鑰設置為環境變數
if gemini_api_key:
    os.environ["GEMINI_API_KEY"] = gemini_api_key
if llama_cloud_api_key:
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key

st.sidebar.markdown("---")

# 側邊欄使用說明
st.sidebar.markdown("""
## 📖 使用說明
1. 輸入必要的 API 金鑰
2. 選擇 Gemini 模型版本
3. 上傳 PDF 文件
4. 點擊「開始解析」
5. 下載 Markdown 結果

## ⚠️ 避免 Recitation 錯誤
- 使用 Gemini 2.0 Flash
- 避免上傳受版權保護的書籍
- 如遇錯誤，請嘗試其他模型
""")

# 添加作者資訊
st.sidebar.markdown("---")
st.sidebar.markdown("""
## 關於作者
Code by Doctor Tseng
Endocrinologist at Tungs' Taichung Metroharbor Hospital
""")

# 主頁面標題和說明
st.title("📄 多模態 PDF 解析器（修正版）")
st.markdown("""
### 使用 Gemini 2.0 Flash 減少內容政策限制

此工具已優化以減少 "recitation" 內容政策錯誤的發生。

#### 🎯 核心功能
- ✅ **優化的提示詞** - 避免逐字複製，改為摘要和重組
- ✅ **推薦使用 Gemini 2.0 Flash** - 較少觸發內容限制
- ✅ **智能錯誤處理** - 自動偵測並提供解決建議
- ✅ **表格和圖表優先** - 專注於結構化資料提取
""")

# 檢查是否已輸入 API 金鑰
if not gemini_api_key or not llama_cloud_api_key:
    st.warning("請在左側輸入必要的 API 金鑰")
else:
    # 文件上傳區
    uploaded_file = st.file_uploader("上傳PDF文件", type="pdf")

    # 解析按鈕
    if uploaded_file is not None:
        # 創建臨時目錄
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        # 保存上傳的文件
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 顯示文件信息
        st.success(f"成功上傳文件: {uploaded_file.name}")

        # 解析按鈕
        if st.button("🚀 開始解析", type="primary", use_container_width=True):
            with st.spinner(f"正在使用 {model_choice} 解析文件，請稍候..."):
                try:
                    # 創建輸出目錄
                    output_dir = "parsed_results"
                    os.makedirs(output_dir, exist_ok=True)

                    # 修改內容指導以避免 recitation - 這是關鍵！
                    content_guideline = """
                    IMPORTANT: To avoid content policy issues, DO NOT copy text verbatim. Instead:

                    1. SUMMARIZE and PARAPHRASE all text content using your own words
                    2. Extract STRUCTURE and DATA, not exact wording:
                       - Create bullet points of main concepts
                       - Identify key themes and topics
                       - Focus on factual information (numbers, dates, names)

                    3. For TABLES: Extract as structured markdown tables with all data
                    4. For FIGURES: Describe the visual content, data trends, and key observations
                    5. For EQUATIONS: Preserve mathematical formulas exactly
                    6. For REFERENCES: List authors, titles, and publication info

                    7. Output format:
                       - Use hierarchical headings (##, ###)
                       - Create summaries for each section
                       - Use bullet points for key information
                       - DO NOT reproduce full paragraphs of original text

                    8. Focus on creating an ANALYTICAL SUMMARY rather than text extraction
                    """

                    # 使用 system_prompt 而不是 deprecated 的 content_guideline_instruction
                    parser = LlamaParse(
                        result_type="markdown",
                        use_vendor_multimodal_model=True,
                        vendor_multimodal_model_name=model_choice,
                        system_prompt=content_guideline,  # 使用 system_prompt
                        invalidate_cache=True,
                        verbose=True  # 顯示詳細資訊
                    )

                    # 執行解析
                    st.info(f"📤 正在上傳文件到 LlamaParse...")

                    try:
                        json_objs = parser.get_json_result(file_path)
                    except Exception as parse_error:
                        error_msg = str(parse_error)

                        # 提供具體的錯誤處理建議
                        if "recitation" in error_msg.lower():
                            st.error("❌ 偵測到內容政策限制（Recitation Error）")
                            st.warning("""
                            ### 解決方案：
                            1. **改用 Gemini 2.0 Flash 模型**（如果還沒使用）
                            2. **檢查 PDF 內容**：
                               - 避免上傳受版權保護的書籍全文
                               - 學術論文和技術文件通常沒問題
                            3. **嘗試分割文件**：
                               - 將大型 PDF 分成較小的部分
                               - 每次只處理幾頁
                            4. **使用本地解析工具**：
                               - 考慮使用 PyPDF2 或 pdfplumber 等本地工具
                            """)

                        elif "credits" in error_msg.lower():
                            st.error("❌ LlamaParse API 額度已用完")
                            st.info("請等待額度重置，或升級到付費方案")

                        else:
                            st.error(f"❌ 解析錯誤：{error_msg}")

                        raise parse_error

                    if not json_objs or len(json_objs) == 0:
                        raise ValueError("無法從 PDF 中解析出內容")

                    json_list = json_objs[0]["pages"]

                    # 儲存解析結果
                    output_file = os.path.join(output_dir, uploaded_file.name.replace(".pdf", ".md"))
                    with open(output_file, 'w', encoding='utf-8') as f:
                        # 添加標題
                        f.write(f"# {uploaded_file.name.replace('.pdf', '')}\n\n")
                        f.write(f"*使用 {model_choice} 解析*\n\n---\n\n")

                        for i, page in enumerate(json_list):
                            f.write(f"\n## 第 {i+1} 頁\n\n")
                            f.write(page.get('md', ''))
                            f.write('\n\n---\n\n')

                    # 讀取解析結果
                    with open(output_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 顯示成功訊息
                    st.success(f"✅ 解析完成！共處理 {len(json_list)} 頁")

                    # 顯示統計
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("總頁數", len(json_list))
                    with col2:
                        st.metric("字數", f"{len(content):,}")

                    # 顯示預覽
                    with st.expander("📝 預覽解析結果（前 1000 字）"):
                        st.markdown(content[:1000] + "..." if len(content) > 1000 else content)

                    # 提供下載按鈕
                    st.download_button(
                        label="📥 下載完整 Markdown 檔案",
                        data=content,
                        file_name=uploaded_file.name.replace(".pdf", ".md"),
                        mime="text/markdown",
                        type="primary",
                        use_container_width=True
                    )

                    # 提供建議
                    st.info("""
                    💡 **提示**：如果解析結果不理想，可以嘗試：
                    - 切換到其他 Gemini 模型
                    - 將 PDF 分成較小的部分
                    - 使用圖片轉文字工具（如果是掃描檔）
                    """)

                except Exception as e:
                    if "recitation" not in str(e).lower():
                        st.error(f"解析過程中發生錯誤: {str(e)}")

                finally:
                    # 清理臨時文件
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                    if os.path.exists(output_dir):
                        shutil.rmtree(output_dir)

# 添加頁尾
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>由 <strong>Gemini 2.0 系列模型</strong> 與 <strong>LlamaParse</strong> 提供支持</p>
    <p style='font-size: 0.9em;'>已優化以減少內容政策限制 | MIT License</p>
</div>
""", unsafe_allow_html=True)