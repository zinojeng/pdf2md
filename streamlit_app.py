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

# 模型選擇
st.sidebar.subheader("🤖 選擇 Gemini 模型")
model_choice = st.sidebar.selectbox(
    "模型版本",
    options=[
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ],
    index=0,
    help="選擇要使用的 Gemini 模型版本"
)

# 模型說明
model_descriptions = {
    "gemini-2.5-pro": "🏆 最高品質，適合複雜文件和高精度需求",
    "gemini-2.5-flash": "⚡ 平衡速度與品質，適合一般文件",
    "gemini-2.5-flash-lite": "🚀 最快速度，適合簡單文件快速處理"
}
st.sidebar.info(model_descriptions[model_choice])

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

## ✨ 功能特色
- 精確提取表格內容
- 智能識別圖表描述
- 保留文件章節結構
- 醫學術語專業處理
- 數學公式轉換
""")

# 添加作者資訊
st.sidebar.markdown("---")
st.sidebar.markdown("""
## 關於作者
Code by Doctor Tseng  
Endocrinologist at Tungs' Taichung Metroharbor Hospital
""")

# 主頁面標題和說明
st.title("📄 多模態 PDF 解析器")
st.markdown("""
### 使用 Gemini 2.5 系列模型進行智能文件解析

此工具整合 **LlamaParse** 與 **Gemini 2.5** 系列模型的多模態能力，提供專業的 PDF 轉 Markdown 解決方案。

#### 🎯 核心功能
- ✅ **精確文字提取** - 智能識別複雜版面與多欄文本
- ✅ **表格完整轉換** - 自動轉換為格式化的 Markdown 表格
- ✅ **圖表智能描述** - 詳細描述圖表內容、數據點和趨勢
- ✅ **結構化輸出** - 保持原始文件的章節層級與格式
- ✅ **專業術語處理** - 特別優化醫學、科學文獻解析
- ✅ **數學公式轉換** - 支援 LaTeX 格式數學符號

#### 📚 參考資料
- [Gemini API 模型說明](https://ai.google.dev/gemini-api/docs/models?hl=zh-tw)
- [LlamaParse 文件](https://docs.llamaindex.ai/en/stable/llama_cloud/llama_parse/)
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

                    # 初始化解析器
                    content_guideline = """
                    You are parsing a document. Pay special attention to:
                    1. Tables - extract all data into markdown tables with proper headers
                    2. Figures - describe each figure in detail including axes, data points, and trends
                    3. References - extract all references in proper citation format
                    4. Sections - maintain proper section hierarchy (Abstract, Introduction, Methods, Results, Discussion)
                    5. Technical terms - preserve exact terminology and units
                    6. Equations - convert to proper markdown math notation
                    """

                    parser = LlamaParse(
                        result_type="markdown",
                        use_vendor_multimodal_model=True,
                        vendor_multimodal_model_name=model_choice,
                        content_guideline_instruction=content_guideline,
                        invalidate_cache=True
                    )

                    # 執行解析
                    st.info(f"📤 正在上傳文件到 LlamaParse...")
                    json_objs = parser.get_json_result(file_path)

                    if not json_objs or len(json_objs) == 0:
                        raise ValueError("無法從 PDF 中解析出內容")

                    json_list = json_objs[0]["pages"]

                    # 儲存解析結果
                    output_file = os.path.join(output_dir, uploaded_file.name.replace(".pdf", ".md"))
                    with open(output_file, 'w', encoding='utf-8') as f:
                        for page in json_list:
                            f.write(page['md'])
                            f.write('\n\n')

                    # 讀取解析結果
                    with open(output_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 顯示成功訊息
                    st.success(f"✅ 解析完成！共處理 {len(json_list)} 頁")

                    # 顯示預覽
                    with st.expander("📝 預覽解析結果（前 500 字）"):
                        st.markdown(content[:500] + "...")

                    # 提供下載按鈕
                    st.download_button(
                        label="📥 下載完整 Markdown 檔案",
                        data=content,
                        file_name=uploaded_file.name.replace(".pdf", ".md"),
                        mime="text/markdown",
                        type="primary",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"解析過程中發生錯誤: {str(e)}")
                finally:
                    # 清理臨時文件
                    shutil.rmtree(temp_dir)
                    if os.path.exists(output_dir):
                        shutil.rmtree(output_dir)

# 添加頁尾
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>由 <strong>Gemini 2.5 系列模型</strong> 與 <strong>LlamaParse</strong> 提供支持</p>
    <p style='font-size: 0.9em;'>Code by Doctor Tseng | MIT License</p>
</div>
""", unsafe_allow_html=True) 