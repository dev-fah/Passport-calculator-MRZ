import streamlit as st
import html
import re

st.set_page_config(page_title="Calculateur MRZ Passport", layout="centered")
st.title("Calculateur MRZ Passport")

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

    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    final_mrz_safe = html.escape(final_mrz)

    # CSS + JS
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg, #f5f8fb 0%, #eef4fb 50%, #f7fbff 100%);}
    .card {background: linear-gradient(180deg, #ffffff, #fbfdff); border-radius:14px; padding:18px; margin-bottom:18px; box-shadow:0 8px 30px rgba(15,30,50,0.06);}
    .card h3 {font-weight:900; color:#0b3b5a;}
    .detail-row {display:flex; justify-content:space-between; padding:10px 0;}
    .badge {background:#e6f3ff; padding:6px 12px; border-radius:999px; font-weight:bold;}
    .mrz {background:#eef6ff; padding:12px; border-radius:10px; font-family:monospace; letter-spacing:3px;}
    .btn-primary {background:#0b6ea3; color:white; padding:8px 12px; border:none; border-radius:8px; cursor:pointer;}
    </style>
    <script>
    function copyMRZ(text, btn){
        navigator.clipboard.writeText(text).then(function(){
            const old = btn.innerText;
            btn.innerText = 'Copié ✓';
            setTimeout(()=>btn.innerText=old,1200);
        });
    }
    </script>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
      <h3>Résultats détaillés</h3>
      <div class="detail-row"><div>Passport<br><small>{safe_passport}</small></div><div class="badge">{passport_check}</div></div>
      <div class="detail-row"><div>Birth<br><small>{safe_birth}</small></div><div class="badge">{birth_check}</div></div>
      <div class="detail-row"><div>Expiry<br><small>{safe_expiry}</small></div><div class="badge">{expiry_check}</div></div>
      <div class="detail-row"><div>Optional<br><small>{safe_optional}</small></div><div class="badge">{optional_check}</div></div>
      <div style="text-align:center; margin-top:10px; font-weight:bold;">Checksum global : {global_check}</div>
    </div>

    <div class="card">
      <h3>Aperçu MRZ</h3>
      <div class="mrz">
        {html.escape(part_passport)} | {nationality} | {html.escape(part_dates)}<br>
        {html.escape(part_optional)}
      </div>
      <br>
      <button class="btn-primary" onclick="copyMRZ('{final_mrz_safe}', this)">Copier MRZ</button>
      <pre>{final_mrz_safe}</pre>
    </div>
    """, unsafe_allow_html=True)
