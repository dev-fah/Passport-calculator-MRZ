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

    # ===== CSS AMÉLIORÉ (UNIQUEMENT STYLE / ANIMATIONS) =====
    st.markdown("""
    <style>
    /* Page background */
    .stApp {
        background: linear-gradient(180deg, #071021 0%, #0b1220 50%, #071021 100%);
        color-scheme: dark;
    }

    /* Container cards */
    .card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(6px) saturate(120%);
        -webkit-backdrop-filter: blur(6px) saturate(120%);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
        color: #e6fff2;
        box-shadow: 0 10px 30px rgba(2,6,23,0.6);
        transition: transform 260ms cubic-bezier(.2,.9,.3,1), box-shadow 260ms;
        font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .card:hover { transform: translateY(-6px); box-shadow: 0 22px 60px rgba(2,6,23,0.75); }

    .card h3 {
        margin: 0 0 12px 0;
        color: #9fffa8;
        font-size: 18px;
        letter-spacing: 0.4px;
    }

    /* Detail rows */
    .detail-row {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:12px;
        padding:10px 0;
        border-bottom: 1px dashed rgba(255,255,255,0.03);
    }
    .label {
        color:#7be3ff;
        font-weight:700;
        font-size:14px;
    }
    .muted {
        color:#9fd8ff;
        font-size:13px;
    }

    /* Animated badge */
    .badge {
        display:inline-flex;
        align-items:center;
        justify-content:center;
        min-width:44px;
        height:34px;
        padding:6px 12px;
        background: linear-gradient(90deg,#ffffff,#f3f3f3);
        color:#04121a;
        border-radius:999px;
        font-weight:800;
        box-shadow: 0 8px 20px rgba(2,6,23,0.45);
        transform-origin:center;
        animation: pop 700ms cubic-bezier(.2,.9,.3,1);
    }
    @keyframes pop {
        0% { transform: scale(.6); opacity:0; }
        60% { transform: scale(1.08); opacity:1; }
        100% { transform: scale(1); }
    }

    /* MRZ block (glass + OCR feel) */
    .mrz {
        background: linear-gradient(90deg, rgba(2,8,20,0.9), rgba(6,12,30,0.9));
        border-radius: 14px;
        padding: 14px;
        font-family: 'OCR-B', monospace;
        color:#00ff9c;
        letter-spacing:3px;
        font-size:18px;
        border: 1px solid rgba(0,255,156,0.06);
        box-shadow: inset 0 -6px 18px rgba(0,0,0,0.35);
    }

    .mrz .line {
        display:block;
        white-space:nowrap;
        overflow:auto;
    }

    /* Copy button */
    .copy-btn {
        background: linear-gradient(90deg,#00ffd1,#7be3ff);
        color:#00121a;
        border:none;
        padding:8px 14px;
        border-radius:12px;
        cursor:pointer;
        font-weight:800;
        box-shadow: 0 10px 30px rgba(0,255,209,0.08);
        transition: transform 160ms ease, box-shadow 160ms ease;
    }
    .copy-btn:hover { transform: translateY(-2px); box-shadow: 0 18px 40px rgba(0,255,209,0.12); }
    .copy-btn:active { transform: translateY(0); }

    /* Final MRZ pre */
    pre.mrz-pre {
        background: rgba(0,0,0,0.28);
        padding:12px;
        border-radius:10px;
        color:#bfffdc;
        font-family:'OCR-B', monospace;
        overflow:auto;
        border: 1px solid rgba(255,255,255,0.02);
    }

    /* Global check highlight with subtle animation */
    .global {
        text-align:center;
        margin-top:12px;
        font-size:20px;
        font-weight:800;
        color:#00ffd1;
        position:relative;
    }
    .global::after {
        content: "";
        position:absolute;
        left:50%;
        transform:translateX(-50%);
        bottom:-10px;
        width:80px;
        height:4px;
        background: linear-gradient(90deg,#00ffd1,#7be3ff);
        border-radius:4px;
        animation: slide 1.6s infinite linear;
        opacity:0.9;
    }
    @keyframes slide {
        0% { transform: translateX(-50%) translateX(-30px); opacity:0.6; }
        50% { transform: translateX(-50%) translateX(30px); opacity:1; }
        100% { transform: translateX(-50%) translateX(-30px); opacity:0.6; }
    }

    /* Responsive */
    @media (max-width: 720px) {
        .card { width: 94% !important; margin-left:auto; margin-right:auto; }
        .mrz { font-size:16px; letter-spacing:2px; }
    }
    </style>

    <!-- Small JS helper for copy feedback -->
    <script>
    function copyToClipboard(text, btn) {
        if (!navigator.clipboard) {
            alert('Copie non supportée par ce navigateur.');
            return;
        }
        navigator.clipboard.writeText(text).then(function() {
            const old = btn.innerText;
            btn.innerText = 'Copié ✓';
            btn.disabled = true;
            setTimeout(function(){ btn.innerText = old; btn.disabled = false; }, 1400);
        }, function() {
            alert('Impossible de copier automatiquement. Sélectionnez et copiez manuellement.');
        });
    }
    </script>
    """, unsafe_allow_html=True)

    # ===== UI (même logique, uniquement style modifié) =====
    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    safe_part_passport = html.escape(part_passport)
    safe_part_dates = html.escape(birth + str(birth_check) + sex + expiry + str(expiry_check))
    safe_part_optional = html.escape(part_optional)
    final_mrz_safe = html.escape(final_mrz)

    st.markdown(f"""
    <div class="card" style="max-width:640px;">
        <h3>Résultats détaillés</h3>
        <div class="detail-row"><div><div class="label">Passport</div><div class="muted">{safe_passport}</div></div><div class="badge">{passport_check}</div></div>
        <div class="detail-row"><div><div class="label">Birth</div><div class="muted">{safe_birth}</div></div><div class="badge">{birth_check}</div></div>
        <div class="detail-row"><div><div class="label">Expiry</div><div class="muted">{safe_expiry}</div></div><div class="badge">{expiry_check}</div></div>
        <div class="detail-row"><div><div class="label">Optional</div><div class="muted">{safe_optional}</div></div><div class="badge">{optional_check}</div></div>
        <div class="global">Checksum global : {global_check}</div>
    </div>

    <div class="card" style="max-width:640px;">
        <h3>Aperçu MRZ</h3>
        <div class="mrz">
            <span class="line">{html.escape(part_passport)}  |  {html.escape(nationality)}  |  {html.escape(birth + str(birth_check) + sex + expiry + str(expiry_check))}</span>
            <span class="line" style="opacity:0.85; font-size:13px; margin-top:6px;">{html.escape(part_optional)}</span>
        </div>

        <div style="display:flex; gap:10px; align-items:center; margin-top:12px;">
            <button class="copy-btn" onclick="copyToClipboard(`{final_mrz_safe}`, this)">Copier MRZ</button>
            <div style="font-family:monospace; color:#bfffdc; padding:8px 12px; border-radius:10px; background:rgba(0,0,0,0.22);">Global: <strong style="margin-left:8px;">{global_check}</strong></div>
        </div>

        <div style="margin-top:12px; font-size:13px; color:#9fd8ff;">Ligne MRZ complète</div>
        <pre class="mrz-pre">{final_mrz_safe}</pre>
    </div>
    """, unsafe_allow_html=True)
