import streamlit as st
import json
import base64
import streamlit.components.v1 as components
from datetime import time

st.set_page_config(page_title="Local Business Schema Generator", layout="centered")
st.title("Local Business Schema Generator")
st.caption("Local Business Schema Generator Testing Beta | Built by Miguel Gracia")

# --- Helper callbacks for dynamic services ---
def add_service():
    st.session_state.services.append({"name": "", "desc": "", "sameAsUrl": ""}) # Added sameAsUrl

def delete_service(idx):
    st.session_state.services.pop(idx)

# --- Build JSON-LD ---
def build_jsonld():
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
    }
    # Basic Info
    if st.session_state.name: schema["name"] = st.session_state.name
    if st.session_state.url: schema["url"] = st.session_state.url
    if st.session_state.logo: schema["logo"] = st.session_state.logo
    if st.session_state.description: schema["description"] = st.session_state.description
    if st.session_state.telephone: schema["telephone"] = st.session_state.telephone

    # Address
    address = {}
    if st.session_state.street: address["streetAddress"] = st.session_state.street
    if st.session_state.city: address["addressLocality"] = st.session_state.city
    if st.session_state.region: address["addressRegion"] = st.session_state.region
    if st.session_state.postal: address["postalCode"] = st.session_state.postal
    if st.session_state.country: address["addressCountry"] = st.session_state.country
    if address:
        address["@type"] = "PostalAddress"
        schema["address"] = address

    # sameAs (Socials + GBP URL)
    same_as_urls = []
    socials = [u.strip() for u in st.session_state.socials.splitlines() if u.strip()]
    if socials:
        same_as_urls.extend(socials)

    gbp_url = st.session_state.get("gbp_url", "").strip()
    if gbp_url:
        same_as_urls.append(gbp_url)

    if same_as_urls:
        schema["sameAs"] = list(set(same_as_urls)) # Remove potential duplicates

    # areaServed
    areas = [a.strip() for a in st.session_state.areas.splitlines() if a.strip()]
    if areas:
        schema["areaServed"] = areas

    # openingHoursSpecification
    hours_spec = []
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        if st.session_state.get(f"chk_{day}", False):
            opens_time = st.session_state[f"open_{day}"]
            closes_time = st.session_state[f"close_{day}"]
            # Ensure times are not None before formatting
            if opens_time and closes_time:
                opens = opens_time.strftime("%H:%M")
                closes = closes_time.strftime("%H:%M")
                hours_spec.append({
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": f"https://schema.org/{day}", # More specific dayOfWeek
                    "opens": opens,
                    "closes": closes,
                })
    if hours_spec:
        schema["openingHoursSpecification"] = hours_spec

    # Services (hasOfferCatalog)
    offers = []
    for svc in st.session_state.services:
        name = svc.get("name", "").strip()
        desc = svc.get("desc", "").strip()
        same_as_url = svc.get("sameAsUrl", "").strip() # Get sameAsUrl
        if name: # Only add service if name is present
            service_item = {
                "@type": "Service",
                "name": name
            }
            if desc: # Add description only if provided
                service_item["description"] = desc
            if same_as_url: # Add sameAs if provided
                service_item["sameAs"] = same_as_url

            offers.append({
                "@type": "Offer",
                "itemOffered": service_item
            })
    if offers:
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Our Services", # Or a more specific catalog name
            "itemListElement": offers
        }

    raw_json = json.dumps(schema, indent=2)
    return f"""<script type=\"application/ld+json\">\n{raw_json}\n</script>"""

# --- Initialize UI State ---
if "services" not in st.session_state:
    st.session_state.services = [{"name": "", "desc": "", "sameAsUrl": ""}] # Initialize with sameAsUrl
if "socials" not in st.session_state:
    st.session_state.socials = ""
if "areas" not in st.session_state:
    st.session_state.areas = ""
if "gbp_url" not in st.session_state: # Initialize gbp_url
    st.session_state.gbp_url = ""


# --- UI Inputs ---
st.markdown("## 🏢 Business Information")
st.text_input("Business Name*", key="name", placeholder="e.g., Acme Corp")
st.text_input("Business Website URL*", key="url", placeholder="https://example.com")
st.text_input("Logo URL", key="logo", placeholder="https://example.com/logo.png")
st.text_area("Business Description", key="description", placeholder="e.g., Acme Corp provides top-notch solutions for all your needs.")
st.text_input("Phone Number", key="telephone", placeholder="+1-555-123-4567")

st.markdown("---")
st.markdown("## 📍 Business Location")
st.text_input("Street Address", key="street", placeholder="123 Main St")
st.text_input("City", key="city", placeholder="Anytown")
st.text_input("Region/State Abbreviation", key="region", placeholder="CA")
st.text_input("Postal Code", key="postal", placeholder="90210")
st.text_input("Country Code (2-letter)", key="country", placeholder="US")

st.markdown("---")
st.markdown("## 🔗 Online Presence & Service Areas")
st.text_input("Google Business Profile URL", key="gbp_url", placeholder="https://maps.google.com/?cid=1234567890123456789")
st.text_area("Other Social Profiles (one URL per line)", key="socials", height=100, placeholder="https://facebook.com/yourpage\nhttps://twitter.com/yourhandle\nhttps://linkedin.com/company/yourcompany")
st.text_area(
    "Areas Served (one per line, e.g., City, State or Postal Code)",
    key="areas",
    height=100,
    placeholder="e.g.,\nRoanoke, VA\nSalem, VA\n24018"
)

st.markdown("---")
# --- Dynamic Services Block ---
st.markdown("## 🛠️ Services Offered")
for i, svc in enumerate(st.session_state.services):
    st.markdown(f"#### Service #{i+1}")
    c1, c2, c3 = st.columns([4, 6, 1])
    with c1:
        name = st.text_input(
            f"Service Name", key=f"svc_name_{i}", value=svc["name"], label_visibility="collapsed", placeholder="Service Name"
        )
        st.session_state.services[i]["name"] = name
        same_as_url = st.text_input( # New input for sameAsUrl
            f"Service URL (sameAs)", key=f"svc_sameAsUrl_{i}", value=svc.get("sameAsUrl", ""), placeholder="URL for this specific service"
        )
        st.session_state.services[i]["sameAsUrl"] = same_as_url
    with c2:
        desc = st.text_area(
            f"Service Description", key=f"svc_desc_{i}", value=svc["desc"], height=75, label_visibility="collapsed", placeholder="Brief description of the service"
        )
        st.session_state.services[i]["desc"] = desc
    with c3:
        st.button(
            "🗑️",
            key=f"del_svc_{i}",
            on_click=delete_service,
            args=(i,),
            help="Delete this service"
        )
st.button("➕ Add another service", on_click=add_service, type="primary")

st.markdown("---")
# --- Opening Hours ---
st.markdown("## ⏰ Opening Hours")
days_of_week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
for day in days_of_week:
    cols = st.columns([0.3, 0.7, 0.7]) # Adjusted column ratios
    with cols[0]:
        st.checkbox(day[:3], key=f"chk_{day}") # Shorter day labels
    if st.session_state.get(f"chk_{day}"):
        with cols[1]:
            st.time_input(f"Opens", value=st.session_state.get(f"open_{day}", time(9,0)), key=f"open_{day}", label_visibility="collapsed")
        with cols[2]:
            st.time_input(f"Closes", value=st.session_state.get(f"close_{day}", time(17,0)), key=f"close_{day}", label_visibility="collapsed")
    else:
        # Initialize time inputs even if checkbox is off to prevent errors if user unchecks
        if f"open_{day}" not in st.session_state:
            st.session_state[f"open_{day}"] = time(9,0)
        if f"close_{day}" not in st.session_state:
            st.session_state[f"close_{day}"] = time(17,0)


st.markdown("---")
# --- Generate & Display ---
if st.button("🚀 Generate JSON-LD Schema", type="primary", use_container_width=True):
    # Basic validation for required fields
    if not st.session_state.name or not st.session_state.url:
        st.error("❗ Business Name and Business Website URL are required.")
    else:
        script_block = build_jsonld()
        st.subheader("Generated JSON-LD Schema ✨")

        # Provide a direct text area for copying as well
        st.text_area("Copyable Schema Code:", script_block, height=250)

        b64 = base64.b64encode(script_block.encode("utf-8")).decode("utf-8")
        html_button_code = f'''
<button id="copy-btn-schema" style="padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #007bff; color: white; border: none; cursor: pointer;">Copy JSON-LD to Clipboard</button>
<div id="copy-feedback" style="margin-top: 5px; font-size: 0.9em;"></div>
<script>
    const rawSchema = atob("{b64}");
    const copyBtnSchema = document.getElementById("copy-btn-schema");
    const feedbackDiv = document.getElementById("copy-feedback");

    if (copyBtnSchema) {{
        copyBtnSchema.addEventListener("click", () => {{
            navigator.clipboard.writeText(rawSchema).then(() => {{
                feedbackDiv.textContent = "Copied to clipboard!";
                feedbackDiv.style.color = "green";
                copyBtnSchema.textContent = "Copied!";
                setTimeout(() => {{
                    copyBtnSchema.textContent = "Copy JSON-LD to Clipboard";
                    feedbackDiv.textContent = "";
                }}, 2000);
            }}, (err) => {{
                feedbackDiv.textContent = "Failed to copy.";
                feedbackDiv.style.color = "red";
                console.error('Failed to copy: ', err);
            }});
        }});
    }}
</script>
'''
        components.html(html_button_code, height=70) # Reduced height as preview is removed

        st.markdown("""
        ---
        **📋 How to Use This Schema:**
        1.  Click the **Copy JSON-LD to Clipboard** button (or manually copy from the text area above).
        2.  Paste the copied `<script>` tag into the `<head>` or `<body>` section of your website's HTML.
        3.  **Important:** Test your implementation using [Google's Rich Results Test](https://search.google.com/test/rich-results) to ensure it's valid and can be processed by Google.
        4.  Consider also validating with the [Schema Markup Validator](https://validator.schema.org/).
        """)
st.markdown("---")
st.caption("Local Business Schema Generator | Built by Miguel Gracia")