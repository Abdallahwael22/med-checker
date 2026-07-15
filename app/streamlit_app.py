import sys
import os
import io
import json
import time
import streamlit as st
from PIL import Image

# Ensure project root is on path so src.* imports resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Page config (must be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="MedChecker AI — Clinical Safety Platform",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (injected once) ──────────────────────────────────────────────────────
_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{font-family:'Inter',sans-serif!important;background:#080d1a!important;color:#e2e8f0!important}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stDecoration"]{display:none}
[data-testid="stMain"]{background:#080d1a!important}
[data-testid="stMainBlockContainer"]{padding:1.5rem 2rem!important;max-width:1400px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1528 0%,#0a1020 100%)!important;border-right:1px solid rgba(0,212,255,.12)!important}
[data-testid="stSidebar"]>div{padding:1rem 1.2rem}
[data-testid="stSidebar"] label{color:#94a3b8!important;font-size:.78rem!important;text-transform:uppercase;letter-spacing:.08em}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,.04)!important;border:1px solid rgba(0,212,255,.2)!important;border-radius:10px!important;color:#e2e8f0!important}
[data-testid="stFileUploader"]{background:rgba(255,255,255,.03)!important;border:2px dashed rgba(0,212,255,.25)!important;border-radius:16px!important;transition:border-color .3s}
[data-testid="stFileUploader"]:hover{border-color:rgba(0,212,255,.5)!important}
[data-testid="stButton"]>button{background:linear-gradient(135deg,#00d4ff 0%,#0080ff 100%)!important;color:#080d1a!important;font-weight:700!important;font-size:.95rem!important;border:none!important;border-radius:12px!important;padding:.65rem 2rem!important;transition:all .25s!important;box-shadow:0 4px 24px rgba(0,212,255,.25)!important}
[data-testid="stButton"]>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 32px rgba(0,212,255,.45)!important}
[data-testid="stExpander"]{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:12px!important}
[data-testid="stExpander"] summary{color:#94a3b8!important}
[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,#00d4ff,#0080ff)!important;border-radius:99px!important}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:#0a0f1e}::-webkit-scrollbar-thumb{background:rgba(0,212,255,.3);border-radius:3px}
hr{border-color:rgba(255,255,255,.06)!important;margin:1.5rem 0!important}
.glass-card{background:rgba(255,255,255,.04);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:1.5rem;transition:box-shadow .3s,transform .3s}
.glass-card:hover{box-shadow:0 8px 32px rgba(0,0,0,.4);transform:translateY(-2px)}
.metric-pill{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:99px;padding:.3rem .85rem;font-size:.82rem;color:#94a3b8;font-weight:500}
.verdict-badge{display:inline-flex;align-items:center;gap:10px;border-radius:14px;padding:1rem 1.75rem;font-size:1.4rem;font-weight:800;letter-spacing:.05em;border:2px solid}
.verdict-approve{background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.4);color:#22c55e;box-shadow:0 0 32px rgba(34,197,94,.15)}
.verdict-deny{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.4);color:#ef4444;box-shadow:0 0 32px rgba(239,68,68,.15)}
.verdict-hold{background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.4);color:#f59e0b;box-shadow:0 0 32px rgba(245,158,11,.15)}
.section-label{font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#00d4ff;margin-bottom:.75rem}
.step-item{display:flex;align-items:center;gap:10px;padding:.5rem .6rem;border-radius:10px;margin-bottom:4px;font-size:.85rem;transition:background .2s}
.step-done{background:rgba(34,197,94,.1);color:#22c55e}
.step-active{background:rgba(0,212,255,.1);color:#00d4ff}
.step-idle{background:rgba(255,255,255,.03);color:#64748b}
.match-item{display:flex;align-items:flex-start;gap:8px;padding:.6rem .75rem;background:rgba(239,68,68,.07);border-left:3px solid rgba(239,68,68,.5);border-radius:0 8px 8px 0;margin-bottom:6px;font-size:.84rem;color:#fca5a5}
.gauge-bar-wrap{width:100%;background:rgba(255,255,255,.06);border-radius:99px;height:10px;margin-top:6px;overflow:hidden}
.alert-human{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.35);border-radius:12px;padding:1rem 1.25rem;display:flex;gap:12px;align-items:flex-start;color:#fde68a;font-size:.9rem}
@keyframes gradient-shift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.hero-title{font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,#00d4ff,#0080ff,#7c3aed,#00d4ff);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gradient-shift 4s ease infinite;line-height:1.1;margin-bottom:.35rem}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.3)}}
.pulse-dot{display:inline-block;width:8px;height:8px;border-radius:50%;animation:pulse 1.6s ease-in-out infinite}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
PATIENTS_PATH = os.path.join(ROOT, "data", "patients", "patient_profiles.json")

PHASES = [
    ("ocr",       "🔍", "OCR Extraction"),
    ("drug_info", "💊", "FDA Drug Lookup"),
    ("profile",   "🧩", "Profile Matching"),
    ("reasoning", "🧠", "Clinical Reasoning"),
    ("audit",     "🛡️", "Safety Audit"),
]

NODE_TO_PHASE = {
    "ocr":           "ocr",
    "drug_info":     "drug_info",
    "profile_match": "profile",
    "reasoning":     "reasoning",
    "audit":         "audit",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_patient_profiles() -> dict:
    try:
        with open(PATIENTS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def emergency_color(level: int) -> str:
    if level <= 3:    return "#22c55e"
    elif level <= 6:  return "#f59e0b"
    return "#ef4444"


def accuracy_color(score: float) -> str:
    if score >= 0.85:  return "#22c55e"
    elif score >= 0.65: return "#f59e0b"
    return "#ef4444"


def gauge_bar(value: float, max_val: float, color: str, lbl_l: str = "", lbl_r: str = "") -> str:
    pct = min(100, max(0, value / max_val * 100))
    return (
        f'<div style="display:flex;justify-content:space-between;font-size:.74rem;color:#64748b;margin-bottom:3px;">'
        f'<span>{lbl_l}</span><span>{lbl_r}</span></div>'
        f'<div class="gauge-bar-wrap"><div style="height:100%;width:{pct:.1f}%;'
        f'background:linear-gradient(90deg,{color}88,{color});border-radius:99px;transition:width .8s ease;"></div></div>'
    )


def chips_html(items, color, bg, border):
    if not items:
        return "<span style='color:#475569;font-size:.8rem;'>None</span>"
    return "".join(
        f"<span style='display:inline-flex;align-items:center;background:{bg};border:1px solid {border};"
        f"border-radius:8px;padding:2px 8px;font-size:.76rem;color:{color};margin:2px;'>{i}</span>"
        for i in items
    )


def render_phases(status_map: dict) -> str:
    html = ""
    for key, icon, label in PHASES:
        s = status_map.get(key, "idle")
        dot = ""
        if s == "active":
            dot = '<span class="pulse-dot" style="background:#00d4ff;margin-left:auto;"></span>'
        elif s == "done":
            dot = '<span style="margin-left:auto;font-size:.8rem;">✓</span>'
        html += f'<div class="step-item step-{s}">{icon} {label}{dot}</div>'
    return html


def serialize_state(state: dict) -> dict:
    result = {}
    for k, v in state.items():
        if v is None:
            result[k] = None
        elif k == "raw_image":
            result[k] = f"<bytes: {len(v)} bytes>"
        elif hasattr(v, "model_dump"):
            result[k] = v.model_dump()
        else:
            try:
                json.dumps(v)
                result[k] = v
            except Exception:
                result[k] = str(v)
    return result

with st.sidebar:
    st.html("""
    <div style="text-align:center;padding:1.2rem 0 1rem;">
        <div style="font-size:2.4rem;margin-bottom:6px;">💊</div>
        <div style="font-size:1.1rem;font-weight:800;color:#00d4ff;letter-spacing:.04em;">MedChecker AI</div>
        <div style="font-size:.72rem;color:#475569;letter-spacing:.1em;text-transform:uppercase;">Clinical Safety Platform</div>
    </div>
    """)

    st.divider()

    st.html('<div class="section-label">🧑‍⚕️ Patient Selection</div>')
    profiles = load_patient_profiles()
    patient_ids = list(profiles.keys())

    if not patient_ids:
        st.warning("No profiles found in `data/patients/patient_profiles.json`")
        selected_id = None
    else:
        selected_id = st.selectbox(
            "Patient ID",
            options=patient_ids,
            index=0,
            key="patient_select",
            label_visibility="collapsed",
        )

    if selected_id and selected_id in profiles:
        p = profiles[selected_id]
        meta      = p.get("metadata", {})
        name      = meta.get("name", "Unknown")
        age       = meta.get("age", "?")
        gender    = meta.get("gender", "?")
        updated   = meta.get("last_updated", "—")
        diseases  = p.get("diseases", [])
        allergies = p.get("allergies", [])
        meds      = p.get("current_medications", [])

        st.html(
            f"""<div class="glass-card" style="margin-top:.75rem;">
            <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:4px;">{name}</div>
            <div style="font-size:.76rem;color:#64748b;margin-bottom:1rem;">{selected_id} &nbsp;•&nbsp; {gender} &nbsp;•&nbsp; Age {age} &nbsp;•&nbsp; {updated}</div>
            <div class="section-label" style="font-size:.65rem;margin-bottom:4px;">Conditions</div>
            <div style="margin-bottom:10px;">{chips_html(diseases,  "#fca5a5","rgba(239,68,68,.08)","rgba(239,68,68,.2)")}</div>
            <div class="section-label" style="font-size:.65rem;margin-bottom:4px;">Allergies</div>
            <div style="margin-bottom:10px;">{chips_html(allergies, "#fcd34d","rgba(245,158,11,.08)","rgba(245,158,11,.2)")}</div>
            <div class="section-label" style="font-size:.65rem;margin-bottom:4px;">Current Medications</div>
            <div>{chips_html(meds, "#a5b4fc","rgba(99,102,241,.08)","rgba(99,102,241,.2)")}</div>
            </div>"""
        )

    st.divider()

    st.html('<div class="section-label">⚙️ Pipeline Status</div>')
    if "phase_status" not in st.session_state:
        st.session_state["phase_status"] = {k: "idle" for k, _, _ in PHASES}

    phase_ph = st.empty()
    phase_ph.html(render_phases(st.session_state["phase_status"]))

    st.divider()
    st.html('<div style="font-size:.7rem;color:#334155;text-align:center;">Powered by LangGraph · PaddleOCR · Groq</div>')


# ── Hero header ──────────────────────────────────────────────────────────────
st.html("""
<div style="padding:.5rem 0 1.5rem;">
    <div class="hero-title">MedChecker AI</div>
    <div style="font-size:1rem;color:#64748b;font-weight:400;margin-top:.1rem;">
        AI-Powered Clinical Drug Safety Verification Platform
    </div>
</div>
""")

col_upload, col_results = st.columns([1, 1.3], gap="large")


# ── Left column: Upload ───────────────────────────────────────────────────────
with col_upload:
    st.html('<div class="section-label">📷 Drug Label Image</div>')

    uploaded_file = st.file_uploader(
        "Upload a drug label image",
        type=["png", "jpg", "jpeg", "webp"],
        key="drug_image",
        label_visibility="collapsed",
    )

    if uploaded_file:
        # Read bytes FIRST before Image.open() consumes the pointer
        uploaded_file.seek(0)
        _img_bytes = uploaded_file.read()
        st.session_state["_cached_image_bytes"] = _img_bytes
        img = Image.open(io.BytesIO(_img_bytes))
        st.image(img, width="stretch", caption=f"📁 {uploaded_file.name}")
    else:
        st.html("""
        <div style="height:220px;display:flex;flex-direction:column;align-items:center;
             justify-content:center;color:#334155;border-radius:12px;gap:10px;">
            <div style="font-size:3rem;">🏷️</div>
            <div style="font-size:.85rem;text-align:center;max-width:200px;line-height:1.5;">
                Drag &amp; drop or click to upload a medication label
            </div>
        </div>""")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    run_disabled = (uploaded_file is None or selected_id is None)
    run_btn = st.button("⚡ Run Analysis", use_container_width=True, disabled=run_disabled, key="run_btn")

    if run_disabled:
        st.html(
            '<div style="font-size:.78rem;color:#475569;text-align:center;margin-top:6px;">Upload an image to enable analysis</div>'
        )

    # Manual drug name override — shown always so user can bypass bad OCR
    with st.expander("✏️ Override Drug Name (if OCR fails)", expanded=False):
        manual_drug_name = st.text_input(
            "Drug name (active ingredient)",
            placeholder="e.g. ibuprofen, warfarin, melatonin…",
            key="manual_drug_name",
            label_visibility="collapsed",
        )
        if manual_drug_name:
            st.html(
                f'<div style="font-size:.78rem;color:#22c55e;margin-top:4px;">'
                f'✓ Will use <strong>{manual_drug_name.strip()}</strong> instead of OCR result.</div>'
            )

    # OCR result card — shown after pipeline run
    if "ocr_result" in st.session_state:
        ocr = st.session_state["ocr_result"]
        st.html("<div style='height:.75rem'></div>")
        st.html('<div class="section-label">🔍 OCR Result</div>')

        conf_pct   = ocr.ocr_confidence * 100
        conf_color = "#22c55e" if conf_pct >= 75 else ("#f59e0b" if conf_pct >= 50 else "#ef4444")
        review_badge = (
            '<span style="background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.4);'
            'border-radius:6px;padding:2px 8px;font-size:.72rem;color:#f59e0b;margin-left:8px;">⚠️ Needs Review</span>'
            if ocr.ocr_needs_review else ""
        )

        st.html(
            f"""<div class="glass-card">
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:.75rem;">
                <span style="font-size:1.05rem;font-weight:700;color:#e2e8f0;">{ocr.scanned_drug_name or "—"}</span>
                {review_badge}
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;">
                <span class="metric-pill">💊 Dosage: {ocr.scanned_dosage or "—"}</span>
                <span class="metric-pill">🔄 Retries: {ocr.ocr_retry_count}</span>
            </div>
            <div style="font-size:.75rem;color:#64748b;margin-bottom:4px;">OCR Confidence — {conf_pct:.1f}%</div>
            {gauge_bar(conf_pct, 100, conf_color, "0%", "100%")}
            </div>"""
        )

        # Show OCR error details if present
        ocr_err = st.session_state.get("final_state", {}).get("ocr_error")
        if ocr_err:
            with st.expander("⚠️ OCR Error Details", expanded=True):
                st.html(
                    f'<div style="font-size:.82rem;color:#fcd34d;line-height:1.7;white-space:pre-wrap;">{ocr_err}</div>'
                )
                st.html(
                    '<div style="font-size:.78rem;color:#64748b;margin-top:.5rem;">'
                    '💡 Use the <strong>Override Drug Name</strong> expander above to type the drug name manually.</div>'
                )



# ── Right column: Results ─────────────────────────────────────────────────────
with col_results:
    st.html('<div class="section-label">📊 Analysis Results</div>')

    if "final_state" not in st.session_state:
        st.html("""
        <div class="glass-card" style="height:340px;display:flex;flex-direction:column;
             align-items:center;justify-content:center;gap:12px;color:#334155;">
            <div style="font-size:3rem;">🧬</div>
            <div style="font-size:.9rem;text-align:center;max-width:240px;line-height:1.6;">
                Upload a drug label and click
                <strong style="color:#00d4ff">Run Analysis</strong>
                to see the clinical safety verdict.
            </div>
        </div>""")

    else:
        final          = st.session_state["final_state"]
        reasoning      = final.get("reasoning_verdict")
        audit          = final.get("audit_verdict")
        requires_human = final.get("requires_human_intervention", True)
        safety_profile = final.get("safety_profile")

        # Verdict card
        if reasoning:
            decision = (reasoning.decision or "").upper()
            if decision == "APPROVE":
                v_cls, v_icon = "verdict-approve", "✅"
            elif decision == "DENY":
                v_cls, v_icon = "verdict-deny", "🚫"
            else:
                v_cls, v_icon, decision = "verdict-hold", "⏸️", "HOLD FOR REVIEW"

            st.html(
                f"""<div class="glass-card" style="margin-bottom:1rem;">
                <div class="section-label" style="margin-bottom:.6rem;">Clinical Verdict</div>
                <div class="verdict-badge {v_cls}" style="margin-bottom:1rem;">{v_icon}&nbsp; {decision}</div>
                <div style="font-size:.88rem;color:#cbd5e1;line-height:1.65;margin-top:.75rem;">{reasoning.explanation}</div>
                </div>"""
            )

            if reasoning.detected_matches:
                st.html('<div class="section-label" style="margin-top:.5rem;">⚠️ Detected Risk Interactions</div>')
                matches_html = "".join(f'<div class="match-item">⚡ {m}</div>' for m in reasoning.detected_matches)
                st.html(f'<div style="margin-bottom:1rem;">{matches_html}</div>')
            else:
                st.html("""
                <div style="padding:.6rem .9rem;background:rgba(34,197,94,.07);border-left:3px solid rgba(34,197,94,.4);
                     border-radius:0 8px 8px 0;font-size:.84rem;color:#86efac;margin-bottom:1rem;">
                    ✅ No risk interactions detected.
                </div>""")

        # Audit score gauges
        if audit:
            ac = accuracy_color(audit.accuracy_score)
            ec = emergency_color(audit.emergency_level)
            col_a, col_b = st.columns(2)

            with col_a:
                st.html(
                    f"""<div class="glass-card" style="text-align:center;">
                    <div class="section-label" style="font-size:.65rem;">Accuracy Score</div>
                    <div style="font-size:2.2rem;font-weight:800;color:{ac};line-height:1.1;margin-bottom:.5rem;">{audit.accuracy_score:.2f}</div>
                    {gauge_bar(audit.accuracy_score, 1.0, ac, "0.0", "1.0")}
                    </div>"""
                )

            with col_b:
                st.html(
                    f"""<div class="glass-card" style="text-align:center;">
                    <div class="section-label" style="font-size:.65rem;">Emergency Level</div>
                    <div style="font-size:2.2rem;font-weight:800;color:{ec};line-height:1.1;margin-bottom:.5rem;">
                        {audit.emergency_level}<span style="font-size:1rem;color:#475569;"> / 10</span>
                    </div>
                    {gauge_bar(audit.emergency_level, 10, ec, "1", "10")}
                    </div>"""
                )

        # Human intervention alert
        if requires_human:
            st.html("""
            <div class="alert-human" style="margin-top:1rem;">
                <div style="font-size:1.4rem;">🚨</div>
                <div>
                    <div style="font-weight:700;margin-bottom:3px;">Human Review Required</div>
                    <div style="opacity:.8;font-size:.83rem;">
                        This case did not meet the automatic threshold (accuracy &ge; 0.85 &amp;
                        emergency &lt; 5). A pharmacist or physician must review before dispensing.
                    </div>
                </div>
            </div>""")
        else:
            st.html("""
            <div style="margin-top:1rem;padding:.75rem 1rem;background:rgba(34,197,94,.07);
                 border:1px solid rgba(34,197,94,.2);border-radius:12px;
                 display:flex;align-items:center;gap:10px;font-size:.85rem;color:#86efac;">
                <span style="font-size:1.2rem;">🟢</span>
                <span>Automatic approval threshold met — no human review required.</span>
            </div>""")

        # FDA safety profile expander
        if safety_profile:
            st.html("<div style='height:1rem'></div>")
            with st.expander(f"🔬 FDA Safety Data — {safety_profile.query_name}", expanded=False):
                st.html(
                    f"""<div style="margin-bottom:.75rem;">
                    <span class="metric-pill">RxCUIs: {', '.join(safety_profile.rxcuis) or 'N/A'}</span>&nbsp;
                    <span class="metric-pill">Ingredients: {', '.join(safety_profile.ingredients) or 'N/A'}</span>
                    </div>"""
                )
                for ingredient, info in safety_profile.safety_profiles.items():
                    st.markdown(f"**{ingredient.upper()}**")
                    if info:
                        fda_fields = {
                            "Contraindications":  info.contraindications,
                            "Boxed Warning":       info.boxed_warning,
                            "Drug Interactions":   info.drug_interactions,
                            "Food Interactions":   info.food_interactions,
                            "Warnings & Cautions": info.warnings_and_cautions,
                            "Pregnancy":           info.pregnancy,
                        }
                        for lbl, val in fda_fields.items():
                            if val:
                                with st.expander(f"  📋 {lbl}", expanded=False):
                                    st.html(f'<div style="font-size:.82rem;color:#94a3b8;line-height:1.6;">{val}</div>')
                    else:
                        st.markdown('<div style="font-size:.82rem;color:#475569;">No FDA data available.</div>', unsafe_allow_html=True)

        # Raw state JSON debug
        with st.expander("🗂️ Raw Pipeline State (JSON)", expanded=False):
            st.json(serialize_state(final))


# ── Pipeline execution ────────────────────────────────────────────────────────
if run_btn and uploaded_file and selected_id:
    # Read bytes from cache (uploaded_file pointer may be exhausted by the preview)
    image_bytes = st.session_state.get("_cached_image_bytes") or b""
    if not image_bytes:
        st.error("Image data lost — please re-upload the file and try again.")
        st.stop()

    for key in ("ocr_result", "final_state"):
        st.session_state.pop(key, None)
    st.session_state["phase_status"] = {k: "idle" for k, _, _ in PHASES}
    phase_ph.html(render_phases(st.session_state["phase_status"]))

    progress_bar = st.progress(0, text="Initialising pipeline…")
    phase_order  = [k for k, _, _ in PHASES]
    total_nodes  = len(PHASES)

    # Warn the user upfront that OCR model loading can be slow
    ocr_info = st.info(
        "⏳ **PaddleOCR is loading** — the first run downloads and initialises 5 deep learning models "
        "(PP-OCRv6, UVDoc, etc.). This takes **1–3 minutes** and only happens once. "
        "Subsequent runs will be much faster. Please wait…",
        icon="🤖",
    )

    try:
        from src.graph import graph  # lazy import keeps page-load fast

        initial_state = {
            "raw_image":                   image_bytes,
            "patient_id":                  selected_id,
            "ocr":                         None,
            "extracted_drug_name":         None,
            "ocr_error":                   None,
            "safety_profile":              None,
            "matched_risk_context":        "",
            "reasoning_verdict":           None,
            "audit_verdict":               None,
            "requires_human_intervention": True,
        }

        # If user provided a manual override, inject it to bypass OCR
        manual_override = st.session_state.get("manual_drug_name", "").strip()
        if manual_override:
            from src.schemas.state_sections import OCRSection
            initial_state["ocr"] = OCRSection(
                scanned_drug_name=manual_override,
                scanned_dosage="",
                ocr_confidence=1.0,
                ocr_needs_review=False,
                ocr_retry_count=0,
            )
            initial_state["extracted_drug_name"] = manual_override
            st.session_state["ocr_result"] = initial_state["ocr"]
            # Skip the OCR node — jump straight to drug_info
            from src.graph import graph
            from langgraph.graph import START
            st.info(f"🔑 Using manual drug name: **{manual_override}** (OCR skipped)")

        final_state = dict(initial_state)

        for step in graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in step.items():
                phase_key = NODE_TO_PHASE.get(node_name)

                if phase_key and phase_key in phase_order:
                    idx = phase_order.index(phase_key)
                    for i, pk in enumerate(phase_order):
                        if i < idx:
                            st.session_state["phase_status"][pk] = "done"
                        elif i == idx:
                            st.session_state["phase_status"][pk] = "active"
                    phase_ph.html(render_phases(st.session_state["phase_status"]))
                    label = next(lbl for k, _, lbl in PHASES if k == phase_key)
                    progress_bar.progress((idx + 0.5) / total_nodes, text=f"Running: {label}…")

                if isinstance(node_output, dict):
                    final_state.update(node_output)

                if phase_key and phase_key in phase_order:
                    st.session_state["phase_status"][phase_key] = "done"
                    idx = phase_order.index(phase_key)
                    phase_ph.html(render_phases(st.session_state["phase_status"]))
                    label = next(lbl for k, _, lbl in PHASES if k == phase_key)
                    progress_bar.progress((idx + 1) / total_nodes, text=f"Done: {label}")

        if final_state.get("ocr"):
            st.session_state["ocr_result"] = final_state["ocr"]
        st.session_state["final_state"] = final_state

        progress_bar.progress(1.0, text="✅ Analysis complete!")
        time.sleep(0.6)
        progress_bar.empty()

    except Exception as exc:
        progress_bar.empty()
        st.error(f"**Pipeline error:** {exc}")
        import traceback
        with st.expander("🐛 Full traceback"):
            st.code(traceback.format_exc(), language="python")
        # Do NOT rerun on error — keeps error message visible
        st.stop()

    # Only rerun on success to refresh results panel
    st.rerun()
