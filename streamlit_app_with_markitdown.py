import streamlit as st
from llama_parse import LlamaParse
import os
import shutil
import time
from typing import Optional, Dict
from markitdown import MarkItDown

# 設置頁面標題
st.set_page_config(
    page_title="多模態 PDF 解析器 - 智能備援版",
    page_icon="📄",
    layout="wide"
)

# 初始化 session state
if 'parsing_history' not in st.session_state:
    st.session_state.parsing_history = []

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
    help="從 LlamaCloud (https://cloud.llamaindex.ai/) 獲取。若無 API Key 或額度用完，將自動使用 MarkItDown 本地解析。"
)

st.sidebar.markdown("---")

# 模型選擇
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

# 解析模式選擇
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 解析設定")
parsing_mode = st.sidebar.radio(
    "解析模式",
    options=[
        "智能模式（推薦）",
        "LlamaParse 優先",
        "MarkItDown 本地解析"
    ],
    index=0,
    help="""
    - 智能模式：優先 LlamaParse，失敗自動切換到 MarkItDown
    - LlamaParse 優先：僅使用 LlamaParse（需要API額度）
    - MarkItDown 本地解析：僅使用 Microsoft MarkItDown（完全本地）
    """
)

# 進階選項
with st.sidebar.expander("進階選項"):
    auto_retry = st.checkbox("遇到錯誤時自動重試", value=True)
    max_retries = st.number_input("最大重試次數", min_value=1, max_value=3, value=2)
    show_debug_info = st.checkbox("顯示除錯資訊", value=False)

# 將 API 金鑰設置為環境變數
if gemini_api_key:
    os.environ["GEMINI_API_KEY"] = gemini_api_key
if llama_cloud_api_key:
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key

st.sidebar.markdown("---")

# 側邊欄使用說明
st.sidebar.markdown("""
## 📖 使用說明
1. 輸入 Gemini API 金鑰（LlamaParse 需要）
2. 選擇解析模式
3. 上傳 PDF 文件
4. 點擊「開始解析」
5. 下載 Markdown 結果

## ✨ 特色功能
- **MarkItDown 備援**：當 LlamaParse 失敗時自動切換
- **智能錯誤處理**：自動偵測並處理各種錯誤
- **完全本地選項**：使用 MarkItDown 不需任何 API
""")

# 添加作者資訊
st.sidebar.markdown("---")
st.sidebar.markdown("""
## 關於
整合 Microsoft MarkItDown 作為備援方案
Code by Doctor Tseng @ Tungs' Hospital
""")

# 主頁面標題和說明
st.title("📄 多模態 PDF 解析器 - 智能備援版")

# 添加狀態指示器
col1, col2, col3 = st.columns(3)
with col1:
    if llama_cloud_api_key:
        st.success("✅ LlamaParse 已就緒")
    else:
        st.info("ℹ️ LlamaParse 未設定")
with col2:
    st.success("✅ MarkItDown 已就緒")
with col3:
    if gemini_api_key:
        st.success(f"✅ {model_choice} 已就緒")
    else:
        st.warning("⚠️ Gemini 未設定")

st.markdown("""
### 智能文件解析，多重備援機制

此工具整合 **LlamaParse** 與 **Microsoft MarkItDown**，提供最可靠的 PDF 解析方案：
- 當 LlamaParse 遇到 **recitation 錯誤**時，自動切換到 MarkItDown
- 當 **API 額度用完**時，使用本地 MarkItDown 解析
- 完全**本地化選項**，不需要任何 API 金鑰
""")

def parse_with_markitdown(file_path: str) -> Dict:
    """
    使用 Microsoft MarkItDown 解析 PDF

    Args:
        file_path: PDF 文件路徑

    Returns:
        解析結果字典
    """
    try:
        # 初始化 MarkItDown
        md = MarkItDown()

        # 解析文件
        with open(file_path, "rb") as f:
            result = md.convert_stream(f, file_path=file_path)

        if result and result.text_content:
            return {
                "success": True,
                "content": result.text_content,
                "method": "MarkItDown",
                "title": result.title if hasattr(result, 'title') else None
            }
        else:
            return {
                "success": False,
                "error": "MarkItDown 無法提取內容",
                "method": "MarkItDown"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"MarkItDown 錯誤: {str(e)}",
            "method": "MarkItDown"
        }

def parse_with_llamaparse(file_path: str, model_choice: str) -> Dict:
    """
    使用 LlamaParse 解析 PDF

    Args:
        file_path: PDF 文件路徑
        model_choice: Gemini 模型選擇

    Returns:
        解析結果字典
    """
    try:
        # 修改內容指導以避免 recitation
        content_guideline = """
        Extract and restructure the document content:
        1. SUMMARIZE text sections, don't copy verbatim
        2. Extract DATA and STRUCTURE (tables, lists, headings)
        3. Focus on KEY INFORMATION and CONCEPTS
        4. Preserve technical terms, formulas, and numbers exactly
        5. Create an analytical summary rather than full text extraction
        6. For tables: convert to markdown format
        7. For figures: describe content and data trends
        """

        parser = LlamaParse(
            result_type="markdown",
            use_vendor_multimodal_model=True,
            vendor_multimodal_model_name=model_choice,
            system_prompt=content_guideline,
            invalidate_cache=True,
            verbose=False
        )

        # 執行解析
        json_objs = parser.get_json_result(file_path)

        if not json_objs or len(json_objs) == 0:
            return {
                "success": False,
                "error": "LlamaParse 無法提取內容",
                "method": "LlamaParse"
            }

        json_list = json_objs[0]["pages"]

        # 組合頁面內容
        content = []
        for i, page in enumerate(json_list):
            content.append(f"## Page {i+1}\n\n{page.get('md', '')}")

        return {
            "success": True,
            "content": "\n\n".join(content),
            "method": "LlamaParse",
            "pages": len(json_list)
        }

    except Exception as e:
        error_msg = str(e)
        error_type = "unknown"

        if "recitation" in error_msg.lower():
            error_type = "recitation"
        elif "credits" in error_msg.lower() or "quota" in error_msg.lower():
            error_type = "quota"
        elif "multimodal" in error_msg.lower():
            error_type = "multimodal"

        return {
            "success": False,
            "error": error_msg,
            "error_type": error_type,
            "method": "LlamaParse"
        }

def smart_parse(file_path: str, mode: str, model_choice: str,
                llama_key: Optional[str], options: Dict) -> Dict:
    """
    智能解析 PDF，根據模式和錯誤自動選擇最佳方法

    Args:
        file_path: PDF 文件路徑
        mode: 解析模式
        model_choice: Gemini 模型
        llama_key: LlamaParse API key
        options: 其他選項

    Returns:
        解析結果
    """
    results = []

    # MarkItDown 本地解析模式
    if mode == "MarkItDown 本地解析":
        st.info("🔧 使用 MarkItDown 進行本地解析...")
        result = parse_with_markitdown(file_path)
        results.append(result)
        return result

    # LlamaParse 優先模式
    elif mode == "LlamaParse 優先":
        if not llama_key:
            st.warning("⚠️ 未提供 LlamaParse API Key，自動切換到 MarkItDown")
            result = parse_with_markitdown(file_path)
            results.append(result)
            return result

        st.info(f"🚀 使用 LlamaParse + {model_choice} 解析...")
        result = parse_with_llamaparse(file_path, model_choice)
        results.append(result)

        if not result["success"]:
            st.warning(f"⚠️ LlamaParse 失敗: {result.get('error', '未知錯誤')}")

            if options.get("auto_retry") and result.get("error_type") in ["recitation", "quota"]:
                st.info("🔄 自動切換到 MarkItDown...")
                fallback_result = parse_with_markitdown(file_path)
                results.append(fallback_result)
                return fallback_result

        return result

    # 智能模式（推薦）
    else:  # 智能模式
        # 優先嘗試 LlamaParse
        if llama_key:
            st.info(f"🚀 嘗試 LlamaParse + {model_choice}...")
            result = parse_with_llamaparse(file_path, model_choice)
            results.append(result)

            if result["success"]:
                st.success("✅ LlamaParse 解析成功")
                return result
            else:
                error_type = result.get("error_type", "unknown")
                st.warning(f"⚠️ LlamaParse 遇到問題: {error_type}")

                # 根據錯誤類型決定是否重試
                if error_type == "recitation":
                    st.info("📝 檢測到內容政策限制，切換到 MarkItDown...")
                elif error_type == "quota":
                    st.info("💳 API 額度不足，切換到 MarkItDown...")
                elif options.get("auto_retry") and len(results) < options.get("max_retries", 2):
                    st.info(f"🔄 重試 {len(results)}/{options.get('max_retries', 2)}...")
                    time.sleep(2)
                    retry_result = parse_with_llamaparse(file_path, model_choice)
                    results.append(retry_result)
                    if retry_result["success"]:
                        return retry_result

        # 使用 MarkItDown 作為備援
        st.info("🔧 使用 MarkItDown 本地解析...")
        fallback_result = parse_with_markitdown(file_path)
        results.append(fallback_result)

        if fallback_result["success"]:
            st.success("✅ MarkItDown 解析成功")

        return fallback_result

# 主要介面
if not gemini_api_key and parsing_mode != "MarkItDown 本地解析":
    st.warning("請在左側輸入 Gemini API 金鑰，或選擇 MarkItDown 本地解析模式")
else:
    # 文件上傳區
    uploaded_file = st.file_uploader(
        "上傳 PDF 文件",
        type="pdf",
        help="支援各種 PDF 格式，包括掃描檔案"
    )

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
            st.success(f"✅ 已上傳: {uploaded_file.name}")
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📊 大小: {file_size_mb:.2f} MB")

        # 解析按鈕
        if st.button("🚀 開始解析", type="primary", use_container_width=True):

            # 創建進度容器
            with st.spinner("解析中..."):
                start_time = time.time()

                try:
                    # 準備選項
                    options = {
                        "auto_retry": auto_retry,
                        "max_retries": max_retries,
                        "show_debug": show_debug_info
                    }

                    # 執行智能解析
                    result = smart_parse(
                        file_path,
                        parsing_mode,
                        model_choice,
                        llama_cloud_api_key,
                        options
                    )

                    # 計算解析時間
                    elapsed_time = time.time() - start_time

                    if result["success"]:
                        content = result["content"]

                        # 添加元資料到內容開頭
                        metadata = f"""---
title: {uploaded_file.name.replace('.pdf', '')}
parsed_by: {result.get('method', 'Unknown')}
model: {model_choice if result.get('method') == 'LlamaParse' else 'N/A'}
date: {time.strftime('%Y-%m-%d %H:%M:%S')}
time_taken: {elapsed_time:.2f}s
---

"""
                        full_content = metadata + content

                        # 顯示成功訊息和統計
                        st.success(f"✅ 解析完成！使用 {result.get('method', 'Unknown')}")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("解析方法", result.get('method', 'Unknown'))
                        with col2:
                            st.metric("耗時", f"{elapsed_time:.1f} 秒")
                        with col3:
                            st.metric("字數", f"{len(content):,}")
                        with col4:
                            if result.get('pages'):
                                st.metric("頁數", result['pages'])

                        # 顯示預覽
                        with st.expander("📝 預覽解析結果", expanded=True):
                            preview_length = min(2000, len(content))
                            st.markdown(content[:preview_length] + "..." if len(content) > preview_length else content)

                        # 提供下載按鈕
                        st.download_button(
                            label="📥 下載 Markdown 檔案",
                            data=full_content,
                            file_name=uploaded_file.name.replace(".pdf", ".md"),
                            mime="text/markdown",
                            type="primary",
                            use_container_width=True
                        )

                        # 記錄到歷史
                        st.session_state.parsing_history.append({
                            "filename": uploaded_file.name,
                            "method": result.get('method'),
                            "success": True,
                            "time": elapsed_time
                        })

                    else:
                        st.error(f"❌ 解析失敗: {result.get('error', '未知錯誤')}")

                        # 提供建議
                        st.info("""
                        💡 **建議嘗試：**
                        1. 切換到 MarkItDown 本地解析模式
                        2. 檢查 PDF 是否損壞
                        3. 如果是掃描檔，可能需要 OCR 處理
                        """)

                except Exception as e:
                    st.error(f"❌ 發生錯誤: {str(e)}")

                    if show_debug_info:
                        st.exception(e)

                finally:
                    # 清理臨時文件
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)

# 顯示解析歷史
if st.session_state.parsing_history:
    with st.expander("📜 解析歷史"):
        for record in st.session_state.parsing_history[-5:]:  # 顯示最近5筆
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text(record['filename'])
            with col2:
                st.text(f"方法: {record['method']}")
            with col3:
                st.text(f"耗時: {record['time']:.1f}s")

# 添加頁尾
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>整合 <strong>LlamaParse</strong> + <strong>Microsoft MarkItDown</strong></p>
    <p style='font-size: 0.9em;'>智能備援機制，確保解析成功 | MIT License</p>
</div>
""", unsafe_allow_html=True)