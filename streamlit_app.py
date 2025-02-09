import streamlit as st
from medical_journal_parser import process_pdf
import os
import shutil

# 設置頁面標題
st.set_page_config(
    page_title="Multimodal Parsing with Gemini 2.0 Flash", 
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

# 將 API 金鑰設置為環境變數
if gemini_api_key:
    os.environ["GEMINI_API_KEY"] = gemini_api_key
if llama_cloud_api_key:
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key

st.sidebar.markdown("---")

# 側邊欄使用說明
st.sidebar.markdown("""
## 使用說明
1. 取得並輸入必要的 API 金鑰
2. 上傳PDF文件
3. 點擊「開始解析」按鈕
4. 下載解析結果

## 功能特色
- 支持表格提取
- 自動識別圖表
- 保留章節結構
- 高精度醫學術語處理
""")

# 添加作者資訊
st.sidebar.markdown("---")
st.sidebar.markdown("""
## 關於作者
Code by Doctor Tseng  
Endocrinologist at Tungs' Taichung Metroharbor Hospital
""")

# 主頁面標題和說明
st.title("📄 Multimodal Parsing with Gemini 2.0 Flash")
st.markdown("""
使用 Gemini 2.0 Flash 技術進行多模態文件解析，特別針對醫療期刊進行優化。

此工具使用 LlamaParse 結合 Gemini 2.0 Flash 的多模態能力，可以：
- 精確解析文字、表格和圖表
- 保持文件的結構和格式
- 自動處理跨頁內容
- 支援複雜的醫學術語和公式

[了解更多關於 Gemini 2.0 Flash](https://www.sergey.fyi/articles/gemini-flash-2)
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
        if st.button("開始解析"):
            with st.spinner("解析中，請稍候..."):
                try:
                    # 創建輸出目錄
                    output_dir = "parsed_results"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # 執行解析
                    process_pdf(file_path, output_dir)
                    
                    # 讀取解析結果
                    output_file = os.path.join(output_dir, uploaded_file.name.replace(".pdf", ".md"))
                    with open(output_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 顯示成功訊息並提供下載按鈕
                    st.success("解析完成！請點擊下方按鈕下載結果")
                    st.download_button(
                        label="📥 下載解析結果 (Markdown)",
                        data=content,
                        file_name=uploaded_file.name.replace(".pdf", ".md"),
                        mime="text/markdown"
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
st.markdown("由 Gemini Flash 2.0 提供支持") 