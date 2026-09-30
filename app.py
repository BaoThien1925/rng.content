import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG CHÍNH
st.set_page_config(
    page_title="Premium Coffee - Product Data", 
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS CAO CẤP (GLASSMORPHISM & COFFEE THEME)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Mulish:wght@400;600&display=swap');
    
    /* Ẩn hoàn toàn dải màu trắng (Header) của Streamlit gây mờ chữ */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Hình nền toàn trang (Hạt cà phê tối màu) */
    .stApp {
        background-color: rgba(15, 8, 5, 0.95);
        background-image: url("https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2071&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-blend-mode: multiply; /* Làm tối nền mạnh để nổi bật chữ */
    }
    
    /* Font chữ chung: Màu trắng ngà */
    html, body, [class*="css"], p, span, label, div {
        font-family: 'Mulish', sans-serif !important;
        color: #FDF7F2 !important; 
    }
    
    /* Tiêu đề: Font tạp chí, màu vàng Gold rực rỡ */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #D4AF37 !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9) !important;
    }
    h1 {
        text-align: center;
        font-size: 3.2rem !important;
        margin-top: -2rem !important;
    }
    
    /* Khung nhập liệu (Form): Kính mờ (Glassmorphism) */
    div[data-testid="stForm"] {
        background: rgba(15, 8, 5, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8) !important;
    }
    
    /* Ô text gõ chữ: Đen nhạt, chữ trắng sáng */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid #8D6E63 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        padding: 15px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.5) !important;
    }
    
    /* Nút bấm nổi bật (Vàng Gold xịn) */
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
        color: #1A100C !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        text-transform: uppercase;
        border-radius: 8px !important;
        padding: 10px 0 !important;
        transition: 0.3s;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.5) !important;
    }
    
    /* Khung kết quả AI: Nền trắng sáng để copy dễ dàng */
    div[data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        padding: 25px !important;
        margin-top: 20px !important;
    }
    div[data-testid="stTabs"] * {
        color: #1A100C !important;
        text-shadow: none !important;
    }
    div[data-testid="stTabs"] h1, div[data-testid="stTabs"] h2, div[data-testid="stTabs"] h3 {
        color: #4E342E !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. KẾT NỐI API GEMINI
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY. Vui lòng kiểm tra lại thiết lập Secrets trên Streamlit Cloud.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. LUẬT AI XỬ LÝ DỮ LIỆU (SUPER PROMPT)
SYSTEM_INSTRUCTION = """
Bạn là một Chuyên gia Đa nhiệm (Quản trị danh mục sản phẩm, SEO E-commerce, Data Analyst và Content Copywriter) chuyên ngành Cà phê & Đồ uống.
Nhiệm vụ của bạn là tiếp nhận "Tên sản phẩm gốc" và "Thông tin thương hiệu", sau đó xử lý và trả về MỘT KẾT QUẢ DUY NHẤT chứa toàn bộ dữ liệu đã được chuẩn hóa.

QUY TẮC CỐ ĐỊNH CHUNG:
- CHỈ sử dụng thông tin có trong dữ liệu đầu vào. Không tự bịa, không suy đoán.
- TUYỆT ĐỐI không chào hỏi, không giải thích.
- Chỉ trả về kết quả theo đúng CẤU TRÚC ĐẦU RA BẮT BUỘC dưới đây.

--- BỘ QUY TẮC XỬ LÝ ---
1. TÊN SẢN PHẨM CHUẨN HÓA:
- Cấu trúc: [Loại sản phẩm] + [Thương hiệu] + [Tên/Dòng sản phẩm] + [Đặc tính phân biệt] + [Quy cách].
- Độ dài: 50-80 ký tự. Đưa loại sản phẩm lên đầu. Viết hoa đúng tên thương hiệu.

2. TRƯỜNG DỮ LIỆU (MASTER DATA):
- Nếu không có thông tin, ghi: "Chưa cung cấp".
- Khối lượng: Bắt buộc đổi về kg (VD: 250g -> 0,25 kg).
- Hạn sử dụng: Bắt buộc đổi về số tháng (VD: 1 năm -> 12).
- Giá vốn: Chỉ ghi số tiền VNĐ.

3. MÔ TẢ NGẮN:
- 1-2 câu, 30-60 từ. Nêu bản chất, điểm nổi bật. Không cường điệu.

4. MÔ TẢ CHI TIẾT:
- Đặt TÊN SẢN PHẨM IN HOA ở dòng đầu tiên.
- Trình bày thành các mục đánh số, TIÊU ĐỀ IN HOA (1. TỔNG QUAN, 2. ĐẶC ĐIỂM...).
- Bắt buộc phải có mục THÔNG SỐ / THÀNH PHẦN.

--- CẤU TRÚC ĐẦU RA BẮT BUỘC ---

**TÊN SẢN PHẨM CHUẨN HÓA**
[Kết quả Tên sản phẩm]

**MASTER DATA**
- Thương hiệu: [Kết quả]
- Giá vốn (VNĐ): [Kết quả]
- Đơn vị tính: [Kết quả]
- Khối lượng (kg): [Kết quả]
- Loại hạt: [Kết quả]
- Nguồn gốc / Vùng trồng: [Kết quả]
- Mức độ rang: [Kết quả]
- Hạn sử dụng (tháng): [Kết quả]

**MÔ TẢ NGẮN**
[Kết quả Mô tả ngắn]

**MÔ TẢ CHI TIẾT**
[TÊN SẢN PHẨM IN HOA]
1. [TIÊU ĐỀ 1]
[Nội dung]
"""

# KHỞI TẠO MODEL "gemini-1.5-flash" ĐỂ TRÁNH LỖI 404
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_model()

# 5. GIAO DIỆN HIỂN THỊ
st.markdown("<h1>☕ TRỢ LÝ XỬ LÝ DỮ LIỆU CÀ PHÊ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 40px; color: #D7CCC8 !important;'>Hệ thống chuẩn hóa Master Data & Content SEO chuyên nghiệp.</p>", unsafe_allow_html=True)

with st.form("product_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: left; margin-bottom: 10px;'>Tên Sản Phẩm Gốc</h3>", unsafe_allow_html=True)
        product_name = st.text_input("Nhập tên từ nhà cung cấp:", placeholder="VD: Cà phê Arabica Cầu Đất Blend 500g...", label_visibility="collapsed")
    
    with col2:
        st.markdown("<h3 style='text-align: left; margin-bottom: 10px;'>Thông tin từ Thương hiệu</h3>", unsafe_allow_html=True)
        raw_description = st.text_area(
            "Dán toàn bộ mô tả:", 
            height=130,
            placeholder="Dán toàn bộ mô tả, tính năng, quy cách vào đây...",
            label_visibility="collapsed"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("✨ TẠO DỮ LIỆU CHUẨN", use_container_width=True)

# 6. XỬ LÝ LOGIC
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("⚠️ Vui lòng nhập dữ liệu đầu vào trước khi xử lý!")
    else:
        with st.spinner("⏳ Đang phân tích và pha chế nội dung... (Vui lòng đợi 5-10 giây)"):
            prompt_to_ai = f"TÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN DO THƯƠNG HIỆU CUNG CẤP:\n{raw_description}"
            
            try:
                response = model.generate_content(prompt_to_ai)
                
                st.markdown("<br><h1>🎯 KẾT QUẢ ĐẦU RA</h1>", unsafe_allow_html=True)
                
                tab1, tab2 = st.tabs(["👁️ Xem trước kết quả", "📋 Copy Code (Dán vào File/Web)"])
                
                with tab1:
                    st.markdown(response.text)
                    
                with tab2:
                    st.code(response.text, language="markdown")
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình kết nối AI: {e}")
