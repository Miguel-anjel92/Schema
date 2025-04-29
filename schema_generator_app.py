import streamlit as st
import json
import streamlit.components.v1 as components
from datetime import time

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")

def build_jsonld():
    # Collect inputs
    name = st.session_state.get("name")
    url = st.session_state.get("url")
    logo = st.session_state.get("logo")
    description = st.session_state.get("description")
    telephone = st.session_state.get("telephone")
    street = st.session_state.get("street")
    city = st.session_state.get("city")
    region = st.session_state.get("region")
    postal = st.session_state.get("postal")
    country = st.session_state.get("country")
    socials = st.session_state.get("socials", "")
    areas_text = st.session_state.get("areas", "")
    services_text = st.session_state.get("services", "")

    # Base schema
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": name,
        "url": url,
        "logo": logo,
        "description": description,
        "telephone": telephone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": street,
            "addressLocality": city,
            "addressRegion": region,
            "postalCode": postal,
            "addressCountry": country,
        },
    }

    # sameAs
    same_as = [line.strip() for line in socials.splitlines() if line.strip()]
    if same_as:
        schema["sameAs"] = same_as

    # areaServed
    areas = [line.strip() for line in areas_text.splitlines() if line.strip()]
    if areas:
        schema["areaServed"] = areas

    # openingHoursSpecification
    hours_specs = []
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        if st.session_state.get(f"chk_{day}", False):
            o = st.session_state[f"open_{day}"].strftime("%H:%M")
            c = st.session_state[f"close_{day}"].strftime("%H:%M")
            hours_specs.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": day,
                "opens": o,
                "closes": c
            })
    if hours_specs:
        schema["openingHoursSpecification"] = hours_specs

    # services → offers
    catalog_name = "Our Services"
    offers = []
    for line in services_text.splitlines():
        if "," in line:
            svc, desc = [p.strip() for p in line.split(",",1)]
            offers.append({
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": svc,
                    "description": desc
                }
            })
    if offers:
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": catalog_name,
            "itemListElement": offers
        }

    # dump + wrap
    json_ld = json.dumps(schema, indent=2)
    script_tag = (
        '<script type="application/ld+json">\n'
        f'{json_ld}\n'
        '</script>'
    )
    return script_tag

# --- sidebar inputs (so build_jsonld can read via session_state) ---
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
st.text_area("Social Profiles (one URL per line)", key="socials")
st.text_area("Areas Served (one per line)", key="areas")
st.text_area("Services (name, description per line)", key="services")

st.markdown("### Opening Hours")
for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
    cols = st.columns([1,2,2])
    with cols[0]:
        st.checkbox(day, key=f"chk_{day}")
    with cols[1]:
        if st.session_state.get(f"chk_{day}"):
            st.time_input(f"{day} opens at", value=time(9,0), key=f"open_{day}")
    with cols[2]:
        if st.session_state.get(f"chk_{day}"):
            st.time_input(f"{day} closes at", value=time(17,0), key=f"close_{day}")

# --- Generate & display ---
if st.button("Generate JSON-LD Schema"):
    script_block = build_jsonld()
    components.html(
        f"""
        <button id="copy-btn">Copy JSON-LD</button>
        <pre id="json-output" style="
            background:#f0f0f0;padding:10px;border-radius:5px;
            overflow:auto;white-space:pre-wrap;word-wrap:break-word;">
            {script_block}
        </pre>
        <script>
          const btn = document.getElementById('copy-btn');
          btn.addEventListener('click', () => {{
            const text = document.getElementById('json-output').innerText;
            navigator.clipboard.writeText(text).then(() => {{
              btn.innerText = 'Copied!';
              setTimeout(() => btn.innerText = 'Copy JSON-LD', 2000);
            }});
          }});
        </script>
        """,
        height=500
    )

    st.markdown("""
**How to use:**  
1. Click 'Copy JSON-LD' — it already includes `<script type="application/ld+json">` around the JSON.  
2. Paste directly into your page’s HTML.  
3. Validate with Google’s Rich Results Test.
""")
    # you now also have `script_block` returned if you want to log it or reuse elsewhere
