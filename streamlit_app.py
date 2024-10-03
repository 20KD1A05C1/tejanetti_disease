import requests
import streamlit as st
from neo4j_database import Neo4jDatabase  # Your Neo4j integration

API_URL = "https://example-medical-api.com/symptom"

# Function to get disease info from Neo4j
def get_disease_info(symptom, db):
    query = """
    MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
    WHERE toLower(s.name) = toLower($symptom)
    RETURN d.name AS disease, d.medicines AS medicines;
    """
    return db.query(query, {"symptom": symptom})

# Function to get disease info from an external API
def get_disease_from_api(symptom):
    headers = {
        'Authorization': f'Bearer {st.secrets["HUGGINGFACE_API_KEY"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{API_URL}?symptom={symptom.lower()}", headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON
    else:
        return None

# Streamlit app layout
st.title("Disease Symptom Finder")

# User input for symptom
symptom_input = st.text_input("Enter a symptom:")

if st.button("Search"):
    if symptom_input:
        # Connect to the database
        db = Neo4jDatabase(st.secrets["NEO4J_URI"], st.secrets["NEO4J_USER"], st.secrets["NEO4J_PASSWORD"])
        
        # Query the graph database (case-insensitive)
        results = get_disease_info(symptom_input.lower(), db)
        
        # If no result from the database, query the API
        if not results:
            api_results = get_disease_from_api(symptom_input.lower())
            if api_results:
                st.write("API Results:")
                for item in api_results:
                    st.write(f"Disease: {item['disease']}")
                    st.write(f"Medicines: {', '.join(item['medicines'])}")
            else:
                st.write("No disease found for the given symptom.")
        else:
            for item in results:
                st.write(f"Disease: {item['disease']}")
                st.write(f"Medicines: {', '.join(item['medicines'])}")
        
        # Close the database connection
        db.close()
    else:
        st.write("Please enter a symptom.")
