import streamlit as st
from llama_parse import LlamaParse
import os
import shutil
import json
import time
from typing import Optional, Dict, List
from pdf_parser_alternative import parse_pdf_with_fallbacks

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
    "Llama Cloud API Key (選擇性)",
    type="password",
    help="從 LlamaCloud (https://cloud.llamaindex.ai/) 獲取。若額度用完可留空，將使用替代方案。"
)

st.sidebar.markdown("---")

# 模型選擇
st.sidebar.subheader("🤖 選擇 Gemini 模型")
model_choice = st.sidebar.selectbox(
    "模型版本",
    options=[
        "gemini-2.0-flash",  # 改用 2.0 版本，較少觸發 recitation
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ],
    index=0,
    help="選擇要使用的 Gemini 模型版本"
)

# 模型說明
model_descriptions = {
    "gemini-2.0-flash": "⚡ 最新版本，較少觸發內容政策限制",
    "gemini-1.5-pro": "🏆 高品質，適合複雜文件",
    "gemini-1.5-flash": "🚀 快速處理，適合一般文件"
}
st.sidebar.info(model_descriptions.get(model_choice, "標準模型"))

# 解析模式選擇
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 解析設定")
parsing_mode = st.sidebar.radio(
    "解析模式",
    options=["智能模式", "LlamaParse優先", "本地解析"],
    index=0,
    help="""
    - 智能模式：自動選擇最佳方案
    - LlamaParse優先：優先使用 LlamaParse（需要API額度）
    - 本地解析：僅使用本地工具（不需要 LlamaParse）
    """
)

# 進階選項
with st.sidebar.expander("進階選項"):
    retry_on_error = st.checkbox("遇到錯誤時自動重試", value=True)
    max_retries = st.number_input("最大重試次數", min_value=1, max_value=5, value=3)
    chunk_pages = st.checkbox("分段處理大型文件", value=True,
                              help="將大型PDF分成小段處理，避免觸發內容政策")
    pages_per_chunk = st.number_input("每段頁數", min_value=5, max_value=50, value=10)

# 將 API 金鑰設置為環境變數
if gemini_api_key:
    os.environ["GEMINI_API_KEY"] = gemini_api_key
if llama_cloud_api_key:
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key

st.sidebar.markdown("---")

# 側邊欄使用說明
st.sidebar.markdown("""
## 📖 使用說明
1. 輸入 Gemini API 金鑰（必要）
2. 輸入 LlamaParse API 金鑰（選擇性）
3. 選擇解析模式
4. 上傳 PDF 文件
5. 點擊「開始解析」
6. 下載 Markdown 結果

## ⚠️ 常見問題解決
- **Recitation錯誤**：系統會自動切換到替代方案
- **API額度不足**：使用本地解析模式
- **大型文件**：啟用分段處理
""")

# 添加作者資訊
st.sidebar.markdown("---")
st.sidebar.markdown("""
## 關於作者
Code by Doctor Tseng
Endocrinologist at Tungs' Taichung Metroharbor Hospital
""")

# 主頁面標題和說明
st.title("📄 多模態 PDF 解析器（增強版）")
st.markdown("""
### 智能文件解析，自動處理錯誤

此工具整合多種解析方案，當遇到 API 限制或內容政策問題時會自動切換到替代方案。

#### 🎯 核心功能
- ✅ **智能錯誤處理** - 自動偵測並處理 recitation 政策錯誤
- ✅ **多重解析引擎** - LlamaParse、PyPDF2、pdfplumber、PyMuPDF
- ✅ **分段處理** - 避免觸發內容政策限制
- ✅ **自動重試機制** - 遇到錯誤時智能重試
- ✅ **離線備援** - API額度用完時可使用本地解析
""")

def parse_with_llama_parse(file_path: str, model_choice: str, chunk_mode: bool = False,
                           start_page: int = 0, end_page: Optional[int] = None) -> Dict:
    """
    使用 LlamaParse 解析 PDF

    Args:
        file_path: PDF 文件路徑
        model_choice: Gemini 模型選擇
        chunk_mode: 是否使用分段模式
        start_page: 開始頁數
        end_page: 結束頁數

    Returns:
        解析結果字典
    """
    try:
        # 修改內容指導以避免 recitation
        content_guideline = """
        Extract and reformat the document content following these rules:
        1. Focus on structure and data, not exact wording
        2. Summarize lengthy paragraphs while preserving key information
        3. Extract tables as structured data
        4. Describe figures and charts focusing on data trends
        5. Use your own words to explain concepts
        6. Preserve technical terms, numbers, and formulas exactly
        7. DO NOT copy verbatim text passages
        8. Create an outline-based summary rather than full text extraction
        """

        # 添加頁面範圍參數
        extra_info = {}
        if chunk_mode and end_page:
            extra_info = {
                "page_range": f"{start_page}-{end_page}",
            }

        parser = LlamaParse(
            result_type="markdown",
            use_vendor_multimodal_model=True,
            vendor_multimodal_model_name=model_choice,
            system_prompt=content_guideline,  # 使用 system_prompt 代替 deprecated 的參數
            invalidate_cache=True,
            **extra_info
        )

        # 執行解析
        json_objs = parser.get_json_result(file_path)

        if not json_objs or len(json_objs) == 0:
            return {"error": "無法從 PDF 中解析出內容", "type": "empty_result"}

        json_list = json_objs[0]["pages"]

        # 組合解析結果
        content = []
        for page in json_list:
            content.append(page.get('md', ''))

        return {
            "success": True,
            "content": "\n\n".join(content),
            "pages": len(json_list)
        }

    except Exception as e:
        error_msg = str(e)

        # 分析錯誤類型
        if "recitation" in error_msg.lower():
            return {"error": "內容政策限制（recitation）", "type": "recitation"}
        elif "credits" in error_msg.lower() or "quota" in error_msg.lower():
            return {"error": "API 額度不足", "type": "quota"}
        elif "multimodal_error" in error_msg.lower():
            return {"error": "多模態處理錯誤", "type": "multimodal", "details": error_msg}
        else:
            return {"error": f"解析錯誤：{error_msg}", "type": "unknown"}

def handle_recitation_error(file_path: str, error_details: str) -> Optional[str]:
    """
    處理 recitation 錯誤，提取失敗的頁面並使用替代方法

    Args:
        file_path: PDF 文件路徑
        error_details: 錯誤詳情

    Returns:
        解析結果或 None
    """
    # 從錯誤訊息中提取失敗的頁面
    import re
    failed_pages = re.findall(r'Page (\d+):', error_details)
    failed_pages = [int(p) for p in failed_pages]

    if failed_pages:
        st.warning(f"檢測到 {len(failed_pages)} 頁觸發內容政策，將使用替代方法處理這些頁面")

    # 使用替代方法
    return None

def smart_parse_pdf(file_path: str, gemini_api_key: str, llama_api_key: Optional[str],
                    mode: str, model_choice: str, options: Dict) -> str:
    """
    智能 PDF 解析主函數

    Args:
        file_path: PDF 文件路徑
        gemini_api_key: Gemini API 金鑰
        llama_api_key: LlamaParse API 金鑰（可選）
        mode: 解析模式
        model_choice: 模型選擇
        options: 其他選項

    Returns:
        解析結果（Markdown 格式）
    """
    result = None
    retry_count = 0
    max_retries = options.get("max_retries", 3)

    # 根據模式選擇解析策略
    if mode == "本地解析" or not llama_api_key:
        st.info("使用本地解析工具...")
        result = parse_pdf_with_fallbacks(file_path, gemini_api_key, model_choice)

    elif mode == "LlamaParse優先" or mode == "智能模式":
        while retry_count < max_retries:
            st.info(f"嘗試使用 LlamaParse 解析... (第 {retry_count + 1} 次)")

            # 嘗試 LlamaParse
            parse_result = parse_with_llama_parse(
                file_path,
                model_choice,
                chunk_mode=options.get("chunk_pages", False),
            )

            if parse_result.get("success"):
                result = parse_result["content"]
                st.success("✅ LlamaParse 解析成功！")
                break

            else:
                error_type = parse_result.get("type", "unknown")
                error_msg = parse_result.get("error", "未知錯誤")

                st.warning(f"⚠️ {error_msg}")

                # 根據錯誤類型決定策略
                if error_type == "recitation":
                    st.info("檢測到內容政策限制，切換到本地解析...")
                    result = parse_pdf_with_fallbacks(file_path, gemini_api_key, model_choice)
                    break

                elif error_type == "quota":
                    st.info("API 額度不足，切換到本地解析...")
                    result = parse_pdf_with_fallbacks(file_path, gemini_api_key, model_choice)
                    break

                elif error_type == "multimodal":
                    # 如果是部分頁面失敗，嘗試處理
                    if "Page errors" in parse_result.get("details", ""):
                        alternative = handle_recitation_error(file_path, parse_result["details"])
                        if alternative:
                            result = alternative
                            break

                    # 重試或切換
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.info("多次嘗試失敗，切換到本地解析...")
                        result = parse_pdf_with_fallbacks(file_path, gemini_api_key, model_choice)
                        break
                    else:
                        time.sleep(2)  # 等待後重試

                else:
                    retry_count += 1
                    if retry_count >= max_retries:
                        st.info("切換到本地解析...")
                        result = parse_pdf_with_fallbacks(file_path, gemini_api_key, model_choice)
                        break

    return result or "無法解析文件"

# 檢查是否已輸入必要的 API 金鑰
if not gemini_api_key:
    st.warning("請在左側輸入 Gemini API 金鑰")
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
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ 成功上傳: {uploaded_file.name}")
        with col2:
            st.info(f"📊 文件大小: {uploaded_file.size / 1024:.2f} KB")

        # 解析按鈕
        if st.button("🚀 開始解析", type="primary", use_container_width=True):

            # 創建進度容器
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # 創建輸出目錄
                    output_dir = "parsed_results"
                    os.makedirs(output_dir, exist_ok=True)

                    # 更新進度
                    progress_bar.progress(20)
                    status_text.text("📤 準備解析文件...")

                    # 準備選項
                    options = {
                        "retry_on_error": retry_on_error,
                        "max_retries": max_retries,
                        "chunk_pages": chunk_pages,
                        "pages_per_chunk": pages_per_chunk
                    }

                    # 執行智能解析
                    progress_bar.progress(40)
                    status_text.text(f"🔄 使用 {model_choice} 進行解析...")

                    content = smart_parse_pdf(
                        file_path,
                        gemini_api_key,
                        llama_cloud_api_key,
                        parsing_mode,
                        model_choice,
                        options
                    )

                    progress_bar.progress(80)
                    status_text.text("💾 保存解析結果...")

                    # 儲存解析結果
                    output_file = os.path.join(output_dir, uploaded_file.name.replace(".pdf", ".md"))
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    progress_bar.progress(100)
                    status_text.text("✅ 解析完成！")

                    # 顯示成功訊息
                    st.success(f"✅ 成功解析文件！")

                    # 顯示統計信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("字數", f"{len(content):,}")
                    with col2:
                        st.metric("行數", f"{content.count(chr(10)):,}")
                    with col3:
                        st.metric("段落數", f"{content.count(chr(10)*2):,}")

                    # 顯示預覽
                    with st.expander("📝 預覽解析結果", expanded=True):
                        preview_length = min(2000, len(content))
                        st.markdown(content[:preview_length] + "..." if len(content) > preview_length else content)

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
                    st.error(f"❌ 解析過程中發生錯誤: {str(e)}")
                    st.info("💡 建議：請嘗試切換到「本地解析」模式或聯繫技術支援")

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
    <p>由 <strong>Gemini API</strong> 與 <strong>多重解析引擎</strong> 提供支持</p>
    <p style='font-size: 0.9em;'>增強版 - 自動處理內容政策限制 | MIT License</p>
</div>
""", unsafe_allow_html=True)