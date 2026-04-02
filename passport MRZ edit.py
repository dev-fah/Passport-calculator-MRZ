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
        optional_in = st.text_input("Optional", "<<<<<<<<<<<<<<<<")
        st.markdown("<div style='font-size:12px;text-align:center; color:#000000;margin-top:6px;'>Astuce: utilisez &lt; pour remplir</div>", unsafe_allow_html=True)
    
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

    # Checks individuels (LOGIQUE INTACTE)
    passport_check = calc_checksum(passport)
    birth_check = calc_checksum(birth)
    expiry_check = calc_checksum(expiry)
    optional_check = calc_checksum(optional)

    # GLOBAL (LOGIQUE INTACTE)
    global_string = (
        passport + str(passport_check) +
        birth + str(birth_check) +
        expiry + str(expiry_check) +
        optional + str(optional_check)
    )
    global_check = calc_checksum(global_string)

    # MRZ affichage (LOGIQUE INTACTE)
    nationality = "USA"
    sex = "M"

    part_passport = passport + str(passport_check)
    part_dates = birth + str(birth_check) + sex + expiry + str(expiry_check)
    part_optional = optional + str(optional_check)

    final_mrz = global_string + str(global_check)

    # ===== STYLE / HTML / JS (UNIQUEMENT L'APPARENCE) =====
    # Thème plus clair et contrasté, cartes claires sur fond doux, animations subtiles.
    st.markdown("""
    <style>
    /* Page background: doux, pas tout noir */
    .stApp {
      background: linear-gradient(180deg, #A0C7F2 0%, #FFFFFF 30%, #A0C7F2 100%); /*===========Fond=============*/
      color-scheme: light;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial;
    }

    /* Container cards: clair, bord arrondi, ombre douce */
    .card {
      background: linear-gradient(180deg, #DCE4F7, #DCE4F7); /*=========Manamboatra========*/
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 18px;
      color: #0b1b2b;
      box-shadow: 0 8px 30px rgba(15, 30, 50, 0.08);
      border: 1px solid rgba(13, 37, 63, 0.06);
      transition: transform .22s cubic-bezier(.2,.9,.3,1), box-shadow .22s;
    }
    .card:hover { transform: translateY(-6px); box-shadow: 0 18px 50px rgba(15, 30, 50, 0.12); }

    .card h3 { margin:0 0 12px 0; color:#0b3b5a; font-size:18px; }

    /* Detail rows */
    .detail-row {
      display:flex; justify-content:space-between; align-items:center;
      gap:12px; padding:10px 0; border-bottom:1px dashed rgba(11,27,43,0.04);
    }
    .label { color:#0b6ea3; font-weight:700; font-size:14px; }
    .muted { color:#4b6b88; font-size:13px; }

    /* Badge: clair, lisible */
    .badge {
      display:inline-flex; align-items:center; justify-content:center;
      min-width:48px; height:36px; padding:6px 14px;
      background: linear-gradient(90deg,#f0f6ff,#e6f3ff);
      color:#042033; border-radius:999px; font-weight:800;
      box-shadow: 0 6px 18px rgba(2,24,40,0.06);
      animation: pop 600ms cubic-bezier(.2,.9,.3,1);
    }
    @keyframes pop {
      0% { transform: translateY(6px) scale(.96); opacity:0; }
      60% { transform: translateY(-2px) scale(1.02); opacity:1; }
      100% { transform: translateY(0) scale(1); }
    }

    /* MRZ block: clair avec police OCR feel, texte sombre sur fond doux */
    .mrz {
      background: linear-gradient(180deg, #f7fbff, #eef6ff);
      border-radius: 10px;
      padding: 12px;
      font-family: 'OCR-B', monospace;
      color:#0b3b5a;
      letter-spacing:3px;
      font-size:16px;
      border: 1px solid rgba(11,110,163,0.06);
      box-shadow: inset 0 -4px 12px rgba(0,0,0,0.02);
      transition: transform 180ms ease;
    }
    .mrz:hover { transform: translateY(-3px); }
    .mrz .line { display:block; white-space:nowrap; overflow:auto; }

    /* Mask overlay to hide MRZ by default (subtil, clair) */
    .mrz-mask {
      position:relative;
      border-radius:8px;
      overflow:hidden;
    }
    .mrz-mask .overlay {
      position:absolute; inset:0;
      display:flex; align-items:center; justify-content:center;
      background: linear-gradient(90deg, rgba(255,255,255,0.85), rgba(255,255,255,0.82));
      color: rgba(11,27,43,0.12);
      font-family:'OCR-B', monospace;
      letter-spacing:6px;
      font-size:16px;
    }

    /* Revealed state */
    .revealed { color:#0b3b5a !important; }
    .revealed .overlay { display:none; }

    /* Buttons: style moderne, accessible */
    .btn {
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 14px; border-radius:10px; cursor:pointer; border:none;
      font-weight:700;
    }
    .btn-ghost {
      background: transparent; color:#0b3b5a; border:1px solid rgba(11,110,163,0.08);
    }
    .btn-primary {
      background: linear-gradient(90deg,#0b9bd6,#0b6ea3); color:#fff;
      box-shadow: 0 8px 24px rgba(11,110,163,0.12);
    }
    .btn-primary:hover { transform: translateY(-2px); }

    /* MRZ pre (hidden by default) */
    pre.mrz-pre {
      background: #f3f7fb;
      padding:12px; border-radius:8px; color:#0b3b5a;
      font-family:'OCR-B', monospace; overflow:auto; border:1px solid rgba(11,110,163,0.04);
      margin-top:10px; display:none;
    }

    /* Global highlight */
    .global {
      text-align:center; margin-top:12px; font-size:18px; font-weight:800; color:#0b6ea3; position:relative;
    }

    /* Responsive */
    @media (max-width:720px) {
      .card { width:94% !important; margin-left:auto; margin-right:auto; }
      .mrz { font-size:15px; letter-spacing:2px; }
      .badge { min-width:40px; height:32px; padding:6px 10px; }
    }
    </style>

    <script>
    /* Helpers: reveal + copy (fonctionne côté client) */
    function toggleReveal(btnId, blockId, preId) {
      const btn = document.getElementById(btnId);
      const block = document.getElementById(blockId);
      const pre = document.getElementById(preId);
      if (!block.classList.contains('revealed')) {
        block.classList.add('revealed');
        btn.innerText = 'Cacher MRZ';
        pre.style.display = 'block';
      } else {
        block.classList.remove('revealed');
        btn.innerText = 'Afficher MRZ';
        pre.style.display = 'none';
      }
    }

    function copyMRZ(text, btn) {
      if (!navigator.clipboard) {
        alert('Copie non supportée par ce navigateur.');
        return;
      }
      navigator.clipboard.writeText(text).then(function() {
        const old = btn.innerText;
        btn.innerText = 'Copié ✓';
        btn.disabled = true;
        setTimeout(function(){ btn.innerText = old; btn.disabled = false; }, 1200);
      }, function() {
        alert('Impossible de copier automatiquement. Sélectionnez et copiez manuellement.');
      });
    }
    </script>
    """, unsafe_allow_html=True)

    # ===== AFFICHAGE (LOGIQUE INTACTE) =====
    safe_passport = html.escape(passport)
    safe_birth = html.escape(birth)
    safe_expiry = html.escape(expiry)
    safe_optional = html.escape(optional)
    final_mrz_safe = html.escape(final_mrz)

    st.markdown(f"""
    <div class="card" style="max-width:760px;">
      <h3>Résultats détaillés</h3>

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
      <div style="font-size:13px;color:#4b6b88;margin-top:8px;">La MRZ est masquée par défaut pour protéger les données. Cliquez sur "Afficher MRZ" pour la révéler.</div>
    </div>

    <div class="card" style="max-width:760px;">
      <h3>Aperçu MRZ</h3>

      <div id="mrzBlock" class="mrz mrz-mask" style="margin-bottom:10px;">
        <div class="line">{html.escape(part_passport)}  |  {html.escape(nationality)}  |  {html.escape(birth + str(birth_check) + sex + expiry + str(expiry_check))}</div>
        <div class="line" style="opacity:0.85; font-size:13px; margin-top:6px;">{html.escape(part_optional)}</div>
        <div class="overlay" style="pointer-events:none;">••••••••••••••••••••••••••••••</div>
      </div>

      <div style="display:flex; gap:10px; align-items:center; margin-top:6px;">
        <button id="revealBtn" class="btn btn-ghost" onclick="toggleReveal('revealBtn','mrzBlock','mrzPre')">Afficher MRZ</button>
        <button class="btn btn-primary" onclick="copyMRZ(`{final_mrz_safe}`, this)">Copier MRZ</button>
        <div style="font-family:monospace; color:#0b3b5a; padding:8px 12px; border-radius:8px; background:#f3f7fb;">Global: <strong style="margin-left:8px;">{global_check}</strong></div>
      </div>

      <div style="margin-top:12px; font-size:13px; color:#4b6b88;">Ligne MRZ complète (masquée par défaut)</div>
      <pre id="mrzPre" class="mrz-pre">{final_mrz_safe}</pre>
    </div>
    """, unsafe_allow_html=True)
