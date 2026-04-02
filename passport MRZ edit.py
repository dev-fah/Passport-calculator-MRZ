# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import html
import re
import json
import streamlit.components.v1 as components

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
    # 1) Normalisation (logique inchangée)
    passport, birth, expiry, optional = normalize_and_pad(passport_in, birth_in, expiry_in, optional_in)

    # 2) Validation (logique inchangée)
    errors = simple_validate(passport, birth, expiry, optional)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # 3) Calculs (logique inchangée)
    passport_check = calc_checksum(passport)
    birth_check = calc_checksum(birth)
    expiry_check = calc_checksum(expiry)
    optional_check = calc_checksum(optional)

    # 4) Construction MRZ (logique inchangée)
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

    # ===== Sécurisation des valeurs affichées =====
    # Échapper uniquement les valeurs utilisateur (sécurité)
    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    safe_part_passport = html.escape(part_passport)
    safe_part_dates = html.escape(part_dates)
    safe_part_optional = html.escape(part_optional)
    final_mrz_safe = html.escape(final_mrz)

    # JSON string (texte brut) pour la copie côté client (bien formée)
    final_mrz_json = json.dumps(final_mrz)

    # ===== HTML/CSS/JS à rendre via components.html (force rendu HTML) =====
    # IMPORTANT : ne pas html.escape ce bloc. Seules les valeurs insérées ci‑dessous sont échappées.
    html_block = f"""
    <html>
    <head>
    <meta charset="utf-8" />
    <style>
    /* Page background */
    body {{ margin:0; padding:18px 0; background: linear-gradient(180deg, #eef6fb 0%, #f7fbff 60%); font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial; color:#0b1b2b; }}

    .wrap {{ display:flex; flex-direction:column; gap:18px; align-items:center; width:100%; }}

    .card {{
      width:100%; max-width:900px;
      background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,252,255,0.99));
      border-radius: 22px; padding: 24px;
      box-shadow: 0 8px 24px rgba(12,30,60,0.06), 0 28px 80px rgba(12,30,60,0.06);
      border: 1px solid rgba(11,110,163,0.06);
      transition: transform 420ms cubic-bezier(.2,.9,.3,1), box-shadow 420ms;
      position: relative; overflow: hidden;
    }}
    .card:hover {{ transform: translateY(-12px) scale(1.01); box-shadow: 0 28px 80px rgba(12,30,60,0.12), 0 60px 160px rgba(12,30,60,0.08); }}

    .card h3 {{ margin:0 0 14px 0; color:#073b57; font-size:20px; font-weight:900; letter-spacing:0.6px; }}

    .detail-row {{ display:flex; justify-content:space-between; align-items:center; gap:12px; padding:12px 0; border-bottom:1px dashed rgba(11,27,43,0.04); }}
    .detail-left {{ display:flex; flex-direction:column; gap:6px; }}
    .label {{ color:#0b6ea3; font-weight:900; font-size:14px; }}
    .muted {{ color:#4b6b88; font-size:13px; opacity:0.65; }}

    .badge {{ display:inline-flex; align-items:center; justify-content:center; min-width:56px; height:40px; padding:6px 16px; background: linear-gradient(90deg,#ffffff,#eef7ff); color:#042033; border-radius:999px; font-weight:900; box-shadow: 0 10px 30px rgba(11,110,163,0.06); animation: badgePop 900ms cubic-bezier(.2,.9,.3,1); }}
    @keyframes badgePop {{ 0% {{ transform: translateY(12px) scale(.86); opacity:0; }} 50% {{ transform: translateY(-6px) scale(1.08); opacity:1; }} 100% {{ transform: translateY(0) scale(1); }} }}

    .mrz {{ background: linear-gradient(180deg, #f7fbff, #eef6ff); border-radius:14px; padding:14px 16px; font-family:'OCR-B', monospace; color:#0b3b5a; letter-spacing:3px; font-size:16px; border:1px solid rgba(11,110,163,0.06); box-shadow: inset 0 -6px 18px rgba(0,0,0,0.02); transition: transform 300ms; }}
    .mrz:hover {{ transform: translateY(-6px) rotate(-0.2deg) scale(1.005); }}
    .mrz .line {{ display:block; white-space:nowrap; overflow:auto; }}

    .btn {{ display:inline-flex; align-items:center; gap:10px; padding:10px 16px; border-radius:12px; cursor:pointer; border:none; font-weight:900; color:#00121a; background: linear-gradient(90deg,#00ffd1,#7be3ff); box-shadow: 0 12px 36px rgba(0,255,209,0.08); transition: transform 180ms, box-shadow 180ms; }}
    .btn:hover {{ transform: translateY(-3px); filter: brightness(1.02); box-shadow: 0 22px 60px rgba(0,255,209,0.12); }}

    pre.mrz-pre {{ background: linear-gradient(180deg,#fbfeff,#f3f9ff); padding:14px; border-radius:12px; color:#0b3b5a; font-family:'OCR-B', monospace; overflow:auto; border:1px solid rgba(11,110,163,0.04); margin-top:12px; box-shadow: 0 8px 30px rgba(11,110,163,0.04); }}

    .global {{ text-align:center; margin-top:14px; font-size:18px; font-weight:900; color:#0b6ea3; position:relative; }}
    .global::after {{ content:""; position:absolute; left:50%; transform:translateX(-50%); bottom:-12px; width:120px; height:6px; background: linear-gradient(90deg,#0b9bd6,#7be3ff); border-radius:6px; box-shadow: 0 8px 30px rgba(11,110,163,0.12); animation: slideGlow 2.2s infinite linear; opacity:0.95; }}
    @keyframes slideGlow {{ 0% {{ transform: translateX(-50%) translateX(-40px); opacity:0.6; }} 50% {{ transform: translateX(-50%) translateX(40px); opacity:1; }} 100% {{ transform: translateX(-50%) translateX(-40px); opacity:0.6; }} }}

    @media (max-width:900px) {{ .card {{ padding:18px; border-radius:16px; }} .mrz {{ font-size:15px; letter-spacing:2.5px; }} .badge {{ min-width:48px; height:36px; }} }}
    @media (max-width:520px) {{ .detail-row {{ flex-direction:column; align-items:flex-start; gap:8px; }} .btn {{ width:100%; justify-content:center; }} }}
    </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <h3>Résultats détaillés</h3>

          <div class="detail-row">
            <div class="detail-left">
              <div class="label">Passport</div>
              <div class="muted">{safe_passport}</div>
            </div>
            <div class="badge">{passport_check}</div>
          </div>

          <div class="detail-row">
            <div class="detail-left">
              <div class="label">Birth</div>
              <div class="muted">{safe_birth}</div>
            </div>
            <div class="badge">{birth_check}</div>
          </div>

          <div class="detail-row">
            <div class="detail-left">
              <div class="label">Expiry</div>
              <div class="muted">{safe_expiry}</div>
            </div>
            <div class="badge">{expiry_check}</div>
          </div>

          <div class="detail-row">
            <div class="detail-left">
              <div class="label">Optional</div>
              <div class="muted">{safe_optional}</div>
            </div>
            <div class="badge">{optional_check}</div>
          </div>

          <div class="global">Checksum global : {global_check}</div>
          <div class="muted" style="margin-top:8px;">La MRZ est affichée ci‑dessous. Utilisez le bouton Copier pour récupérer la ligne complète.</div>
        </div>

        <div class="card">
          <h3>Aperçu MRZ</h3>

          <div class="mrz">
            <div class="line">{safe_part_passport}  |  {html.escape(nationality)}  |  {safe_part_dates}</div>
            <div class="line" style="opacity:0.85; font-size:13px; margin-top:8px;">{safe_part_optional}</div>
          </div>

          <div style="display:flex; gap:12px; align-items:center; margin-top:14px;">
            <button class="btn" onclick='(function(btn){{ try{{ navigator.clipboard.writeText({final_mrz_json}); const old = btn.innerText; btn.innerText = "Copié ✓"; btn.disabled = true; setTimeout(function(){{ btn.innerText = old; btn.disabled = false; }}, 1200); }}catch(e){{ alert("Erreur copie: "+e); }} }})(this)'>Copier MRZ</button>
            <div style="font-family:monospace; color:#0b3b5a; padding:10px 14px; border-radius:10px; background:#fbfeff;">Global: <strong style="margin-left:8px;">{global_check}</strong></div>
          </div>

          <div style="margin-top:12px; font-size:13px; color:#4b6b88;">Ligne MRZ complète</div>
          <pre class="mrz-pre">{final_mrz_safe}</pre>
        </div>
      </div>
    </body>
    </html>
    """

    # ===== RENDER HTML VIA components.html (force rendu) =====
    # height large enough to show content; allow scrolling if needed
    components.html(html_block, height=760, scrolling=True)
