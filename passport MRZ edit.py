import streamlit as st
import html
import re

# ===== CONFIG =====
st.set_page_config(page_title="Calculateur MRZ Passport", layout="centered")
st.title("Calculateur MRZ Passport")

# ===== FONCTIONS (TA VERSION = CORRECTE) =====
def char_to_value(c):
    if c.isdigit():
        return int(c)
    elif c.isalpha():
        return ord(c.upper()) - ord('A') + 10
    elif c == '<':
        return 0
    return 0

def calc_checksum(s):
    poids = [7,3,1]
    return sum(char_to_value(c)*poids[i%3] for i,c in enumerate(s)) % 10

def normalize_and_pad(passport, birth, expiry, optional):
    passport = passport.strip().upper().ljust(9, '<')[:9]
    optional = optional.strip().upper().ljust(14, '<')[:14]
    return passport, birth.strip(), expiry.strip(), optional

def simple_validate(passport, birth, expiry, optional):
    errors = []
    if not re.fullmatch(r'[A-Z0-9<]{1,9}', passport):
        errors.append("Passport invalide")
    if not re.fullmatch(r'\d{6}', birth):
        errors.append("Birth invalide (YYMMDD)")
    if not re.fullmatch(r'\d{6}', expiry):
        errors.append("Expiry invalide (YYMMDD)")
    return errors

# ===== INPUTS =====
with st.form("mrz_form"):
    col1, col2 = st.columns(2)

    with col1:
        passport_in = st.text_input("Passport", "A20256311")
        birth_in = st.text_input("Birth (YYMMDD)", "950712")
        expiry_in = st.text_input("Expiry (YYMMDD)", "301125")

    with col2:
        optional_in = st.text_input("Optional", "<<<<<<<<<<<<<<")
    
    submit = st.form_submit_button("Calculer")

# ===== CALCUL =====
if submit:
    passport, birth, expiry, optional = normalize_and_pad(
        passport_in, birth_in, expiry_in, optional_in
    )

    errors = simple_validate(passport, birth, expiry, optional)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Checks individuels (TA LOGIQUE)
    passport_check = calc_checksum(passport)
    birth_check = calc_checksum(birth)
    expiry_check = calc_checksum(expiry)
    optional_check = calc_checksum(optional)

    # GLOBAL (TA LOGIQUE EXACTE)
    global_string = (
        passport + str(passport_check) +
        birth + str(birth_check) +
        expiry + str(expiry_check) +
        optional + str(optional_check)
    )
    global_check = calc_checksum(global_string)

    # MRZ affichage
    nationality = "USA"
    sex = "M"

    part_passport = passport + str(passport_check)
    part_dates = birth + str(birth_check) + sex + expiry + str(expiry_check)
    part_optional = optional + str(optional_check)

    final_mrz = global_string + str(global_check)

    # ===== CSS COPILOT (AMÉLIORÉ) =====
    st.markdown("""
    <style>
    .card {
        background: linear-gradient(135deg, #0a0c14, #12161e);
        border-radius: 30px;
        padding: 20px;
        margin-bottom: 20px;
        color: #dfffe6;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .card h3 {
        color: #9fffa8;
    }

    .detail-row {
        display:flex;
        justify-content:space-between;
        padding:8px 0;
        border-bottom:5px dashed #333;
    }

    .label {
        color:#7be3ff;
        font-weight:bold;
    }

    .badge {
        background:white;
        color:black;
        padding:5px 10px;
        border-radius:999px;
        font-weight:bold;
    }

    .mrz {
        background:black;
        padding:12px;
        border-radius:30px;
        font-family: monospace;
        color:#00ff9c;
        letter-spacing:3px;
    }

    .global {
        text-align:center;
        margin-top:10px;
        font-size:20px;
        font-weight:bold;
        color:#00ffd1;
    }

    .copy-btn {
        background:#00ffd1;
        border:none;
        padding:8px 12px;
        border-radius:30px;
        cursor:pointer;
        font-weight:bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== UI =====
    st.markdown(f"""
    <div class="card">
        <h3>Résultats détaillés</h3>
        <div class="detail-row"><span class="label">Passport</span><span class="badge">{passport_check}</span></div>
        <div class="detail-row"><span class="label">Birth</span><span class="badge">{birth_check}</span></div>
        <div class="detail-row"><span class="label">Expiry</span><span class="badge">{expiry_check}</span></div>
        <div class="detail-row"><span class="label">Optional</span><span class="badge">{optional_check}</span></div>
        <div class="global">Checksum global : {global_check}</div>
    </div>

    <div class="card">
        <h3>MRZ</h3>
        <div class="mrz">
            {part_passport} | {nationality} | {part_dates}<br>
            {part_optional}
        </div>
        <div class="global">Global: {global_check}</div>

        <pre>{final_mrz}</pre>
    </div>
    """, unsafe_allow_html=True)
