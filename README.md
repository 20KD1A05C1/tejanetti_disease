# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Load the sample Neo4j dataset

   ```
   $ python create_sample_data.py
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Neo4j sample dataset

The sample dataset includes diseases such as `Influenza`, `Common Cold`, `Migraine`, `Allergic Rhinitis`, and `Gastroenteritis`, along with their symptoms and medicines.

### Secrets configuration

Create a `secrets.toml` file for Streamlit with:

```toml
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your-password"
HUGGINGFACE_API_KEY = "your-key"
MEDICAL_API_URL = "https://example-medical-api.com/symptom"
```

If you are not using the external API, you can omit `HUGGINGFACE_API_KEY` and `MEDICAL_API_URL`.
