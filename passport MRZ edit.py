# app_final.py
# -*- coding: utf-8 -*-
import streamlit as st
import html
import re

# ===== CONFIG =====
st.set_page_config(page_title="Calculateur MRZ Passport", layout="centered")
st.title("Calculateur MRZ Passport")

# ===== FONCTIONS =====
def char_to_value(c):
    if c.isdigit():
        return int(c)
    elif c.isalpha():
        return ord(c.upper()) - ord('A') + 10
    elif c == '<':
        return 0
    return 0

def calc_checksum(s):
    poids = [7, 3, 1]
    return sum(char_to_value(c) * poids[i % 3] for i, c in enumerate(s)) % 10

def normalize_and_pad(passport, birth, expiry, optional):
    passport = passport.strip().upper().ljust(9, '<')[:9]
    optional = optional.strip().upper().ljust(14, '<')[:14]
    return passport, birth.strip(), expiry.strip(), optional

def simple_validate(passport, birth, expiry, optional):
    errors = []
    if not re.fullmatch(r'[A-Z][0-9]{8}', passport):
        errors.append("Passport invalide : 1 lettre + 8 chiffres requis")
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
        st.markdown(
            "<div style='font-size:12px;color:#2b6ea3;margin-top:6px;opacity:0.75;'>Astuce: utilisez &lt; pour remplir</div>",
            unsafe_allow_html=True,
        )
    submit = st.form_submit_button("Calculer")

# ===== CALCUL =====
if submit:
    passport, birth, expiry, optional = normalize_and_pad(passport_in, birth_in, expiry_in, optional_in)
    errors = simple_validate(passport, birth, expiry, optional)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    passport_check = calc_checksum(passport)
    birth_check = calc_checksum(birth)
    expiry_check = calc_checksum(expiry)
    optional_check = calc_checksum(optional)

    global_string = passport + str(passport_check) + birth + str(birth_check) + expiry + str(expiry_check) + optional + str(optional_check)
    global_check = calc_checksum(global_string)

    nationality = "USA"
    sex = "M"

    part_passport = passport + str(passport_check)
    part_dates = birth + str(birth_check) + sex + expiry + str(expiry_check)
    part_optional = optional + str(optional_check)
    final_mrz = global_string + str(global_check)

    # ===== SÉCURISATION =====
    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    safe_part_passport = html.escape(part_passport)
    safe_part_dates = html.escape(part_dates)
    safe_part_optional = html.escape(part_optional)
    final_mrz_safe = html.escape(final_mrz)

    # ===== CSS =====
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #eef6fb 0%, #f7fbff 60%); font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial; }
    .card { background:#fff; border-radius:18px; padding:20px; margin-bottom:18px; box-shadow:0 8px 24px rgba(12,30,60,0.06); }
    .card h3 { font-weight:900; color:#073b57; }
    .detail-row { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px dashed rgba(11,27,43,0.04); }
    .label { font-weight:900; color:#0b6ea3; font-size:14px; }
    .muted { color:#4b6b88; opacity:0.65; font-size:13px; }
    .badge { display:inline-flex; align-items:center; justify-content:center; min-width:50px; height:36px; background:linear-gradient(90deg,#eef7ff,#ffffff); border-radius:999px; font-weight:900; color:#042033; }
    .mrz { background: linear-gradient(180deg,#f7fbff,#eef6ff); border-radius:12px; padding:14px; font-family:'OCR-B', monospace; letter-spacing:3px; font-size:16px; color:#0b3b5a; }
    .mrz-pre { background:#f3f9ff; padding:14px; border-radius:12px; font-family:'OCR-B', monospace; color:#0b3b5a; overflow:auto; border:1px solid rgba(11,110,163,0.04); margin-top:12px; }
    .global { text-align:center; font-weight:900; color:#0b6ea3; margin-top:12px; font-size:18px; }
    </style>
    """, unsafe_allow_html=True)

    # ===== AFFICHAGE =====
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Résultats détaillés</h3>', unsafe_allow_html=True)
    st.markdown(f'''
    <div class="detail-row">
      <div>
        <div class="label">Passport</div>
        <div class="muted">{safe_passport}</div>
      </div>
      <div class="badge">{passport_check}</div>
    </div>
    <div class="detail-row">
      <div>
        <div class="label">Birth</div>
        <div class="muted">{safe_birth}</div>
      </div>
      <div class="badge">{birth_check}</div>
    </div>
    <div class="detail-row">
      <div>
        <div class="label">Expiry</div>
        <div class="muted">{safe_expiry}</div>
      </div>
      <div class="badge">{expiry_check}</div>
    </div>
    <div class="detail-row">
      <div>
        <div class="label">Optional</div>
        <div class="muted">{safe_optional}</div>
      </div>
      <div class="badge">{optional_check}</div>
    </div>
    <div class="global">Checksum global : {global_check}</div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # MRZ card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3>Aperçu MRZ</h3>', unsafe_allow_html=True)
    reveal = st.checkbox("Afficher la MRZ", value=True)
    if reveal:
        st.markdown(f'''
        <div class="mrz">
          <div>{safe_part_passport}  |  {html.escape(nationality)}  |  {safe_part_dates}</div>
          <div style="opacity:0.85; font-size:13px; margin-top:8px;">{safe_part_optional}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="mrz" style="filter:blur(2px); opacity:0.85;">
          <div>•••••••••  |  •••  |  •••••• • ••••••</div>
          <div style="opacity:0.6; font-size:13px; margin-top:8px;">••••••••••••••••</div>
        </div>
        ''', unsafe_allow_html=True)

    # Download and copy fallback
    mrz_bytes = final_mrz.encode("utf-8")
    st.download_button("Télécharger MRZ (.txt)", data=mrz_bytes, file_name="mrz.txt", mime="text/plain")
    st.text_area("MRZ (sélectionner et copier)", value=final_mrz, height=90)
    st.markdown(f'<pre class="mrz-pre">{final_mrz_safe}</pre>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
