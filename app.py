import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Running Reward Tracker",
    page_icon="🏃",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Initial Session State (จำลองฐานข้อมูลใน Memory)
# -----------------------------------------------------------------------------
if 'users' not in st.session_state:
    # เก็บข้อมูลผู้ใช้งาน: {ชื่อ: ระยะทางสะสมคงเหลือ}
    st.session_state['users'] = {}

if 'runs' not in st.session_state:
    # บันทึกการวิ่ง
    st.session_state['runs'] = []

if 'redemptions' not in st.session_state:
    # บันทึกประวัติการแลกของรางวัล
    st.session_state['redemptions'] = []

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("🏃 ระบบสะสมระยะวิ่งแลกอาหาร 🍕")
st.caption("สะสมระยะทางเพื่อแลกรางวัล: 🍧 ของหวาน (5 km) | 🥩 บุฟเฟต์ (10 km)")

# -----------------------------------------------------------------------------
# Sidebar: บันทึกการวิ่งใหม่ & แลกของรางวัล
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("📌 เมนูจัดการ")
    
    # --- ส่วนที่ 1: บันทึกการวิ่ง ---
    st.subheader("1. บันทึกการวิ่ง")
    run_date = st.date_input("วันที่วิ่ง", datetime.now())
    run_time = st.time_input("เวลาที่วิ่ง", datetime.now().time())
    runner_name = st.text_input("ชื่อผู้วิ่ง").strip()
    distance = st.number_input("ระยะทาง (กิโลเมตร)", min_value=0.1, step=0.5, format="%.2f")
    
    if st.button("➕ บันทึกระยะวิ่ง", use_container_width=True):
        if runner_name:
            run_datetime = f"{run_date} {run_time.strftime('%H:%M')}"
            
            # บันทึกประวัติการวิ่ง
            st.session_state['runs'].append({
                "วัน-เวลา": run_datetime,
                "ชื่อผู้วิ่ง": runner_name,
                "ระยะทาง (km)": distance
            })
            
            # อัปเดตรยพสะสมของผู้ใช้งาน
            current_dist = st.session_state['users'].get(runner_name, 0.0)
            st.session_state['users'][runner_name] = current_dist + distance
            
            st.success(f"บันทึกวิ่ง {distance} km ให้คุณ {runner_name} เรียบร้อย!")
            st.rerun()
        else:
            st.warning("กรุณากรอกชื่อผู้วิ่ง")

    st.divider()

    # --- ส่วนที่ 2: แลกของรางวัล ---
    st.subheader("2. แลกของรางวัล")
    available_users = list(st.session_state['users'].keys())
    
    if available_users:
        selected_user = st.selectbox("เลือกผู้ใช้งาน", available_users)
        user_points = st.session_state['users'].get(selected_user, 0.0)
        st.info(f"ระยะสะสมคงเหลือ: **{user_points:.2f} km**")

        reward = st.selectbox("เลือกรางวัลที่ต้องการแลก", [
            "🍧 ของหวาน (ใช้ 5 km)",
            "🥩 บุฟเฟต์ (ใช้ 10 km)"
        ])
        
        cost = 5.0 if "ของหวาน" in reward else 10.0
        
        if st.button("🎁 แลกของรางวัล", use_container_width=True):
            if user_points >= cost:
                st.session_state['users'][selected_user] -= cost
                redeem_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # บันทึกประวัติการแลก
                st.session_state['redemptions'].append({
                    "วัน-เวลา": redeem_datetime,
                    "ชื่อผู้ใช้": selected_user,
                    "รางวัลที่แลก": reward,
                    "ระยะทางที่ใช้ (km)": cost,
                    "ระยะสะสมคงเหลือ (km)": st.session_state['users'][selected_user]
                })
                
                st.balloons()
                st.success(f"แลกสำเร็จ! คุณ {selected_user} ได้รับ {reward}")
                st.rerun()
            else:
                st.error(f"ระยะทางสะสมไม่เพียงพอ (ขาดอีก {cost - user_points:.2f} km)")
    else:
        st.write("ยังไม่มีข้อมูลผู้ใช้งาน")

# -----------------------------------------------------------------------------
# Main Dashboard: แสดงข้อมูลและประวัติ
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 ตารางคะแนนสะสมคงเหลือ")
    if st.session_state['users']:
        user_df = pd.DataFrame([
            {"ชื่อ": name, "ระยะสะสมคงเหลือ (km)": f"{dist:.2f}"}
            for name, dist in st.session_state['users'].items()
        ])
        st.dataframe(user_df, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีข้อมูลการสะสมระยะทาง")

with col2:
    tab1, tab2 = st.tabs(["📜 ประวัติการวิ่ง", "🎁 ประวัติการแลกรางวัล"])
    
    with tab1:
        if st.session_state['runs']:
            st.dataframe(pd.DataFrame(st.session_state['runs']), use_container_width=True, hide_index=True)
        else:
            st.write("ยังไม่มีประวัติการวิ่ง")
            
    with tab2:
        if st.session_state['redemptions']:
            st.dataframe(pd.DataFrame(st.session_state['redemptions']), use_container_width=True, hide_index=True)
        else:
            st.write("ยังไม่มีประวัติการแลกรางวัล")
