import streamlit as st
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")

# Collect basic business information
name = st.text_input(
    "Business Name", value="", placeholder="Acme Corp"
)
url = st.text_input(
    "Business URL (e.g. https://example.com)", value="", placeholder="https://example.com"
)
logo = st.text_input(
    "Logo URL (absolute URL)", value="", placeholder="https://example.com/logo.png"
)
description = st.text_area(
    "Business Description",
    value="",
    placeholder="Acme Corp provides top-notch solutions to meet all your needs."
)

# Contact and address
telephone = st.text_input(
    "Phone Number", value="", placeholder="+1-555-123-4567"
)
street = st.text_input(
    "Street Address", value="", placeholder="123 Main St"
)
city = st.text_input(
    "City", value="", placeholder="Anytown"
)
region = st.text_input(
    "Region/State", value="", placeholder="CA"
)
postal = st.text_input(
    "Postal Code", value="", placeholder="12345"
)
country = st.text_input(
    "Country Code (e.g. US)", value="", placeholder="US"
)

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

# Hidden Offer Catalog Name
catalog_name = "Our Services"

# Services input (name, description)
services_text = st.text_area(
    "Services (one per line, format: name, description)",
    placeholder="Service One, Brief description of service one.\nService Two, Brief description of service two."
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
    components.html(f"""
    <button onclick="navigator.clipboard.writeText(`{json_ld}`)">Copy JSON-LD</button>
    <pre style="background:#f0f0f0;padding:10px;border-radius:5px;overflow:auto;">{json_ld}</pre>
    """, height=400)

    st.markdown("""
**How to use:**
1. Click the 'Copy JSON-LD' button above to copy the full JSON-LD.
2. Paste it into a `<script type=\"application/ld+json\">` tag on your page.
3. Verify with Google's Rich Results Test.
""")
