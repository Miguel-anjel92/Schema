import streamlit as st
import json
import streamlit.components.v1 as components
from datetime import time

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")

def build_jsonld():
    # grab everything from session_state
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

    # sameAs
    same_as = [u.strip() for u in st.session_state.socials.splitlines() if u.strip()]
    if same_as:
        schema["sameAs"] = same_as

    # areaServed
    areas = [a.strip() for a in st.session_state.areas.splitlines() if a.strip()]
    if areas:
        schema["areaServed"] = areas

    # openingHoursSpecification
    hours = []
    week_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    for day in week_days:
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

    # services → OfferCatalog
    offers = []
    for line in st.session_state.services.splitlines():
        if "," in line:
            name, desc = [p.strip() for p in line.split(",", 1)]
            offers.append({
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": name,
                    "description": desc,
                }
            })
    if offers:
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Our Services",
            "itemListElement": offers
        }

    # dump + wrap in <script>
    raw_json = json.dumps(schema, indent=2)
    return f'<script type="application/ld+json">\n{raw_json}\n</script>'

# --- Inputs ---
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

st.text_area("Social Profiles (one URL per line)", key="socials",
             placeholder="https://facebook.com/yourbusiness\nhttps://twitter.com/yourbusiness")
st.text_area("Areas Served (one per line)", key="areas",
             placeholder="Anytown, CA\nOtherville, TX")
st.text_area("Services (format: name, description per line)", key="services",
             placeholder="Service One, Brief description.\nService Two, Another description.")

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

# --- Generate & display ---
if st.button("Generate JSON-LD Schema"):
    script_block = build_jsonld()

    # Build HTML with escape/display logic + copy raw
    html = f"""
    <button id="copy-btn">Copy JSON-LD</button>
    <pre id="json-output" style="
        background:#f0f0f0;
        padding:10px;
        border-radius:5px;
        overflow:auto;
        white-space:pre-wrap;
        word-wrap:break-word;
    "></pre>

    <script>
      // raw <script> block
      const raw = `{script_block}`;
      // escaped for visible display
      const escaped = raw.replace(/</g, "&lt;").replace(/>/g, "&gt;");
      document.getElementById("json-output").innerHTML = escaped;

      document.getElementById("copy-btn").addEventListener("click", () => {{
        navigator.clipboard.writeText(raw).then(() => {{
          const btn = document.getElementById("copy-btn");
          btn.innerText = "Copied!";
          setTimeout(() => btn.innerText = "Copy JSON-LD", 2000);
        }});
      }});
    </script>
    """

    components.html(html, height=500)
    st.markdown("""
**How to use:**  
1. Click **Copy JSON-LD** — it copies the full `<script type="application/ld+json">…</script>` block.  
2. Paste directly into your page’s HTML.  
3. Verify with Google’s Rich Results Test.
""")
