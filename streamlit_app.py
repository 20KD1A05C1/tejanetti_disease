import streamlit as st
from neo4j import GraphDatabase
import csv
from io import StringIO

# Neo4j connection setup
class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def create_graph(self, data):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")  # Clear existing data
            for row in data:
                symptom, disease, medicine = row
                session.run("""
                    MERGE (s:Symptom {name: $symptom})
                    MERGE (d:Disease {name: $disease})
                    MERGE (m:Medicine {name: $medicine})
                    MERGE (s)-[:INDICATES]->(d)
                    MERGE (d)-[:TREATED_BY]->(m)
                """, symptom=symptom, disease=disease, medicine=medicine)

    def get_disease_info(self, symptom):
        query = """
        MATCH (s:Symptom {name: $symptom})-[:INDICATES]->(d:Disease)
        OPTIONAL MATCH (d)-[:TREATED_BY]->(m:Medicine)
        RETURN d.name AS disease, COLLECT(m.name) AS medicines
        """
        with self.driver.session() as session:
            result = session.run(query, symptom=symptom)
            return [{"disease": record["disease"], "medicines": record["medicines"]} for record in result]

# Streamlit app layout
st.title("Disease Ontology: Symptom to Disease Finder")

# Taking Neo4j credentials from Streamlit secrets
uri = st.secrets["neo4j"]["uri"]
username = st.secrets["neo4j"]["username"]
password = st.secrets["neo4j"]["password"]

# Initialize Neo4j connection
db = Neo4jDatabase(uri, username, password)

# CSV data (replace this with your actual CSV data)
csv_data = """Symptom,Disease,Medicine
"Fever, cough, fatigue",Influenza,Oseltamivir
"Chest pain, shortness of breath",Angina,Nitroglycerin
"Frequent urination, excessive thirst",Type 2 Diabetes,Metformin
"Joint pain, swelling, stiffness",Rheumatoid Arthritis,Methotrexate
"Headache, sensitivity to light and sound",Migraine,Sumatriptan
"Abdominal pain, diarrhea, weight loss",Crohn's Disease,Mesalamine
"Sneezing, runny nose, itchy eyes",Allergic Rhinitis,Cetirizine
"Mood swings, depressed mood, loss of interest",Bipolar Disorder,Lithium
"Memory loss, confusion, personality changes",Alzheimer's Disease,Donepezil
"Shortness of breath, wheezing, chest tightness",Asthma,Albuterol
"Heartburn, regurgitation, difficulty swallowing",Gastroesophageal Reflux Disease (GERD),Omeprazole
"Fatigue, weight gain, hair loss",Hypothyroidism,Levothyroxine
"Red, itchy, scaly skin",Psoriasis,Adalimumab
"Painful, frequent urination",Urinary Tract Infection,Ciprofloxacin
High blood pressure,Hypertension,Lisinopril
"Excessive sweating, rapid heartbeat, weight loss",Hyperthyroidism,Methimazole
"Nausea, vomiting, loss of appetite",Gastroenteritis,Ondansetron
"Anxiety, restlessness, insomnia",Generalized Anxiety Disorder,Sertraline
"Tremors, stiffness, slow movement",Parkinson's Disease,Levodopa
"Sore throat, difficulty swallowing, fever",Strep Throat,Amoxicillin"""

# Parse CSV data
csv_file = StringIO(csv_data)
csv_reader = csv.reader(csv_file)
next(csv_reader)  # Skip header
data = list(csv_reader)

# Create graph in Neo4j
db.create_graph(data)

# User input for symptoms
symptom_input = st.text_input("Enter a symptom:")

if st.button("Search"):
    if symptom_input:
        # Query the Neo4j database
        results = db.get_disease_info(symptom_input)
        
        if results:
            st.write(f"Diseases related to '{symptom_input}':")
            for item in results:
                st.write(f"Disease: {item['disease']}")
                st.write(f"Medicines: {', '.join(item['medicines']) if item['medicines'] else 'No medicines available'}")
        else:
            st.write("No disease found for the given symptom.")
    else:
        st.write("Please enter a symptom.")

# Close the Neo4j connection
db.close()
