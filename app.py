import streamlit as st
import pandas as pd

# ==========================================
# Математичні функції
# ==========================================


def zmishyvach(Gr, Ck, Ci, Gv):
    """Змішувач перед мембраною"""
    Gi = Gv - Gr
    if Gv > 0:
        Cv = (Gr * Ck + Gi * Ci) / Gv
    else:
        Cv = Ci
    return Gi, Cv


def rozdiluvach(Gk, Xr):
    """Розділювач"""
    Gr = Gk * Xr
    Gs = Gk - Gr
    return Gr, Gs


def membrana(Gv, Cv, Xob, Xp):
    """Мембрана"""
    Gp = Gv * Xp
    Gk = Gv - Gp
    Cp = Cv * (1 - Xob)
    if Gk > 0:
        Ck = (Gv * Cv - Gp * Cp) / Gk
    else:
        Ck = Cv
    return Gp, Cp, Gk, Ck


def zmish2(Gr1, Ck1, Gr2, Ck2):
    """Змішувач двох циркуляційних потоків"""
    Gr = Gr1 + Gr2
    if Gr > 0:
        Ck = (Gr1 * Ck1 + Gr2 * Ck2) / Gr
    else:
        Ck = 0
    return Gr, Ck

# ==========================================
# Інтерфейс користувача Streamlit
# ==========================================


st.set_page_config(page_title="Калькулятор ЗО", layout="wide")
st.title("💧 Калькулятор зворотного осмосу")

system_type = st.radio("Оберіть конфігурацію:", [
                       "Одноступенева", "Двоступенева (по пермеату)"])

st.sidebar.header("Вихідні дані")
Gv_in = st.sidebar.number_input("Gv (м3/год)", value=1.0)
Ci_in = st.sidebar.number_input("Ci (мг/дм3)", value=1500.0)
Xob_in = st.sidebar.number_input("Xob (коеф. затримки)", value=0.99)
Xr1_in = st.sidebar.number_input("X рец 1 (xr1)", value=0.2)
Xp_in = st.sidebar.number_input("X перм (xp)", value=0.2)

if system_type == "Двоступенева (по пермеату)":
    Xr2_in = st.sidebar.number_input("X рец 2 (xr2)", value=0.25)
else:
    Xr2_in = 0.0

# ==========================================
# Розрахунок
# ==========================================

if st.button("🚀 Виконати розрахунок"):
    max_iter = 100
    tol = 1e-6

    if system_type == "Одноступенева":
        Gr_curr = 0.1
        Ck_curr = Ci_in * 1.5

        for i in range(max_iter):
            Gi, Cv = zmishyvach(Gr_curr, Ck_curr, Ci_in, Gv_in)
            Gp, Cp, Gk, Ck_new = membrana(Gv_in, Cv, Xob_in, Xp_in)
            Gr_new, Gkk1 = rozdiluvach(Gk, Xr1_in)

            if abs(Ck_new - Ck_curr) < tol:
                break
            Gr_curr, Ck_curr = Gr_new, Ck_new

        st.success("✅ Розрахунок завершено!")

        # Виведення в стилі таблиць Excel
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Змішувач")
            st.write(f"**Gv:** {Gv_in:.2f} | **Ci:** {Ci_in:.2f}")
            st.write(f"**Gi:** {Gi:.2f} | **Cv:** {Cv:.2f}")
        with col2:
            st.markdown("### Мембрана 1")
            st.write(f"**Gp:** {Gp:.2f} | **Gk:** {Gk:.2f}")
            st.write(f"**Cp:** {Cp:.2f} | **Ck:** {Ck_new:.2f}")
        with col3:
            st.markdown("### Розділювач 1")
            st.write(f"**Gr:** {Gr_new:.2f} | **Gkk:** {Gkk1:.2f}")

    elif system_type == "Двоступенева (по пермеату)":
        # Початкові значення
        Gr1_curr, Ck1_curr = 0.1, Ci_in * 1.2
        Gr2_curr, Ck2_curr = 0.1, Ci_in * 0.1

        for i in range(max_iter):
            # 1. Змішувач 2 (Сума рециркуляцій)
            Gr_sum, Ck_sum = zmish2(Gr1_curr, Ck1_curr, Gr2_curr, Ck2_curr)

            # 2. Змішувач 1 (Головний)
            Gi, Cv = zmishyvach(Gr_sum, Ck_sum, Ci_in, Gv_in)

            # 3. Мембрана 1
            Gp1, Cp1, Gk1, Ck1_new = membrana(Gv_in, Cv, Xob_in, Xp_in)

            # 4. Розділювач 1
            Gr1_new, Gkk1 = rozdiluvach(Gk1, Xr1_in)

            # 5. Мембрана 2
            Gp2, Cp2, Gk2, Ck2_new = membrana(Gp1, Cp1, Xob_in, Xp_in)

            # 6. Розділювач 2
            Gr2_new, Gkk2 = rozdiluvach(Gk2, Xr2_in)

            # Перевірка збіжності
            if abs(Ck1_new - Ck1_curr) < tol and abs(Ck2_new - Ck2_curr) < tol:
                break

            Gr1_curr, Ck1_curr = Gr1_new, Ck1_new
            Gr2_curr, Ck2_curr = Gr2_new, Ck2_new

        st.success(f"✅ Розрахунок зійшовся за {i+1} ітерацій!")

        # Візуалізація результатів у вигляді блоків (як в Excel)
        st.divider()

        # --- ПЕРШИЙ РЯДОК БЛОКІВ ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Змішувач 1")
            st.write(f"**Gv:** {Gv_in:.2f} | **Ci:** {Ci_in:.2f}")
            st.write(f"**Gi:** {Gi:.2f} | **Cv:** {Cv:.2f}")

        with col2:
            st.markdown("### Мембрана 1")
            st.write(f"**Gp:** {Gp1:.2f} | **Gk:** {Gk1:.2f}")
            st.write(f"**Cp:** {Cp1:.2f} | **Ck:** {Ck1_new:.2f}")

        with col3:
            st.markdown("### Мембрана 2")
            st.write(f"**Gp2:** {Gp2:.2f} | **Gk2:** {Gk2:.2f}")
            st.write(f"**Cp2:** {Cp2:.2f} | **Ck2:** {Ck2_new:.2f}")

        # --- ДРУГИЙ РЯДОК БЛОКІВ ---
        st.write("")  # Відступ
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown("### Змішувач 2")
            st.write(f"**Gi2:** {Gr_sum:.2f}")
            st.write(f"**Cv2:** {Ck_sum:.2f}")

        with col5:
            st.markdown("### Розділювач 1")
            st.write(f"**Gr:** {Gr1_new:.2f}")
            st.write(f"**Gkk:** {Gkk1:.2f}")

        with col6:
            st.markdown("### Розділювач 2")
            st.write(f"**Gr2:** {Gr2_new:.2f}")
            st.write(f"**Gkk2:** {Gkk2:.2f}")
