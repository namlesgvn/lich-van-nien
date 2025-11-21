import os
import streamlit as st
from datetime import datetime
from pytz import timezone
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from lunardate import LunarDate

# --- CONSTANTS ---
THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

DS_TIET_KHI = [
    "Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
    "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
    "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
    "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập"
]

DATA_GIO_HOANG_DAO = {
    0: [0, 1, 3, 5, 7, 9], 1: [2, 4, 5, 7, 9, 10], 2: [0, 1, 4, 7, 9, 10],
    3: [0, 2, 4, 6, 8, 10], 4: [2, 4, 5, 7, 9, 10], 5: [1, 4, 6, 8, 10, 0],
    6: [0, 1, 3, 5, 7, 9], 7: [2, 4, 5, 7, 9, 10], 8: [0, 1, 4, 7, 9, 10],
    9: [0, 2, 4, 6, 8, 10], 10: [2, 4, 5, 7, 9, 10], 11: [1, 4, 6, 8, 10, 0]
}

DATA_TRUC = [
    {"ten": "Kiến", "tot": "Xuất hành, giá thú, mưu sự", "xau": "Động thổ, đào ao"},
    {"ten": "Trừ",  "tot": "Cúng tế, giải oan, chữa bệnh", "xau": "Cưới hỏi, đi xa"},
    {"ten": "Mãn",  "tot": "Cúng tế, cầu tài, khai trương", "xau": "Kiện tụng, nhậm chức"},
    {"ten": "Bình", "tot": "Sửa nhà, nhập trạch, cưới hỏi", "xau": "Đào mương, thưa kiện"},
    {"ten": "Định", "tot": "Nhập học, mua bán, động thổ", "xau": "Tố tụng, xuất quân"},
    {"ten": "Chấp", "tot": "Lập khế ước, sửa nhà, trồng trọt", "xau": "Xuất vốn, chuyển nhà"},
    {"ten": "Phá",  "tot": "Phá dỡ nhà cũ, chữa bệnh", "xau": "Cưới hỏi, khai trương"},
    {"ten": "Nguy", "tot": "Cúng tế, san đường", "xau": "Đi thuyền, leo núi, cưới hỏi"},
    {"ten": "Thành", "tot": "Khai trương, nhập học, giá thú", "xau": "Kiện tụng, tranh chấp"},
    {"ten": "Thu",  "tot": "Thu nợ, mua súc vật, cấy gặt", "xau": "Mai táng, xuất vốn"},
    {"ten": "Khai", "tot": "Cưới hỏi, khai trương, động thổ", "xau": "Chôn cất, tranh chấp"},
    {"ten": "Bế",   "tot": "Đắp đập, xây tường, an táng", "xau": "Đi xa, chữa mắt, cưới hỏi"}
]

@st.cache_resource
def load_astronomy_data():
    """Tải và cache dữ liệu thiên văn để không phải tải lại mỗi lần reload web"""
    # Skyfield tự động kiểm tra, nếu chưa có file sẽ tải về
    # Dùng load.timescale() và load('de421.bsp')
    ts = load.timescale()
    eph = load('de421.bsp')
    return ts, eph

def get_tiet_khi(date_obj):
    ts, eph = load_astronomy_data()
    
    if date_obj.tzinfo is None:
        tz = timezone('Asia/Ho_Chi_Minh')
        date_obj = tz.localize(date_obj)
    
    t = ts.from_datetime(date_obj)
    earth, sun = eph['earth'], eph['sun']
    astrometric = earth.at(t).observe(sun).apparent()
    _, lon, _ = astrometric.frame_latlon(ecliptic_frame)
    degrees = lon.degrees
    index = int(degrees // 15)
    return DS_TIET_KHI[index], degrees

def get_can_chi(can, chi):
    return f"{THIEN_CAN[can]} {DIA_CHI[chi]}"

def tinh_can_chi_ngay_julian(d, m, y):
    a = (14 - m) // 12
    y_j = y + 4800 - a
    m_j = m + 12 * a - 3
    jdn = d + (153 * m_j + 2) // 5 + 365 * y_j + y_j // 4 - y_j // 100 + y_j // 400 - 32045
    return (jdn + 9) % 10, (jdn + 1) % 12

def check_ngay_hoang_dao(thang_am, chi_ngay_idx):
    khoi_thanh_long = ((thang_am - 1) % 6) * 2
    offset = (chi_ngay_idx - khoi_thanh_long + 12) % 12
    return offset in [0, 1, 4, 5, 7, 10]

def lay_info_truc(thang_am, chi_ngay_idx):
    khoi_kien = (thang_am + 1) % 12 
    truc_idx = (chi_ngay_idx - khoi_kien + 12) % 12
    return DATA_TRUC[truc_idx]

def lay_gio_hoang_dao(chi_ngay_idx, can_ngay_idx):
    ds_indices = DATA_GIO_HOANG_DAO.get(chi_ngay_idx, [])
    ket_qua = []
    for chi_gio in ds_indices:
        can_gio = ((can_ngay_idx % 5) * 2 + chi_gio) % 10
        ten_gio = f"{DIA_CHI[chi_gio]}" # Rút gọn chỉ lấy tên chi cho bảng đỡ dài
        start = (chi_gio * 2 - 1) % 24
        end = (chi_gio * 2 + 1) % 24
        ket_qua.append(f"{ten_gio} ({start}-{end}h)")
    return ", ".join(ket_qua)

def phan_tich_ngay(date_obj):
    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    can_ngay, chi_ngay = tinh_can_chi_ngay_julian(date_obj.day, date_obj.month, date_obj.year)
    
    can_nam = (lunar.year + 6) % 10
    chi_nam = (lunar.year + 8) % 12
    can_thang = ((can_nam * 2 + 1) % 10 + lunar.month - 1) % 10
    chi_thang = (2 + lunar.month - 1) % 12

    is_hoang_dao = check_ngay_hoang_dao(lunar.month, chi_ngay)
    tiet_khi, _ = get_tiet_khi(date_obj)
    info_truc = lay_info_truc(lunar.month, chi_ngay)
    
    return {
        "duong_lich": date_obj.strftime("%d/%m/%Y"),
        "am_lich_str": f"{lunar.day}/{lunar.month}",
        "am_lich_full": f"{lunar.day}/{lunar.month}/{lunar.year}",
        "can_chi_ngay": get_can_chi(can_ngay, chi_ngay),
        "can_chi_thang": get_can_chi(can_thang, chi_thang),
        "can_chi_nam": get_can_chi(can_nam, chi_nam),
        "tiet_khi": tiet_khi,
        "is_hoang_dao": is_hoang_dao,
        "loai_ngay": "Hoàng Đạo" if is_hoang_dao else "Hắc Đạo",
        "gio_tot": lay_gio_hoang_dao(chi_ngay, can_ngay),
        "truc_ten": info_truc['ten'],
        "viec_tot": info_truc['tot'],
        "viec_xau": info_truc['xau']
    }
