import streamlit as st
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="Supabase To-Do Pro", page_icon="🚀")

conn = st.connection("supabase", type=SupabaseConnection)

# --- SPRACHLOGIK ---
sprache = st.sidebar.radio("Sprache", ("Deutsch", "English"))
texte = {
    "Deutsch": {
        "titel": "🚀 To-Do mit Kategorien",
        "label": "Aufgabe",
        "kat_label": "Kategorie",
        "btn": "Hinzufügen",
        "kategorien": ["Privat", "Arbeit", "Einkauf", "Wichtig"],
        "loeschen": "Löschen"
    },
    "English": {
        "titel": "🚀 To-Do with Categories",
        "label": "Task",
        "kat_label": "Category",
        "btn": "Add",
        "kategorien": ["Personal", "Work", "Shopping", "Important"],
        "loeschen": "Delete"
    }
}
t = texte[sprache]

st.title(t["titel"])

# --- FUNKTIONEN ---
def lade_todos():
    # Wir laden die Daten und sortieren sie
    response = conn.table("todos").select("*").order("created_at", desc=True).execute()
    return response.data

def fuege_hinzu(task, category):
    conn.table("todos").insert({"task": task, "category": category, "done": False}).execute()

def update_status(todo_id, status):
    conn.table("todos").update({"done": status}).eq("id", todo_id).execute()

def loesche_todo(todo_id):
    conn.table("todos").delete().eq("id", todo_id).execute()

# --- EINGABE-BEREICH ---
with st.form("add_form", clear_on_submit=True):
    col_t, col_k = st.columns([0.7, 0.3])
    neue_aufgabe = col_t.text_input(t["label"])
    kategorie = col_k.selectbox(t["kat_label"], t["kategorien"])
    
    if st.form_submit_button(t["btn"]) and neue_aufgabe:
        fuege_hinzu(neue_aufgabe, kategorie)
        st.rerun()

# --- ANZEIGE-LOGIK ---
alle_todos = lade_todos()
offene = [x for x in alle_todos if not x.get("done")]
erledigte = [x for x in alle_todos if x.get("done")]

def render_item(item):
    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
    
    # Checkbox
    check = col1.checkbox("", value=item["done"], key=f"c_{item['id']}")
    if check != item["done"]:
        update_status(item["id"], check)
        st.rerun()
    
    # Text und Kategorie-Tag
    kat_tag = f"`{item.get('category', 'Privat')}`"
    col2.markdown(f"{item['task']} {kat_tag}")
    
    # Löschen
    if col3.button(t["loeschen"], key=f"d_{item['id']}"):
        loesche_todo(item["id"])
        st.rerun()

st.subheader("Offen")
for item in offene:
    render_item(item)

if erledigte:
    st.divider()
    st.subheader("Erledigt")
    for item in erledigte:
        render_item(item)
