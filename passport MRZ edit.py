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
        st.markdown("<div style='font-size:12px;color:#2b6ea3;margin-top:6px;opacity:0.7;'>Astuce: utilisez &lt; pour remplir</div>", unsafe_allow_html=True)
    
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

    global_string = (
        passport + str(passport_check) +
        birth + str(birth_check) +
        expiry + str(expiry_check) +
        optional + str(optional_check)
    )
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

    # ===== STYLE & JS =====
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #f5f8fb 0%, #eef4fb 50%, #f7fbff 100%); color-scheme: light; font-family: Inter, system-ui; }
    .card { background: linear-gradient(180deg, #ffffff, #fbfdff); border-radius:14px; padding:18px; margin-bottom:18px; color:#0b1b2b; box-shadow:0 8px 30px rgba(15,30,50,0.06); border:1px solid rgba(13,37,63,0.06); transition: transform .22s, box-shadow .22s; }
    .card:hover { transform: translateY(-6px); box-shadow:0 18px 50px rgba(15,30,50,0.12); }
    .card h3 { margin:0 0 12px 0; color:#0b3b5a; font-size:18px; font-weight:900; letter-spacing:0.4px; }
    .label { color:#0b6ea3; font-weight:900; font-size:14px; }
    .muted { color:#4b6b88; font-size:13px; opacity:0.6; }
    .small-note { font-size:13px; color:#4b6b88; opacity:0.6; margin-top:8px; }
    .detail-row { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:10px 0; border-bottom:1px dashed rgba(11,27,43,0.04); }
    .badge { display:inline-flex; align-items:center; justify-content:center; min-width:48px; height:36px; padding:6px 14px; background: linear-gradient(90deg,#f0f6ff,#e6f3ff); color:#042033; border-radius:999px; font-weight:900; box-shadow:0 6px 18px rgba(2,24,40,0.06); animation: pop 600ms cubic-bezier(.2,.9,.3,1); }
    @keyframes pop {0%{transform:translateY(6px) scale(.96); opacity:0;}60%{transform:translateY(-2px) scale(1.02); opacity:1;}100%{transform:translateY(0) scale(1);}}
    .mrz { background: linear-gradient(180deg, #f7fbff, #eef6ff); border-radius:10px; padding:12px; font-family:'OCR-B', monospace; color:#0b3b5a; letter-spacing:3px; font-size:16px; border:1px solid rgba(11,110,163,0.06); box-shadow: inset 0 -4px 12px rgba(0,0,0,0.02); transition: transform 180ms ease; }
    .mrz:hover { transform: translateY(-3px); }
    .mrz .line { display:block; white-space:nowrap; overflow:auto; }
    .btn { display:inline-flex; align-items:center; gap:8px; padding:8px 14px; border-radius:10px; cursor:pointer; border:none; font-weight:800; }
    .btn-primary { background: linear-gradient(90deg,#0b9bd6,#0b6ea3); color:#fff; box-shadow:0 8px 24px rgba(11,110,163,0.12); padding:8px 14px; border-radius:10px; }
    .btn-primary:hover { transform: translateY(-2px); }
    pre.mrz-pre { background:#f3f7fb; padding:12px; border-radius:8px; color:#0b3b5a; font-family:'OCR-B', monospace; overflow:auto; border:1px solid rgba(11,110,163,0.04); margin-top:10px; display:block; }
    .global { text-align:center; margin-top:12px; font-size:18px; font-weight:900; color:#0b6ea3; position:relative; }
    </style>
    <script>
    function copyMRZ(text, btn){
        if(!navigator.clipboard){alert('Copie non supportée'); return;}
        navigator.clipboard.writeText(text).then(function(){
            const old=btn.innerText; btn.innerText='Copié ✓'; btn.disabled=true;
            setTimeout(()=>{btn.innerText=old; btn.disabled=false;},1200);
        },function(){alert('Impossible de copier automatiquement');});
    }
    </script>
    """, unsafe_allow_html=True)

    # ===== AFFICHAGE =====
    st.markdown(f"""
    <div class="card" style="max-width:760px;">
        <h3>Résultats détaillés</h3>
        <div class="detail-row"><div><div class="label">Passport</div><div class="muted">{safe_passport}</div></div><div class="badge">{passport_check}</div></div>
        <div class="detail-row"><div><div class="label">Birth</div><div class="muted">{safe_birth}</div></div><div class="badge">{birth_check}</div></div>
        <div class="detail-row"><div><div class="label">Expiry</div><div class="muted">{safe_expiry}</div></div><div class="badge">{expiry_check}</div></div>
        <div class="detail-row"><div><div class="label">Optional</div><div class="mut
