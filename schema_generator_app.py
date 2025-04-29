import streamlit as st
import json
import base64
import streamlit.components.v1 as components
from datetime import time

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")

def build_jsonld():
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": st.session_state.name,
        "url": st.session_state.url,
        "logo": st.session_state.logo,
        "description": st.session_state.description,
        "telephone": st.session_state.telephone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": st.session_state.street,
            "addressLocality": st.session_state.city,
            "addressRegion": st.session_state.region,
            "postalCode": st.session_state.postal,
            "addressCountry": st.session_state.country,
        },
    }

    same_as = [u.strip() for u in st.session_state.socials.splitlines() if u.strip()]
    if same_as:
        schema["sameAs"] = same_as

    areas = [a.strip() for a in st.session_state.areas.splitlines() if a.strip()]
    if areas:
        schema["areaServed"] = areas

    hours = []
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        if st.session_state.get(f"chk_{day}", False):
            opens = st.session_state[f"open_{day}"].strftime("%H:%M")
            closes = st.session_state[f"close_{day}"].strftime("%H:%M")
            hours.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": day,
                "opens": opens,
                "closes": closes,
            })
    if hours:
        schema["openingHoursSpecification"] = hours

    offers = []
    for line in st.session_state.services.splitlines():
        if "," in line:
            svc_name, svc_desc = [p.strip() for p in line.split(",",1)]
            offers.append({
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": svc_name,
                    "description": svc_desc,
                }
            })
    if offers:
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Our Services",
            "itemListElement": offers
        }

    raw_json = json.dumps(schema, indent=2)
    # wrap with actual newlines
    return f"""<script type="application/ld+json">
{raw_json}
</script>"""

# --- UI inputs (same as before) ---
st.text_input("Business Name", key="name", placeholder="Acme Corp")
st.text_input("Business URL", key="url", placeholder="https://example.com")
st.text_input("Logo URL", key="logo", placeholder="https://example.com/logo.png")
st.text_area("Business Description", key="description", placeholder="Acme Corp provides top-notch solutions.")
st.text_input("Phone Number", key="telephone", placeholder="+1-555-123-4567")

st.text_input("Street Address", key="street", placeholder="123 Main St")
st.text_input("City", key="city", placeholder="Anytown")
st.text_input("Region/State", key="region", placeholder="CA")
st.text_input("Postal Code", key="postal", placeholder="12345")
st.text_input("Country Code", key="country", placeholder="US")

st.text_area("Social Profiles", key="socials")
st.text_area("Areas Served", key="areas")
st.text_area("Services (name, description)", key="services")

st.markdown("### Opening Hours")
for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
    c1, c2, c3 = st.columns([1,2,2])
    with c1:
        st.checkbox(day, key=f"chk_{day}")
    if st.session_state.get(f"chk_{day}", False):
        with c2:
            st.time_input(f"{day} opens at", value=time(9,0), key=f"open_{day}")
        with c3:
            st.time_input(f"{day} closes at", value=time(17,0), key=f"close_{day}")

# --- Generate & show ---
if st.button("Generate JSON-LD Schema"):
    script_block = build_jsonld()
    b64 = base64.b64encode(script_block.encode("utf-8")).decode("utf-8")

    html = f'''
<button id="copy-btn">Copy JSON-LD</button>
<pre id="json-output" style="background:#f0f0f0;
    padding:10px;border-radius:5px;overflow:auto;
    white-space:pre-wrap;word-wrap:break-word;"></pre>
<script>
  const raw = atob("{b64}");
  document.getElementById("json-output").textContent = raw;
  document.getElementById("copy-btn").addEventListener("click", () => {{
    navigator.clipboard.writeText(raw).then(() => {{
      const btn = document.getElementById("copy-btn");
      btn.textContent = "Copied!";
      setTimeout(() => btn.textContent = "Copy JSON-LD", 2000);
    }});
  }});
</script>
'''
    components.html(html, height=500)

    st.markdown("""
**How to use:**  
1. Click **Copy JSON-LD**.  
2. Paste directly into your page’s HTML.  
3. Validate with Google’s Rich Results Test.
""")
