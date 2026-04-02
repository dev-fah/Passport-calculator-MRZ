# -*- coding: utf-8 -*-
import streamlit as st
import html
import re

# ===== CONFIG =====
st.set_page_config(page_title="Calculateur MRZ Passport", layout="centered")
st.title("Calculateur MRZ Passport")

# ===== FONCTIONS (LOGIQUE INCHANGÉE) =====
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
    passport = passport.strip().upper()
    optional = optional.strip().upper().ljust(14, '<')[:14]
    return passport, birth.strip(), expiry.strip(), optional

def strict_validate(passport, birth, expiry, optional):
    errors = []
    # Passeport: 1 lettre + 8 chiffres
    if not re.fullmatch(r'[A-Z][0-9]{8}', passport):
        errors.append("Le numéro de passeport doit être 1 lettre suivie de 8 chiffres.")
    # Dates: 6 chiffres
    if not re.fullmatch(r'\d{6}', birth):
        errors.append("Date de naissance invalide : doit être au format YYMMDD (6 chiffres).")
    if not re.fullmatch(r'\d{6}', expiry):
        errors.append("Date d'expiration invalide : doit être au format YYMMDD (6 chiffres).")
    # Optional: jusqu'à 14 caractères A-Z ou <
    if not re.fullmatch(r'[A-Z<]{0,14}', optional):
        errors.append("Champ optionnel invalide : maximum 14 caractères A-Z ou <.")
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
        st.markdown("<div style='font-size:12px;color:#2b6ea3;margin-top:6px;opacity:0.7;'>Astuce: utilisez &lt; pour remplir</div>", unsafe_allow_html=True)
    
    submit = st.form_submit_button("Calculer")

# ===== CALCUL =====
if submit:
    passport, birth, expiry, optional = normalize_and_pad(passport_in, birth_in, expiry_in, optional_in)
    errors = strict_validate(passport, birth, expiry, optional)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Checks individuels
    passport_check = calc_checksum(passport)
    birth_check = calc_checksum(birth)
    expiry_check = calc_checksum(expiry)
    optional_check = calc_checksum(optional)

    # Checksum global
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

    # ===== STYLE / HTML / JS (UNIQUEMENT L'APPARENCE) =====
    st.markdown("""
    <style>
    .card { background: linear-gradient(135deg, rgba(10,12,20,0.95), rgba(18,22,30,0.95)); border-radius:14px; padding:18px; box-shadow:0 8px 30px rgba(2,6,23,0.6); color:#dfffe6; width:520px; font-family: Inter, ui-sans-serif, system-ui; transition: transform 300ms; border:1px solid rgba(255,255,255,0.03); }
    .card:hover { transform:translateY(-6px); box-shadow:0 18px 50px rgba(2,6,23,0.75); }
    .card h3 { margin:0 0 8px 0; color:#9fffa8; font-weight:700; letter-spacing:0.6px; }
    .mrz { background: linear-gradient(90deg, rgba(2,8,20,0.95), rgba(6,12,30,0.95)); border-radius:10px; padding:12px 14px; font-family:'OCR-B', monospace; color:#00ff9c; letter-spacing:3px; font-size:18px; display:flex; flex-direction:column; gap:8px; }
    .badge { display:inline-block; background:linear-gradient(90deg,#ffffff,#f0f0f0); color:#000; padding:6px 10px; border-radius:999px; font-weight:700; animation: pop 900ms ease; }
    @keyframes pop { 0% { transform:scale(.6); opacity:0; } 60% { transform:scale(1.08); opacity:1; } 100% { transform:scale(1); } }
    .detail-row { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:6px 0; border-bottom:1px dashed rgba(255,255,255,0.03); }
    .label { color:#7be3ff; font-weight:600; }
    .muted { color:#9fd8ff; font-size:13px; }
    .global-check { margin-top:10px; padding-top:10px; border-top:2px solid rgba(0,255,156,0.08); text-align:center; font-weight:800; color:#00ffd1; font-size:20px; position:relative; }
    .global-check::after { content:""; position:absolute; left:50%; transform:translateX(-50%); bottom:-8px; width:60px; height:4px; background:linear-gradient(90deg,#00ffd1,#7be3ff); border-radius:4px; animation: slide 1.6s infinite linear; opacity:0.9; }
    @keyframes slide { 0% { transform:translateX(-50%) translateX(-30px); opacity:0.6; } 50% { transform:translateX(-50%) translateX(30px); opacity:1; } 100% { transform:translateX(-50%) translateX(-30px); opacity:0.6; } }
    .copy-btn { background: linear-gradient(90deg,#00ffd1,#7be3ff); color:#002; border:none; padding:8px 12px; border-radius:10px; font-weight:700; cursor:pointer; box-shadow:0 8px 20px rgba(0,255,209,0.08); }
    .copy-btn:active { transform: translateY(1px); }
    </style>

    <script>
    function copyMRZ(text, btn) {
      if (!navigator.clipboard) {
        alert('Copie non supportée par ce navigateur.');
        return;
      }
      navigator.clipboard.writeText(text).then(function() {
        const old = btn.innerText;
        btn.innerText = 'MRZ copié ✓';
        btn.disabled = true;
        setTimeout(function(){ btn.innerText = old; btn.disabled = false; }, 1200);
      }, function() {
        alert('Impossible de copier automatiquement. Sélectionnez et copiez manuellement.');
      });
    }
    </script>
    """, unsafe_allow_html=True)

    # ===== AFFICHAGE =====
    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    final_mrz_safe = html.escape(final_mrz)

    st.markdown(f"""
    <div class="card">
      <h3>Résultats détaillés</h3>
      <div class="detail-row"><div><span class="label">Passport</span><div class="muted">{safe_passport}</div></div><div class="badge">{passport_check}</div></div>
      <div class="detail-row"><div><span class="label">Birth</span><div class="muted">{safe_birth}</div></div><div class="badge">{birth_check}</div></div>
      <div class="detail-row"><div><span class="label">Expiry</span><div class="muted">{safe_expiry}</div></div><div class="badge">{expiry_check}</div></div>
      <div class="detail-row"><div><span class="label">
