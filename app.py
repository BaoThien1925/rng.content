import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG (ĐỔI TÊN & ICON)
st.set_page_config(
    page_title="Premium Coffee - Product Master Data", 
    page_icon="☕",
    layout="wide"
)

# 2. CSS "WOW EFFECT" - HIỆU ỨNG KÍNH MỜ & HÌNH NỀN SANG TRỌNG
st.markdown("""
<style>
    /* Import 2 font chữ cao cấp từ Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Mulish:wght@400;600&display=swap');
    
    /* 1. Đổi hình nền toàn trang (Ảnh hạt cà phê chất lượng cao) + Phủ gradient tối */
    .stApp {
        background: linear-gradient(rgba(20, 10, 5, 0.7), rgba(20, 10, 5, 0.85)), 
                    url("https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2071&auto=format&fit=crop") center/cover no-repeat fixed !important;
    }
    
    /* 2. Thiết lập font chữ chung (Màu kem sáng) */
    html, body, [class*="css"], .stTextInput p, .stTextArea p {
        font-family: 'Mulish', sans-serif !important;
        color: #EFEBE9 !important; 
    }
    
    /* 3. Tiêu đề sang trọng (Playfair Display) */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #D7CCC8 !important; 
        text-shadow: 2px 2px 8px rgba(0,0,0,0.6) !important;
    }
    h1 {
        text-align: center;
        font-size: 3.2rem !important;
        margin-bottom: 0.5rem !important;
        color: #E6C49F !important; /* Màu vàng Gold */
    }
    
    /* 4. HIỆU ỨNG GLASSMORPHISM CHO KHUNG NHẬP LIỆU (Mờ ảo) */
    div[data-testid="stForm"] {
        background: rgba(30, 15, 8, 0.45) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        box-shadow: 0 15px 35px 0 rgba(0, 0, 0, 0.6) !important;
    }
    
    /* 5. Làm đẹp ô gõ chữ */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.55) !important;
        border: 1px solid #795548 !important;
        border-radius: 10px !important;
        color: #FFF !important;
        font-size: 15px !important;
        padding: 12px !important;
        transition: 0.3s;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E6C49F !important;
        box-shadow: 0 0 10px rgba(230, 196, 159, 0.4) !important;
    }

    /* 6. Nút bấm (Button) phong cách Premium */
    .stButton>button {
        background: linear-gradient(135deg, #8D6E63 0%, #4E342E 100%) !important;
        color: #FFF !important;
        border-radius: 10px !important;
        border: 1px solid #A1887F !important;
        font-family: 'Mulish', sans-serif !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 25px rgba(141, 110, 99, 0.6) !important;
        border-color: #E6C49F !important;
        color: #E6C49F !important;
    }
    
    /* 7. Khung kết quả màu sáng để dễ copy */
    div[data-testid="stTabs"] {
        background: rgba(249, 246, 240, 0.95) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        color: #3E2723 !important;
    }
    div[data-testid="stTabs"] h1, div[data-testid="stTabs"] h2, div[data-testid="stTabs"] h3 {
        color: #3E2723 !important;
        text-shadow: none !important;
    }
    div[data-testid="stTabs"] p, div[data-testid="stTabs"] li {
        color: #4E342E !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. KẾT NỐI API
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY. Vui lòng kiểm tra lại thiết lập Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. LUẬT AI XỬ LÝ DỮ LIỆU
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

# ĐÃ KHẮC PHỤC LỖI MODEL (Chuyển về chuẩn gemini-1.5-flash)
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_model()

# 5. GIAO DIỆN HIỂN THỊ
st.markdown("<h1>☕ HỆ THỐNG XỬ LÝ DỮ LIỆU SẢN PHẨM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 40px;'>Chuẩn hóa thông tin, trích xuất Master Data và tạo Content SEO cho danh mục Cà phê cao cấp.</p>", unsafe_allow_html=True)

with st.form("product_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>Tên Sản Phẩm Gốc</h3>", unsafe_allow_html=True)
        product_name = st.text_input("", placeholder="Nhập tên từ nhà cung cấp... (VD: Cà phê Arabica Cầu Đất)")
    
    with col2:
        st.markdown("<h3>Thông tin từ Thương hiệu</h3>", unsafe_allow_html=True)
        raw_description = st.text_area(
            "", 
            height=130,
            placeholder="Dán toàn bộ mô tả, tính năng, thông số vào đây..."
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("✨ Bắt đầu chuẩn hóa dữ liệu", use_container_width=True)

# 6. XỬ LÝ LOGIC
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("⚠️ Vui lòng nhập dữ liệu đầu vào trước khi xử lý!")
    else:
        with st.spinner("⏳ Máy đang rang xay dữ liệu... (Vui lòng đợi 5-10 giây)"):
            prompt_to_ai = f"TÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN DO THƯƠNG HIỆU CUNG CẤP:\n{raw_description}"
            
            try:
                response = model.generate_content(prompt_to_ai)
                
                st.markdown("<br><h3>🎯 KẾT QUẢ ĐẦU RA</h3>", unsafe_allow_html=True)
                
                tab1, tab2 = st.tabs(["👁️ Xem trước kết quả", "📋 Copy Code dán vào File/Web"])
                
                with tab1:
                    st.markdown(response.text)
                    
                with tab2:
                    st.code(response.text, language="markdown")
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
