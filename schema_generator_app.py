import streamlit as st
import json
import streamlit.components.v1 as components
from datetime import time

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")

# Collect basic business information
name = st.text_input("Business Name", placeholder="Acme Corp")
url = st.text_input("Business URL (e.g. https://example.com)", placeholder="https://example.com")
logo = st.text_input("Logo URL (absolute URL)", placeholder="https://example.com/logo.png")
description = st.text_area("Business Description", placeholder="Acme Corp provides top-notch solutions.")

# Contact and address
telephone = st.text_input("Phone Number", placeholder="+1-555-123-4567")
street = st.text_input("Street Address", placeholder="123 Main St")
city = st.text_input("City", placeholder="Anytown")
region = st.text_input("Region/State", placeholder="CA")
postal = st.text_input("Postal Code", placeholder="12345")
country = st.text_input("Country Code (e.g. US)", placeholder="US")

# Social profiles
socials = st.text_area(
    "Social Profiles (one URL per line, optional)",
    placeholder="https://facebook.com/yourbusiness\nhttps://twitter.com/yourbusiness"
)

# Areas served
areas_text = st.text_area(
    "Areas Served (one place per line, optional)",
    placeholder="Anytown, CA\nOtherville, TX"
)

# Opening hours via checkboxes + time inputs
st.markdown("### Opening Hours (check days and set times)")
week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
hours = []
for day in week_days:
    col1, col2 = st.columns([1, 2])
    with col1:
        selected = st.checkbox(day, key=f"chk_{day}")
    with col2:
        if selected:
            open_time = st.time_input(f"{day} opens at", value=time(9, 0), key=f"open_{day}")
            close_time = st.time_input(f"{day} closes at", value=time(17, 0), key=f"close_{day}")
            hours.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": day,
                "opens": open_time.strftime("%H:%M"),
                "closes": close_time.strftime("%H:%M"),
            })

# Hidden Offer Catalog Name
catalog_name = "Our Services"

# Services input (name, description)
services_text = st.text_area(
    "Services (one per line, format: name, description)",
    placeholder="Service One, Brief description.\nService Two, Another description."
)

if st.button("Generate JSON-LD Schema"):
    # Build base schema
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
    # Include sameAs if provided
    same_as = [line.strip() for line in socials.splitlines() if line.strip()]
    if same_as:
        schema["sameAs"] = same_as

    # Include areaServed if provided
    areas = [line.strip() for line in areas_text.splitlines() if line.strip()]
    if areas:
        schema["areaServed"] = areas

    # Include openingHoursSpecification
    if hours:
        schema["openingHoursSpecification"] = hours

    # Include services catalog if provided
    offers = []
    for line in services_text.splitlines():
        if "," in line:
            svc_name, desc = [part.strip() for part in line.split(",", 1)]
            offers.append({
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": svc_name,
                    "description": desc,
                }
            })
    if offers:
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": catalog_name,
            "itemListElement": offers,
        }

    # Render JSON-LD and copy button
    json_ld = json.dumps(schema, indent=2)
    html = f"""
    <button id=\"copy-btn\">Copy JSON-LD</button>
    <pre id=\"json-output\" style=\"background:#f0f0f0;padding:10px;border-radius:5px;overflow:auto;white-space:pre-wrap;word-wrap:break-word;\">{json_ld}</pre>
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
    """
    components.html(html, height=500)

    st.markdown("""
**How to use:**  
1. Click the 'Copy JSON-LD' button above to copy the full JSON-LD.  
2. Paste it into a `<script type=\"application/ld+json\">` tag on your page.  
3. Verify with Google's Rich Results Test.
""")
