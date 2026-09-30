import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG STREAMLIT (SỬA ICON)
st.set_page_config(
    page_title="Product Master Data - Coffee Edition", 
    page_icon="☕",
    layout="wide"
)

# 2. CSS CUSTOM CHO TYPOGRAPHY & HIERARCHY (COFFEE THEME)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,500&family=Mulish:wght@400;600&display=swap');
    
    /* Ghi đè Font chữ chung */
    html, body, [class*="css"] {
        font-family: 'Mulish', sans-serif;
    }
    
    /* Font cho các Tiêu đề (Hierarchy) */
    h1, h2, h3 {
        font-family: 'Lora', serif !important;
        color: #3E2723 !important;
    }
    
    /* Căn chỉnh khoảng cách Title */
    .stApp > header {
        background-color: transparent !important;
    }
    
    /* Chỉnh nút bấm thành màu Espresso */
    .stButton>button {
        background-color: #4E342E !important;
        color: #F9F6F0 !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #3E2723 !important;
        box-shadow: 0 4px 12px rgba(62, 39, 35, 0.2) !important;
    }
    
    /* Định dạng lại khối kết quả */
    .stMarkdown p {
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY. Vui lòng kiểm tra lại thiết lập Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 3. SIÊU CÂU LỆNH (SUPER PROMPT)
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

# KHẮC PHỤC LỖI MODEL 404 BẰNG 'gemini-1.5-flash-latest'
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_model()

# 4. GIAO DIỆN NGƯỜI DÙNG
st.title("☕ Hệ Thống Xử Lý Dữ Liệu Sản Phẩm")
st.markdown("*Chuẩn hóa thông tin, trích xuất Master Data và tạo Content SEO cho danh mục Cà phê.*")
st.divider()

with st.form("product_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tên Sản Phẩm Gốc")
        product_name = st.text_input("Nhập tên từ nhà cung cấp:", placeholder="VD: Cà phê Arabica Cầu Đất...")
    
    with col2:
        st.subheader("Thông tin từ Thương hiệu")
        raw_description = st.text_area(
            "Nhập toàn bộ mô tả, tính năng, thông số:", 
            height=150,
            placeholder="Dán toàn bộ thông tin nhà cung cấp đưa vào đây..."
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("☕ Xử lý Dữ liệu Ngay", use_container_width=True)

# 5. XỬ LÝ & HIỂN THỊ
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("Vui lòng nhập dữ liệu đầu vào!")
    else:
        with st.spinner("Đang rang xay dữ liệu... (Vui lòng đợi 5-10 giây)"):
            prompt_to_ai = f"TÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN DO THƯƠNG HIỆU CUNG CẤP:\n{raw_description}"
            
            try:
                response = model.generate_content(prompt_to_ai)
                st.success("✨ Cà phê đã pha xong! Dữ liệu của bạn đây:")
                
                tab1, tab2 = st.tabs(["👁️ Xem trước hiển thị", "📋 Copy để dán vào File/Web"])
                
                with tab1:
                    st.markdown(response.text)
                    
                with tab2:
                    st.code(response.text, language="markdown")
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
