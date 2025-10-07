import json
from pathlib import Path

import streamlit as st
from PIL import Image

# ---------- Paths
REPO_ROOT = Path(__file__).parent
DATA_PATH = REPO_ROOT / "V1.json"
IMAGES_DIR = REPO_ROOT / "images"

st.set_page_config(page_title="TCGP Playground", layout="wide")
st.title("Pokémon TCG Pocket – Card Browser")

# ---------- Load data
@st.cache_data
def load_cards():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)  # list[dict]
    return cards

cards = load_cards()
if not cards:
    st.warning("No cards found in V1.json")
    st.stop()

# ---------- Sidebar filters
all_types   = sorted({c.get("type","") for c in cards if c.get("type")})
all_packs   = sorted({c.get("pack","") for c in cards if c.get("pack")})
all_rarity  = sorted({c.get("rarity","") for c in cards if c.get("rarity")})

name_query  = st.sidebar.text_input("Search name contains")
sel_types   = st.sidebar.multiselect("Type", all_types)
sel_packs   = st.sidebar.multiselect("Pack", all_packs)
sel_rarity  = st.sidebar.multiselect("Rarity", all_rarity)
only_ex     = st.sidebar.checkbox("EX only")
only_full   = st.sidebar.checkbox("Full Art only")

# ---------- Filtering
def matches(card):
    if name_query and name_query.lower() not in card.get("name","").lower():
        return False
    if sel_types and card.get("type") not in sel_types:
        return False
    if sel_packs and card.get("pack") not in sel_packs:
        return False
    if sel_rarity and card.get("rarity") not in sel_rarity:
        return False
    if only_ex and card.get("ex","No") != "Yes":
        return False
    if only_full and card.get("fullart","No") != "Yes":
        return False
    return True

filtered = [c for c in cards if matches(c)]

st.caption(f"Showing {len(filtered)} / {len(cards)} cards")

# ---------- Card grid
COLS = 5
rows = (len(filtered) + COLS - 1) // COLS

def load_local_image(card_id: str):
    """Prefer local PNG: images/<id>.png (e.g., images/a1-001.png)."""
    png_path = IMAGES_DIR / f"{card_id}.png"
    if png_path.exists():
        return Image.open(png_path)
    return None

for r in range(rows):
    cols = st.columns(COLS)
    for ci in range(COLS):
        idx = r * COLS + ci
        if idx >= len(filtered):
            break
        c = filtered[idx]
        with cols[ci]:
            img = load_local_image(c["id"])
            if img is not None:
                st.image(img, use_container_width=True)
            else:
                # Fallback to remote URL in JSON if local image missing
                url = c.get("image")
                if url:
                    st.image(url, use_container_width=True)
                else:
                    st.write("No image available")

            st.markdown(f"**{c.get('name','Unknown')}**")
            meta = []
            if c.get("type"):   meta.append(c["type"])
            if c.get("rarity"): meta.append(f"Rarity: {c['rarity']}")
            if c.get("pack"):   meta.append(f"Pack: {c['pack']}")
            if c.get("health"): meta.append(f"HP: {c['health']}")
            if c.get("artist"): meta.append(f"Artist: {c['artist']}")
            if c.get("ex") == "Yes":      meta.append("EX")
            if c.get("fullart") == "Yes": meta.append("Full Art")
            st.caption(" · ".join(meta))
