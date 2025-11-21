import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from logic import phan_tich_ngay

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Lịch Vạn Niên - LeNamVN",
    page_icon="📅",
    layout="wide"
)

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .main {background-color: #f5f7f9;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
    .hoang-dao {color: #d9534f; font-weight: bold; border: 1px solid #d9534f; padding: 2px 8px; border-radius: 5px;}
    .hac-dao {color: #6c757d; font-weight: bold; border: 1px solid #6c757d; padding: 2px 8px; border-radius: 5px;}
    h1 {color: #2c3e50;}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("📅 Lịch Vạn Niên Online")
st.write("Tra cứu ngày tốt xấu, tiết khí và giờ hoàng đạo.")
st.divider()

# --- CHỌN NGÀY ---
col_pick, col_empty = st.columns([1, 3])
with col_pick:
    selected_date = st.date_input("Chọn ngày xem:", datetime.now())

# Chuyển đổi sang datetime object để xử lý
current_date = datetime.combine(selected_date, datetime.min.time())

# --- XỬ LÝ DỮ LIỆU NGÀY ĐANG CHỌN ---
data = phan_tich_ngay(current_date)

# --- HIỂN THỊ THÔNG TIN CHI TIẾT ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Thông tin thời gian")
    c1, c2 = st.columns(2)
    c1.metric("Dương lịch", data['duong_lich'])
    c2.metric("Âm lịch", data['am_lich_full'])
    
    st.markdown(f"""
    * **Can Chi:** Ngày {data['can_chi_ngay']} | Tháng {data['can_chi_thang']} | Năm {data['can_chi_nam']}
    * **Tiết khí:** {data['tiet_khi']}
    * **Trực:** {data['truc_ten']}
    """)
    
    if data['is_hoang_dao']:
        st.markdown('<span class="hoang-dao">★ NGÀY HOÀNG ĐẠO (TỐT)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="hac-dao">● NGÀY HẮC ĐẠO (THƯỜNG/XẤU)</span>', unsafe_allow_html=True)

with col2:
    st.subheader("Việc nên làm & Giờ tốt")
    with st.container(border=True):
        st.write(f"**✅ Nên làm:** {data['viec_tot']}")
        st.write(f"**❌ Kiêng kỵ:** {data['viec_xau']}")
        st.divider()
        st.write(f"**⏰ Giờ hoàng đạo:**")
        st.info(data['gio_tot'])

# --- BẢNG 30 NGÀY TỚI ---
st.divider()
st.header("🗓️ Danh sách Ngày Hoàng Đạo (30 ngày tới)")

list_days = []
temp_date = current_date
for i in range(1, 31):
    temp_date += timedelta(days=1)
    info = phan_tich_ngay(temp_date)
    
    # Chỉ lấy ngày hoàng đạo
    if info['is_hoang_dao']:
        list_days.append({
            "Dương lịch": info['duong_lich'],
            "Âm lịch": info['am_lich_str'],
            "Can Chi Ngày": info['can_chi_ngay'],
            "Trực": info['truc_ten'],
            "Việc Nên Làm": info['viec_tot'],
            "Giờ Tốt": info['gio_tot']
        })

if list_days:
    df = pd.DataFrame(list_days)
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Việc Nên Làm": st.column_config.TextColumn(width="medium"),
            "Giờ Tốt": st.column_config.TextColumn(width="medium"),
        }
    )
else:
    st.warning("Không tìm thấy ngày hoàng đạo nào trong 30 ngày tới (Điều này rất hiếm khi xảy ra).")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: grey;'>Phát triển bởi LeNamVN | Dữ liệu Skyfield</div>", unsafe_allow_html=True)
