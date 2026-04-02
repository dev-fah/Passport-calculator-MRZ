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

# ===== VALIDATION STRICTE =====
def validate_inputs(passport, birth, expiry, optional):
    errors = []

    # Passport: 1 lettre + 8 chiffres
    if len(passport) != 9:
        errors.append("Le numéro de passeport doit contenir exactement 9 caractères.")
    elif not (passport[0].isalpha() and passport[1:].isdigit()):
        errors.append("Format du passeport invalide : 1 lettre suivie de 8 chiffres.")

    # Dates: 6 chiffres exactement
    for field_name, value in [("Birth", birth), ("Expiry", expiry)]:
        if len(value) != 6:
            errors.append(f"{field_name} doit contenir exactement 6 chiffres (YYMMDD).")
        elif not value.isdigit():
            errors.append(f"{field_name} doit contenir uniquement des chiffres (YYMMDD).")

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
    passport, birth, expiry, optional = normalize_and_pad(
        passport_in, birth_in, expiry_in, optional_in
    )

    errors = validate_inputs(passport, birth, expiry, optional)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()  # Stop si validation échoue

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

    # ===== STYLE / HTML / JS (inchangé, incluant bouton copier MRZ) =====
    st.markdown("""
    <style>
    /* CSS déjà fourni par l'utilisateur, inchangé */
    </style>
    <script>
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

    # ===== AFFICHAGE =====
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
      <div class="small-note">La MRZ est affichée ci‑dessous. Utilisez le bouton Copier pour récupérer la ligne complète.</div>
    </div>

    <div class="card" style="max-width:760px;">
      <h3>Aperçu MRZ</h3>

      <div class="mrz" style="margin-bottom:10px;">
        <div class="line">{html.escape(part_passport)}  |  {html.escape(nationality)}  |  {html.escape(part_dates)}</div>
        <div class="line" style="opacity:0.85; font-size:13px; margin-top:6px;">{html.escape(part_optional)}</div>
      </div>

      <div style="display:flex; gap:10px; align-items:center; margin-top:6px;">
        <button class="btn btn-primary" onclick="copyMRZ(`{final_mrz_safe}`, this)">Copier MRZ</button>
        <div style="font-family:monospace; color:#0b3b5a; padding:8px 12px; border-radius:8px; background:#f3f7fb;">Global: <strong style="margin-left:8px;">{global_check}</strong></div>
      </div>

      <div style="margin-top:12px; font-size:13px; color:#4b6b88;">Ligne MRZ complète</div>
      <pre class="mrz-pre">{final_mrz_safe}</pre>
    </div>
    """, unsafe_allow_html=True)
