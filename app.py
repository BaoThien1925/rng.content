import streamlit as st
import google.generativeai as genai
import json

# ==========================================
# 1. CẤU HÌNH TRANG (CHUYÊN NGHIỆP, TỐI GIẢN)
# ==========================================
st.set_page_config(
    page_title="Product Master Data - Coffee", 
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Thiết kế dạng Bảng (Card Layout)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
    
    /* Ẩn Header mặc định */
    header[data-testid="stHeader"] { display: none !important; }
    
    /* Nền Tối Sang Trọng (Màu Xám Đen Nhám) */
    .stApp {
        background-color: #121212 !important;
        color: #E0E0E0 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Tiêu đề */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #D4AF37 !important; /* Vàng Gold */
        text-align: center;
        font-size: 2.5rem !important;
        margin-top: 1rem !important;
    }
    h3 { color: #D4AF37 !important; }
    
    /* Khung nhập liệu (Form) */
    div[data-testid="stForm"] {
        background: #1E1E1E !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 30px !important;
    }
    
    /* Ô text gõ chữ */
    .stTextInput input, .stTextArea textarea {
        background-color: #2A2A2A !important;
        border: 1px solid #444 !important;
        color: #FFF !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 5px rgba(212, 175, 55, 0.5) !important;
    }
    
    /* Nút bấm (Button) */
    [data-testid="stFormSubmitButton"] button {
        background: #D4AF37 !important;
        color: #121212 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 0 !important;
        text-transform: uppercase;
        border: none !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: #E5C158 !important;
    }
    
    /* === THIẾT KẾ CÁC Ô KẾT QUẢ (CARDS) === */
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #D4AF37;
    }
    .metric-title {
        font-size: 12px;
        color: #9E9E9E;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 16px;
        color: #FFFFFF;
        font-weight: 500;
        word-wrap: break-word;
    }
    
    .content-box {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        color: #E0E0E0;
    }
    .content-title {
        color: #D4AF37;
        font-family: 'Playfair Display', serif;
        font-size: 20px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KẾT NỐI API & THIẾT LẬP PROMPT
# ==========================================
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY.")
    st.stop()
genai.configure(api_key=API_KEY)

# ÉP GEMINI TRẢ VỀ ĐỊNH DẠNG JSON ĐỂ CHIA Ô RÕ RÀNG
SYSTEM_INSTRUCTION = """
Bạn là Data Specialist và Content Copywriter E-commerce chuyên ngành Cà phê.
Nhiệm vụ: Phân tích Tên gốc và Thông tin thương hiệu, chuẩn hóa và trả về kết quả định dạng JSON.

QUY TẮC JSON BẮT BUỘC:
Trả về CHÍNH XÁC cấu trúc JSON sau, không được thêm bất kỳ text nào ngoài JSON:
{
  "ten_san_pham_chuan_hoa": "Chuẩn hóa theo: [Loại] + [Thương hiệu] + [Dòng] + [Đặc tính] + [Quy cách]",
  "master_data": {
    "thuong_hieu": "Tên thương hiệu",
    "gia_von": "Số VNĐ",
    "don_vi_tinh": "Gói/Túi/Hộp...",
    "khoi_luong": "Quy về kg (VD: 0,5 kg)",
    "loai_hat": "Arabica/Robusta...",
    "nguon_goc": "Vùng trồng",
    "muc_do_rang": "Rang vừa/Rang đậm...",
    "han_su_dung": "Số tháng"
  },
  "mo_ta_ngan": "1-2 câu, 30-60 từ. Không lặp tên SP, nêu bật giá trị.",
  "mo_ta_chi_tiet": "[TÊN SẢN PHẨM IN HOA]\\n\\n1. TỔNG QUAN... \\n\\n2. THÔNG SỐ..."
}

LƯU Ý: Nếu không có thông tin, ghi "Chưa cung cấp".
"""

# Tôi sử dụng gemini-1.5-flash theo nhu cầu tốc độ của bạn.
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
model = get_model()

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.markdown("<h1>TRỢ LÝ DỮ LIỆU CÀ PHÊ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#9E9E9E; margin-bottom: 30px;'>Chuẩn hóa Master Data & Content SEO chuyên nghiệp</p>", unsafe_allow_html=True)

with st.form("product_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='color:#D4AF37; font-weight:600; margin-bottom:5px;'>1. Tên Sản Phẩm Gốc</div>", unsafe_allow_html=True)
        product_name = st.text_input("", placeholder="Nhập tên từ nhà cung cấp...", label_visibility="collapsed")
    with col2:
        st.markdown("<div style='color:#D4AF37; font-weight:600; margin-bottom:5px;'>2. Thông tin từ Thương hiệu</div>", unsafe_allow_html=True)
        raw_description = st.text_area("", height=120, placeholder="Dán toàn bộ mô tả...", label_visibility="collapsed")
        
    submitted = st.form_submit_button("TẠO DỮ LIỆU CHUẨN", use_container_width=True)

# ==========================================
# 4. XỬ LÝ & HIỂN THỊ DẠNG Ô (GRID CARDS)
# ==========================================
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("⚠️ Vui lòng nhập dữ liệu!")
    else:
        with st.spinner("⏳ Đang phân tích... (Định dạng JSON)"):
            prompt_to_ai = f"TÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN THƯƠNG HIỆU:\n{raw_description}"
            
            try:
                # Ép API trả JSON
                response = model.generate_content(prompt_to_ai, generation_config={"response_mime_type": "application/json"})
                
                # Chuyển đổi kết quả AI thành Dictionary của Python
                data = json.loads(response.text)
                
                st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
                st.markdown("<h3>🎯 KẾT QUẢ ĐẦU RA</h3>", unsafe_allow_html=True)
                
                # --- PHẦN 1: TÊN SẢN PHẨM ---
                st.markdown(f"""
                <div class='content-box'>
                    <div class='metric-title'>TÊN SẢN PHẨM CHUẨN HÓA</div>
                    <div style='color:#D4AF37; font-size:22px; font-weight:bold;'>{data.get('ten_san_pham_chuan_hoa', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='color:#D4AF37; font-weight:bold; margin-top:20px; margin-bottom:10px;'>📊 MASTER DATA (THÔNG SỐ CHÍNH)</div>", unsafe_allow_html=True)
                
                # --- PHẦN 2: CHIA CÁC Ô (GRID) CHO MASTER DATA ---
                md = data.get('master_data', {})
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Thương hiệu</div><div class='metric-value'>{md.get('thuong_hieu', '')}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Khối lượng (kg)</div><div class='metric-value'>{md.get('khoi_luong', '')}</div></div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Giá vốn (VNĐ)</div><div class='metric-value'>{md.get('gia_von', '')}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Loại hạt</div><div class='metric-value'>{md.get('loai_hat', '')}</div></div>", unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Đơn vị tính</div><div class='metric-value'>{md.get('don_vi_tinh', '')}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Vùng trồng</div><div class='metric-value'>{md.get('nguon_goc', '')}</div></div>", unsafe_allow_html=True)
                with col_d:
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Mức độ rang</div><div class='metric-value'>{md.get('muc_do_rang', '')}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-card'><div class='metric-title'>Hạn sử dụng</div><div class='metric-value'>{md.get('han_su_dung', '')}</div></div>", unsafe_allow_html=True)
                
                # --- PHẦN 3: NỘI DUNG SEO ---
                st.markdown("<div style='color:#D4AF37; font-weight:bold; margin-top:20px; margin-bottom:10px;'>📝 CONTENT SEO</div>", unsafe_allow_html=True)
                
                mo_ta_chi_tiet_html = data.get('mo_ta_chi_tiet', '').replace('\n', '<br>')
                
                st.markdown(f"""
                <div class='content-box'>
                    <div class='content-title'>MÔ TẢ NGẮN</div>
                    <div style='line-height:1.6;'>{data.get('mo_ta_ngan', '')}</div>
                </div>
                
                <div class='content-box'>
                    <div class='content-title'>MÔ TẢ CHI TIẾT</div>
                    <div style='line-height:1.6;'>{mo_ta_chi_tiet_html}</div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")
