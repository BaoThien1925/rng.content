import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="Hệ thống Xử lý Dữ liệu Sản phẩm (Master Data & Content)", 
    page_icon="📦",
    layout="wide" # Mở rộng giao diện cho dễ nhìn
)

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY. Vui lòng thêm vào cấu hình Secrets trên Streamlit Cloud.")
    st.stop()

genai.configure(api_key=API_KEY)

# 2. SIÊU CÂU LỆNH (SUPER PROMPT) - GỘP CẢ 3 YÊU CẦU CỦA BẠN
SYSTEM_INSTRUCTION = """
Bạn là một Chuyên gia Đa nhiệm (Quản trị danh mục sản phẩm, SEO E-commerce, Data Analyst và Content Copywriter).
Nhiệm vụ của bạn là tiếp nhận "Tên sản phẩm gốc" và "Thông tin thương hiệu cung cấp", sau đó xử lý và trả về MỘT KẾT QUẢ DUY NHẤT chứa toàn bộ dữ liệu đã được chuẩn hóa.

QUY TẮC CỐ ĐỊNH CHUNG:
- CHỈ sử dụng thông tin có trong dữ liệu đầu vào. Không tự bịa, không suy đoán.
- TUYỆT ĐỐI không chào hỏi, không giải thích, không đưa ra nhiều phương án.
- Chỉ trả về kết quả theo đúng CẤU TRÚC ĐẦU RA BẮT BUỘC dưới đây.

--- BỘ QUY TẮC XỬ LÝ ---

1. TÊN SẢN PHẨM CHUẨN HÓA:
- Cấu trúc: [Loại sản phẩm] + [Thương hiệu] + [Tên/Dòng sản phẩm] + [Đặc tính phân biệt] + [Quy cách].
- Độ dài: 50-80 ký tự. Đưa loại sản phẩm lên đầu. Không nhồi nhét từ khóa (Giá rẻ, Hot...).
- Viết hoa đúng tên thương hiệu, không viết hoa toàn bộ. Không dùng chấm kết thúc.

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
- Không dùng các câu như "Theo thông tin thương hiệu...". Viết trực diện như trang sản phẩm thật.

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
...
"""

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_model()

# 3. GIAO DIỆN CHUYÊN NGHIỆP CHO B, C, D
st.title("📦 Tool Xử Lý Dữ Liệu Sản Phẩm Chuẩn SEO")
st.markdown("Nhập tên gốc và thông tin từ hãng, AI sẽ tự động xuất ra Tên chuẩn, Master Data và Content chi tiết.")

with st.form("product_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Tên Sản Phẩm Gốc")
        product_name = st.text_input("Nhập tên sản phẩm gốc:", placeholder="VD: Cà phê sáng tạo 1 340g Trung Nguyên")
    
    with col2:
        st.subheader("2. Thông tin từ Thương hiệu")
        raw_description = st.text_area(
            "Nhập toàn bộ mô tả, tính năng, thông số:", 
            height=200,
            placeholder="Dán toàn bộ thông tin nhà cung cấp đưa vào đây..."
        )
        
    submitted = st.form_submit_button("🚀 Xử lý Toàn bộ Dữ liệu", type="primary", use_container_width=True)

# 4. XỬ LÝ & HIỂN THỊ
if submitted:
    if not product_name.strip() and not raw_description.strip():
        st.warning("Vui lòng nhập dữ liệu đầu vào!")
    else:
        with st.spinner("AI đang phân tích, chuẩn hóa tên, trích xuất dữ liệu và viết content... (Có thể mất 5-10 giây)"):
            prompt_to_ai = f"TÊN SẢN PHẨM GỐC:\n{product_name}\n\nTHÔNG TIN DO THƯƠNG HIỆU CUNG CẤP:\n{raw_description}"
            
            try:
                response = model.generate_content(prompt_to_ai)
                st.success("Hoàn thành!")
                
                st.subheader("🎯 KẾT QUẢ ĐẦU RA")
                
                tab1, tab2 = st.tabs(["👁️ Xem trước kết quả", "📋 Copy để dán vào File/Web"])
                
                with tab1:
                    st.markdown(response.text)
                    
                with tab2:
                    st.code(response.text, language="markdown")
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
