import requests
import streamlit as st
from neo4j_database import Neo4jDatabase  # Your Neo4j integration

API_URL = st.secrets.get("MEDICAL_API_URL", "https://example-medical-api.com/symptom")

# Function to get disease info from Neo4j
def get_disease_info(symptom, db):
    query = """
    MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
    WHERE toLower(s.name) = toLower($symptom)
    RETURN d.name AS disease, d.medicines AS medicines;
    """
    return db.query(query, {"symptom": symptom})

# Function to format medicine output cleanly
def format_medicines(medicines):
    if medicines is None:
        return "No medicines listed"
    if isinstance(medicines, list):
        return ", ".join(str(m) for m in medicines)
    return str(medicines)

# Function to get disease info from an external API
def get_disease_from_api(symptom):
    api_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.get(f"{API_URL}?symptom={symptom.lower()}", headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None
    return None

# Streamlit app layout
st.title("Disease Symptom Finder")

# User input for symptom
symptom_input = st.text_input("Enter a symptom:")

if st.button("Search"):
    if not symptom_input:
        st.warning("Please enter a symptom.")
    else:
        if not st.secrets.get("NEO4J_URI") or not st.secrets.get("NEO4J_USER") or not st.secrets.get("NEO4J_PASSWORD"):
            st.error("Neo4j credentials are not configured in Streamlit secrets.")
        else:
            try:
                db = Neo4jDatabase(
                    st.secrets["NEO4J_URI"],
                    st.secrets["NEO4J_USER"],
                    st.secrets["NEO4J_PASSWORD"],
                )
                results = get_disease_info(symptom_input, db)
            except Exception as exc:
                st.error(f"Failed to connect to Neo4j: {exc}")
                results = []
            else:
                db.close()

            if results:
                st.success("Found disease(s) in the database:")
                for item in results:
                    st.write(f"Disease: {item.get('disease', 'Unknown')}")
                    st.write(f"Medicines: {format_medicines(item.get('medicines'))}")
            else:
                st.info("No matching disease found in the database.")
                api_results = get_disease_from_api(symptom_input)
                if api_results:
                    st.success("API Results:")
                    for item in api_results:
                        st.write(f"Disease: {item.get('disease', 'Unknown')}")
                        st.write(f"Medicines: {format_medicines(item.get('medicines'))}")
                else:
                    st.warning("No disease found for the given symptom and external API is not configured or returned no results.")
