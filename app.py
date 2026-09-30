import streamlit as st
import google.generativeai as genai
import json

# ==========================================
# 1. CẤU HÌNH TRANG: MODERN LIGHT SAAS
# ==========================================
st.set_page_config(
    page_title="Product Master Data", 
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    header[data-testid="stHeader"] { display: none !important; }
    
    .stApp {
        background-color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }
    
    h1, h2, h3 { font-family: 'Inter', sans-serif !important; color: #1E293B !important; font-weight: 700 !important; }
    
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 32px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        padding: 12px !important;
        transition: 0.2s ease;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        background-color: #FFFFFF !important;
        border-color: #8B5A2B !important;
        box-shadow: 0 0 0 3px rgba(139, 90, 43, 0.15) !important;
    }
    
    [data-testid="stFormSubmitButton"] button {
        background-color: #8B5A2B !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: 0.2s ease;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #6F4520 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 90, 43, 0.3) !important;
    }
    
    .grid-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 4px solid #8B5A2B;
    }
    .grid-label {
        font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;
    }
    .grid-value { font-size: 16px; color: #0F172A; font-weight: 600; }
    
    .content-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .content-title {
        color: #1E293B; font-size: 18px; font-weight: 700; border-bottom: 2px solid #F1F5F9; padding-bottom: 12px; margin-bottom: 16px;
    }
    .content-body { color: #334155; line-height: 1.7; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HÀM XỬ LÝ CHUỖI VÀ API
# ==========================================
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY.")
    st.stop()
genai.configure(api_key=API_KEY)

def parse_json_safely(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())

SYSTEM_INSTRUCTION = """
Bạn là Data Specialist và Content Copywriter E-commerce chuyên ngành Cà phê.
Nhiệm vụ: Phân tích Tên gốc và Thông tin thương hiệu, chuẩn hóa và trả về kết quả ĐÚNG CHUẨN JSON SAU ĐÂY. KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO BÊN NGOÀI JSON:
{
  "ten_san_pham_chuan_hoa": "[Loại] + [Thương hiệu] + [Dòng] + [Đặc tính] + [Quy cách]",
  "master_data": {
    "thuong_hieu": "Tên",
    "gia_von": "Số VNĐ",
    "don_vi_tinh": "Gói/Túi/Hộp",
    "khoi_luong": "kg",
    "loai_hat": "Loại hạt",
    "nguon_goc": "Vùng trồng",
    "muc_do_rang": "Mức rang",
    "han_su_dung": "Số tháng"
  },
  "mo_ta_ngan": "1-2 câu, 30-60 từ.",
  "mo_ta_chi_tiet": "[TÊN SẢN PHẨM IN HOA]\\n\\n1. TỔNG QUAN... \\n\\n2. THÔNG SỐ..."
}
Nếu không có thông tin, ghi "Chưa cung cấp".
"""

# ==========================================
# 3. GIAO DIỆN
# ==========================================
st.markdown("<h1 style='text-align: center; margin-top: 1rem;'>HỆ THỐNG MASTER DATA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748B; margin-bottom: 2rem;'>Chuẩn hóa dữ liệu Catalog & Content E-commerce</p>", unsafe_allow_html=True)

with st.form("product_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='font-weight:600; margin-bottom:8px; color:#1E293B;'>Tên Sản Phẩm Gốc</div>", unsafe_allow_html=True)
        product_name = st.text_input("", placeholder="Nhập tên từ nhà cung cấp...", label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-weight:600; margin-bottom:8px; color:#1E293B;'>Thông tin từ Thương hiệu</div>", unsafe_allow_html=True)
        raw_description = st.text_area("", height=120, placeholder="Dán toàn bộ mô tả...", label_visibility="collapsed")
        
    submitted = st.form_submit_button("TIẾN HÀNH CHUẨN HÓA DỮ LIỆU", use_container_width=True)

# ==========================================
# 4. THUẬT TOÁN AUTO-MODEL VÀ XỬ LÝ DỮ LIỆU
# ==========================================
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("⚠️ Vui lòng nhập dữ liệu!")
    else:
        with st.spinner("⏳ Đang tự động dò tìm Model phù hợp và xử lý dữ liệu..."):
            try:
                # 1. TỰ ĐỘNG DÒ TÌM MODEL (KHÔNG BAO GIỜ BỊ LỖI 404 NỮA)
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not available_models:
                    st.error("Tài khoản của bạn hiện không có quyền truy cập model nào từ Google.")
                    st.stop()
                
                # Ưu tiên chọn model có chữ "flash" (nhanh nhất)
                target_model = available_models[0]
                for m in available_models:
                    if 'flash' in m.lower():
                        target_model = m
                        break
                        
                # 2. XỬ LÝ VỚI MODEL ĐÃ TÌM ĐƯỢC
                model = genai.GenerativeModel(target_model)
                prompt_to_ai = f"{SYSTEM_INSTRUCTION}\n\nTÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN THƯƠNG HIỆU:\n{raw_description}"
                
                response = model.generate_content(prompt_to_ai)
                
                # 3. HIỂN THỊ KẾT QUẢ DẠNG KHUNG
                try:
                    data = parse_json_safely(response.text)
                    
                    st.markdown("<h2 style='margin-top: 30px; margin-bottom: 20px;'>Kết Quả Đầu Ra</h2>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class='content-card'>
                        <div class='grid-label'>TÊN SẢN PHẨM CHUẨN HÓA</div>
                        <div style='color:#0F172A; font-size:24px; font-weight:700;'>{data.get('ten_san_pham_chuan_hoa', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<h3 style='font-size:18px; margin: 24px 0 16px 0; color:#334155;'>📊 THÔNG SỐ MASTER DATA</h3>", unsafe_allow_html=True)
                    md = data.get('master_data', {})
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Thương hiệu</div><div class='grid-value'>{md.get('thuong_hieu', '')}</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Khối lượng (kg)</div><div class='grid-value'>{md.get('khoi_luong', '')}</div></div>", unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Giá vốn (VNĐ)</div><div class='grid-value'>{md.get('gia_von', '')}</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Loại hạt</div><div class='grid-value'>{md.get('loai_hat', '')}</div></div>", unsafe_allow_html=True)
                    with col_c:
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Đơn vị tính</div><div class='grid-value'>{md.get('don_vi_tinh', '')}</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Vùng trồng</div><div class='grid-value'>{md.get('nguon_goc', '')}</div></div>", unsafe_allow_html=True)
                    with col_d:
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Mức độ rang</div><div class='grid-value'>{md.get('muc_do_rang', '')}</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='grid-card'><div class='grid-label'>Hạn sử dụng</div><div class='grid-value'>{md.get('han_su_dung', '')}</div></div>", unsafe_allow_html=True)
                    
                    st.markdown("<h3 style='font-size:18px; margin: 24px 0 16px 0; color:#334155;'>📝 NỘI DUNG SEO WEBSITE</h3>", unsafe_allow_html=True)
                    mo_ta_chi_tiet_html = data.get('mo_ta_chi_tiet', '').replace('\n', '<br>')
                    
                    st.markdown(f"""
                    <div class='content-card'>
                        <div class='content-title'>MÔ TẢ NGẮN</div>
                        <div class='content-body'>{data.get('mo_ta_ngan', '')}</div>
                    </div>
                    <div class='content-card'>
                        <div class='content-title'>MÔ TẢ CHI TIẾT</div>
                        <div class='content-body'>{mo_ta_chi_tiet_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as parse_err:
                    st.warning("AI không trả về định dạng bảng chuẩn, dưới đây là kết quả thô:")
                    st.markdown(f"<div class='content-card'>{response.text}</div>", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Lỗi kết nối API: {e}")
