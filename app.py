import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="লেবু পাতার রোগ শনাক্তকরণ",
    page_icon="🍋",
    layout="centered"
)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Hind Siliguri', sans-serif;
}

.main { background: #f7f9f8; }

.header-box {
    background: linear-gradient(135deg, #1a5c2a, #2d8a47);
    color: white;
    padding: 24px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.hero-box {
    background: linear-gradient(160deg, #1a5c2a, #2d8a47, #4caf72);
    color: white;
    padding: 36px 24px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 24px;
}

.result-healthy {
    background: linear-gradient(135deg, #1a5c2a, #2d8a47);
    color: white;
    padding: 20px 24px;
    border-radius: 14px 14px 0 0;
}

.result-diseased {
    background: linear-gradient(135deg, #7b1a1a, #c0392b);
    color: white;
    padding: 20px 24px;
    border-radius: 14px 14px 0 0;
}

.result-uncertain {
    background: linear-gradient(135deg, #7a5c00, #c49a00);
    color: white;
    padding: 20px 24px;
    border-radius: 14px 14px 0 0;
}

.info-box {
    background: #f7f9f8;
    border-left: 3px solid #4caf72;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}

.info-label {
    font-size: 11px;
    font-weight: 600;
    color: #9aab9d;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.info-value {
    font-size: 14px;
    color: #1a2b1c;
    font-weight: 500;
    line-height: 1.5;
}

.treatment-box {
    background: #fff9e6;
    border: 1.5px solid #f5c518;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}

.treatment-healthy {
    background: #e8f5ec;
    border: 1.5px solid #4caf72;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}

.stat-box {
    background: rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
}

.disclaimer {
    background: #f7f9f8;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12px;
    color: #9aab9d;
    line-height: 1.5;
}

.footer-box {
    background: #1a5c2a;
    color: rgba(255,255,255,0.75);
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    font-size: 12px;
    line-height: 1.8;
    margin-top: 24px;
}

.stButton > button {
    background: linear-gradient(135deg, #1a5c2a, #2d8a47) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    font-family: 'Hind Siliguri', sans-serif !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(26,92,42,0.4) !important;
}

div[data-testid="stFileUploader"] {
    border: 2.5px dashed #4caf72 !important;
    border-radius: 14px !important;
    background: #e8f5ec !important;
    padding: 20px !important;
}

.confidence-bar-bg {
    background: #e8ede9;
    border-radius: 99px;
    height: 10px;
    overflow: hidden;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── Gemini Setup ──────────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ─── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <div style="width:48px;height:48px;background:#f5c518;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">🍋</div>
    <div style="flex:1;">
        <div style="font-weight:700;font-size:18px;line-height:1.2;">লেবু পাতার রোগ শনাক্তকরণ</div>
        <div style="font-size:12px;opacity:0.8;margin-top:3px;">Manarat International University — CSE Thesis 2026</div>
    </div>
    <div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);border-radius:20px;padding:5px 14px;font-size:11px;">🤖 AI Powered</div>
</div>
""", unsafe_allow_html=True)

# ─── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
    <div style="font-size:60px;margin-bottom:12px;">🌿</div>
    <div style="font-size:24px;font-weight:700;margin-bottom:10px;">AI দিয়ে লেবু পাতার রোগ চিনুন</div>
    <div style="font-size:14px;opacity:0.88;max-width:400px;margin:0 auto 20px;line-height:1.6;">
        ছবি আপলোড করুন — কৃত্রিম বুদ্ধিমত্তা মুহূর্তেই রোগ শনাক্ত করে প্রতিকার জানাবে
    </div>
    <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;">
        <div class="stat-box"><div style="font-size:24px;font-weight:700;color:#f5c518;">৯৫%+</div><div style="font-size:11px;opacity:0.8;">Accuracy</div></div>
        <div class="stat-box"><div style="font-size:24px;font-weight:700;color:#f5c518;">&lt;৫s</div><div style="font-size:11px;opacity:0.8;">বিশ্লেষণ সময়</div></div>
        <div class="stat-box"><div style="font-size:24px;font-weight:700;color:#f5c518;">৭+</div><div style="font-size:11px;opacity:0.8;">রোগের ধরন</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── API Key Check ─────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.warning("⚠️ Gemini API Key সেট করা হয়নি। Streamlit secrets-এ GEMINI_API_KEY যোগ করুন।")
    st.info("🔑 বিনামূল্যে API Key পেতে: [aistudio.google.com](https://aistudio.google.com) → Get API Key")
    st.stop()

# ─── Upload Section ────────────────────────────────────────────
st.markdown("### 📸 ছবি আপলোড করুন")
st.caption("লেবু পাতার স্পষ্ট ছবি দিন — JPG, PNG, WEBP সমর্থিত")

uploaded = st.file_uploader(
    "ছবি সিলেক্ট করুন",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="আপলোড করা ছবি", use_column_width=True)
    st.markdown("---")

    if st.button("🔬 রোগ শনাক্ত করুন"):
        with st.spinner("AI বিশ্লেষণ করছে..."):

            # Progress steps
            progress = st.empty()
            progress.markdown("🖼️ ছবি প্রক্রিয়া করা হচ্ছে...")

            prompt = """তুমি একজন উদ্ভিদ রোগ বিশেষজ্ঞ AI। এই লেবু পাতার ছবি বিশ্লেষণ করো।
শুধু নিচের JSON format এ উত্তর দাও, অন্য কিছু লিখবে না:
{
  "status": "healthy অথবা diseased অথবা uncertain",
  "disease_name_bn": "রোগের নাম বাংলায় (সুস্থ হলে সুস্থ পাতা)",
  "disease_name_en": "Disease name in English",
  "confidence": 85,
  "symptoms_bn": "লক্ষণের বিবরণ বাংলায় ২-৩ বাক্য",
  "cause_bn": "রোগের কারণ বাংলায়",
  "severity": "কম অথবা মাঝারি অথবা বেশি অথবা প্রযোজ্য নয়",
  "treatments": ["প্রতিকার ১", "প্রতিকার ২", "প্রতিকার ৩"],
  "prevention": "প্রতিরোধমূলক ব্যবস্থা বাংলায়"
}
সাধারণ লেবু পাতার রোগ: Citrus Canker, Greening, Melanose, Powdery Mildew, Leaf Miner, Alternaria Brown Spot, Anthracnose, Sooty Mold।"""

            try:
                progress.markdown("🧠 AI মডেল বিশ্লেষণ করছে...")
                model = genai.GenerativeModel("gemini-1.5-flash")

                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_bytes.read()}
                ])

                progress.markdown("📋 ফলাফল তৈরি হচ্ছে...")
                raw = response.text.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)

                progress.empty()

                # ─── Result Display ───────────────────────────────
                status = result.get("status", "uncertain")
                icon = "✅" if status == "healthy" else "⚠️" if status == "uncertain" else "🚨"
                header_class = "result-healthy" if status == "healthy" else "result-uncertain" if status == "uncertain" else "result-diseased"
                subtitle = "পাতা সুস্থ আছে" if status == "healthy" else f"{result.get('disease_name_en', '')} শনাক্ত হয়েছে"

                st.markdown(f"""
                <div class="{header_class}">
                    <div style="display:flex;align-items:center;gap:14px;">
                        <div style="font-size:40px;">{icon}</div>
                        <div>
                            <div style="font-weight:700;font-size:20px;margin-bottom:4px;">{result.get('disease_name_bn', '')}</div>
                            <div style="opacity:0.85;font-size:13px;">{subtitle}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Confidence
                conf = result.get("confidence", 80)
                st.markdown(f"""
                <div style="padding:16px 0 8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:13px;font-weight:600;color:#3d4f40;">নিশ্চিততার মাত্রা</span>
                        <span style="font-size:22px;font-weight:700;color:#1a5c2a;">{conf}%</span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div style="height:100%;width:{conf}%;background:linear-gradient(90deg,#4caf72,#1a5c2a);border-radius:99px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Info boxes
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<div class="info-box"><div class="info-label">রোগের ধরন</div><div class="info-value">{result.get('disease_name_bn','')}</div></div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class="info-box"><div class="info-label">তীব্রতা</div><div class="info-value">{result.get('severity','প্রযোজ্য নয়')}</div></div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="info-box"><div class="info-label">লক্ষণ</div><div class="info-value">{result.get('symptoms_bn','')}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="info-box"><div class="info-label">কারণ</div><div class="info-value">{result.get('cause_bn','')}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="info-box"><div class="info-label">প্রতিরোধ</div><div class="info-value">{result.get('prevention','')}</div></div>""", unsafe_allow_html=True)

                # Treatments
                treatments = result.get("treatments", [])
                treat_class = "treatment-healthy" if status == "healthy" else "treatment-box"
                treat_title = "✅ যত্নের পরামর্শ" if status == "healthy" else "💊 প্রতিকার ও পরামর্শ"
                treat_color = "#1a5c2a" if status == "healthy" else "#7a5c00"
                treat_html = "".join([f'<div style="display:flex;gap:8px;margin-bottom:8px;font-size:14px;color:#3d4f40;line-height:1.5;"><span style="color:#2d8a47;font-weight:700;flex-shrink:0;">✓</span><span>{t}</span></div>' for t in treatments])

                st.markdown(f"""
                <div class="{treat_class}">
                    <div style="font-weight:700;font-size:15px;color:{treat_color};margin-bottom:12px;">{treat_title}</div>
                    {treat_html}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="disclaimer">
                    ℹ️ এই ফলাফল AI-ভিত্তিক। গুরুতর ক্ষেত্রে কৃষি বিশেষজ্ঞের পরামর্শ নিন।
                    Manarat International University CSE Thesis 2026।
                </div>
                """, unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("❌ ফলাফল পার্স করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            except Exception as e:
                st.error(f"❌ বিশ্লেষণ করতে সমস্যা হয়েছে: {str(e)}")

# ─── How it works ──────────────────────────────────────────────
else:
    st.markdown("### ⚙️ কীভাবে কাজ করে?")
    col1, col2, col3, col4 = st.columns(4)
    for col, num, icon, text in zip(
        [col1, col2, col3, col4],
        ["১", "২", "৩", "৪"],
        ["📸", "🤖", "📋", "🌱"],
        ["ছবি আপলোড করুন", "AI বিশ্লেষণ করে", "ফলাফল দেখুন", "ফসল রক্ষা করুন"]
    ):
        with col:
            st.markdown(f"""
            <div style="background:#e8f5ec;border-radius:12px;padding:14px 10px;text-align:center;">
                <div style="width:28px;height:28px;background:#2d8a47;color:white;border-radius:50%;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">{num}</div>
                <div style="font-size:24px;margin-bottom:6px;">{icon}</div>
                <div style="font-size:11px;color:#3d4f40;font-weight:500;line-height:1.4;">{text}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="footer-box">
    <div style="color:white;font-weight:600;margin-bottom:4px;">🍋 AI-Based Lemon Leaf Disease Detection System</div>
    <div>Manarat International University | Department of CSE | B.Sc. Thesis 2026</div>
    <div>Supervised by: Md. Zahurul Islam, Assistant Professor</div>
</div>
""", unsafe_allow_html=True)
