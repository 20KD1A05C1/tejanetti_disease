import os
from neo4j import GraphDatabase

SAMPLE_DISEASES = [
    {
        "name": "Influenza",
        "symptoms": ["fever", "cough", "sore throat", "body ache"],
        "medicines": ["oseltamivir", "acetaminophen", "rest"]
    },
    {
        "name": "Common Cold",
        "symptoms": ["cough", "runny nose", "sore throat", "sneezing"],
        "medicines": ["decongestant", "ibuprofen", "rest"]
    },
    {
        "name": "Migraine",
        "symptoms": ["headache", "nausea", "sensitivity to light"],
        "medicines": ["sumatriptan", "naproxen"]
    },
    {
        "name": "Allergic Rhinitis",
        "symptoms": ["sneezing", "runny nose", "itchy eyes"],
        "medicines": ["loratadine", "cetirizine"]
    },
    {
        "name": "Gastroenteritis",
        "symptoms": ["diarrhea", "vomiting", "stomach pain", "fever"],
        "medicines": ["oral rehydration", "ondansetron"]
    }
]


def get_neo4j_credentials():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")

    if not uri:
        uri = input("Enter Neo4j URI (e.g. bolt://localhost:7687): ").strip()
    if not user:
        user = input("Enter Neo4j username: ").strip()
    if not password:
        password = input("Enter Neo4j password: ").strip()

    return uri, user, password


def load_sample_data(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        session.run("MATCH (n:SampleData) DETACH DELETE n")

        for disease in SAMPLE_DISEASES:
            session.run(
                """
                MERGE (d:Disease:SampleData {name: $disease_name})
                SET d.medicines = $medicines
                WITH d
                UNWIND $symptoms AS symptom_name
                MERGE (s:Symptom:SampleData {name: symptom_name})
                MERGE (d)-[:HAS_SYMPTOM]->(s)
                """,
                disease_name=disease["name"],
                medicines=disease["medicines"],
                symptoms=disease["symptoms"],
            )

    driver.close()


if __name__ == "__main__":
    print("Loading sample disease dataset into Neo4j...")
    uri, user, password = get_neo4j_credentials()
    load_sample_data(uri, user, password)
    print("Sample data loaded successfully.")
    print("Now run: streamlit run streamlit_app.py")
