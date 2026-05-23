"""
Initialize healthcare knowledge graph data in Neo4j.
Ontology inspired by neo4j-labs/create-context-graph healthcare domain.
"""

import os
from dotenv import load_dotenv
from neo4j_utils import Neo4jConnector

load_dotenv()

DOMAIN = "healthcare"


def upsert_node(connector: Neo4jConnector, label: str, props: dict) -> None:
    cypher = f"""
    MERGE (n:{label} {{name: $name}})
    SET n += $props
    """
    connector.execute(cypher, {"name": props["name"], "props": {**props, "domain": DOMAIN}})


def upsert_relationship(
    connector: Neo4jConnector,
    source: str,
    target: str,
    rel_type: str,
    description: str = "",
) -> None:
    cypher = f"""
    MATCH (a {{name: $source}})
    MATCH (b {{name: $target}})
    MERGE (a)-[r:{rel_type}]->(b)
    SET r.description = $description, r.domain = $domain
    """
    connector.execute(
        cypher,
        {"source": source, "target": target, "description": description, "domain": DOMAIN},
    )


def create_healthcare_nodes(connector: Neo4jConnector) -> None:
    patients = [
        {
            "name": "Maria Gonzalez",
            "description": "58-year-old female with Type 2 diabetes and hypertension",
            "age": 58,
            "gender": "female",
            "mrn": "MRN-1001",
        },
        {
            "name": "James Wilson",
            "description": "72-year-old male with congestive heart failure",
            "age": 72,
            "gender": "male",
            "mrn": "MRN-1002",
        },
        {
            "name": "Sarah Chen",
            "description": "34-year-old female, postpartum follow-up",
            "age": 34,
            "gender": "female",
            "mrn": "MRN-1003",
        },
        {
            "name": "Robert Kim",
            "description": "45-year-old male with asthma and seasonal allergies",
            "age": 45,
            "gender": "male",
            "mrn": "MRN-1004",
        },
        {
            "name": "Elena Patel",
            "description": "67-year-old female recovering from hip replacement",
            "age": 67,
            "gender": "female",
            "mrn": "MRN-1005",
        },
    ]

    providers = [
        {
            "name": "Dr. Amanda Foster",
            "description": "Internal medicine physician, diabetes specialist",
            "specialty": "Internal Medicine",
            "npi": "NPI-2001",
        },
        {
            "name": "Dr. Michael Torres",
            "description": "Cardiologist specializing in heart failure",
            "specialty": "Cardiology",
            "npi": "NPI-2002",
        },
        {
            "name": "Dr. Lisa Nguyen",
            "description": "Obstetrician managing postpartum care",
            "specialty": "Obstetrics",
            "npi": "NPI-2003",
        },
        {
            "name": "Dr. David Brooks",
            "description": "Orthopedic surgeon, joint replacement",
            "specialty": "Orthopedics",
            "npi": "NPI-2004",
        },
    ]

    hospitals = [
        {
            "name": "Riverside General Hospital",
            "description": "Regional acute care hospital with cardiology and orthopedics units",
            "city": "Austin",
            "beds": 420,
        },
        {
            "name": "Northside Women's Health Center",
            "description": "Outpatient women's health and maternity clinic",
            "city": "Austin",
            "beds": 0,
        },
    ]

    diagnoses = [
        {
            "name": "Type 2 Diabetes Mellitus",
            "description": "Chronic metabolic disorder with insulin resistance",
            "icd10": "E11.9",
        },
        {
            "name": "Essential Hypertension",
            "description": "Primary high blood pressure without known secondary cause",
            "icd10": "I10",
        },
        {
            "name": "Congestive Heart Failure",
            "description": "Heart unable to pump blood effectively",
            "icd10": "I50.9",
        },
        {
            "name": "Postpartum Depression",
            "description": "Depressive episode following childbirth",
            "icd10": "F53.0",
        },
        {
            "name": "Persistent Asthma",
            "description": "Chronic inflammatory airway disease",
            "icd10": "J45.909",
        },
        {
            "name": "Osteoarthritis of Hip",
            "description": "Degenerative joint disease requiring surgical intervention",
            "icd10": "M16.11",
        },
    ]

    treatments = [
        {
            "name": "Metformin 500mg",
            "description": "First-line oral antidiabetic medication",
            "type": "medication",
        },
        {
            "name": "Lisinopril 10mg",
            "description": "ACE inhibitor for blood pressure control",
            "type": "medication",
        },
        {
            "name": "Furosemide 40mg",
            "description": "Loop diuretic for fluid overload in heart failure",
            "type": "medication",
        },
        {
            "name": "Sertraline 50mg",
            "description": "SSRI antidepressant for postpartum depression",
            "type": "medication",
        },
        {
            "name": "Albuterol Inhaler",
            "description": "Short-acting bronchodilator for asthma rescue",
            "type": "medication",
        },
        {
            "name": "Total Hip Arthroplasty",
            "description": "Surgical replacement of hip joint",
            "type": "procedure",
        },
        {
            "name": "Physical Therapy Program",
            "description": "12-week post-surgical rehabilitation plan",
            "type": "therapy",
        },
    ]

    lab_results = [
        {
            "name": "HbA1c 8.2%",
            "description": "Elevated glycated hemoglobin indicating poor glucose control",
            "test_code": "4548-4",
        },
        {
            "name": "BNP 980 pg/mL",
            "description": "Elevated B-type natriuretic peptide suggesting heart failure",
            "test_code": "30934-4",
        },
        {
            "name": "Peak Flow 320 L/min",
            "description": "Reduced peak expiratory flow consistent with asthma exacerbation",
            "test_code": "33452-4",
        },
    ]

    for patient in patients:
        upsert_node(connector, "Patient", patient)
        print(f"✓ Patient: {patient['name']}")

    for provider in providers:
        upsert_node(connector, "Provider", provider)
        print(f"✓ Provider: {provider['name']}")

    for hospital in hospitals:
        upsert_node(connector, "Hospital", hospital)
        print(f"✓ Hospital: {hospital['name']}")

    for diagnosis in diagnoses:
        upsert_node(connector, "Diagnosis", diagnosis)
        print(f"✓ Diagnosis: {diagnosis['name']}")

    for treatment in treatments:
        upsert_node(connector, "Treatment", treatment)
        print(f"✓ Treatment: {treatment['name']}")

    for lab in lab_results:
        upsert_node(connector, "LabResult", lab)
        print(f"✓ LabResult: {lab['name']}")


def create_healthcare_relationships(connector: Neo4jConnector) -> None:
    relationships = [
        ("Maria Gonzalez", "Type 2 Diabetes Mellitus", "HAS_DIAGNOSIS", "Diagnosed 3 years ago"),
        ("Maria Gonzalez", "Essential Hypertension", "HAS_DIAGNOSIS", "Comorbid condition"),
        ("Maria Gonzalez", "Metformin 500mg", "PRESCRIBED", "Twice daily with meals"),
        ("Maria Gonzalez", "Lisinopril 10mg", "PRESCRIBED", "Once daily"),
        ("Maria Gonzalez", "HbA1c 8.2%", "HAS_LAB_RESULT", "Latest quarterly panel"),
        ("Maria Gonzalez", "Dr. Amanda Foster", "TREATED_BY", "Primary care physician"),
        ("James Wilson", "Congestive Heart Failure", "HAS_DIAGNOSIS", "NYHA Class II"),
        ("James Wilson", "Furosemide 40mg", "PRESCRIBED", "Daily diuretic"),
        ("James Wilson", "BNP 980 pg/mL", "HAS_LAB_RESULT", "Admission labs"),
        ("James Wilson", "Dr. Michael Torres", "TREATED_BY", "Cardiology follow-up"),
        ("James Wilson", "Riverside General Hospital", "ADMITTED_TO", "Recent CHF exacerbation"),
        ("Sarah Chen", "Postpartum Depression", "HAS_DIAGNOSIS", "Screened positive at 6-week visit"),
        ("Sarah Chen", "Sertraline 50mg", "PRESCRIBED", "Started at 25mg, titrated up"),
        ("Sarah Chen", "Dr. Lisa Nguyen", "TREATED_BY", "Obstetric follow-up"),
        ("Sarah Chen", "Northside Women's Health Center", "ADMITTED_TO", "Outpatient clinic visits"),
        ("Robert Kim", "Persistent Asthma", "HAS_DIAGNOSIS", "Moderate persistent asthma"),
        ("Robert Kim", "Albuterol Inhaler", "PRESCRIBED", "Rescue inhaler as needed"),
        ("Robert Kim", "Peak Flow 320 L/min", "HAS_LAB_RESULT", "Pulmonary function check"),
        ("Robert Kim", "Dr. Amanda Foster", "TREATED_BY", "Primary care management"),
        ("Elena Patel", "Osteoarthritis of Hip", "HAS_DIAGNOSIS", "Severe joint degeneration"),
        ("Elena Patel", "Total Hip Arthroplasty", "UNDERWENT", "Successful surgery last month"),
        ("Elena Patel", "Physical Therapy Program", "PRESCRIBED", "Post-op rehab"),
        ("Elena Patel", "Dr. David Brooks", "TREATED_BY", "Orthopedic surgeon"),
        ("Elena Patel", "Riverside General Hospital", "ADMITTED_TO", "Inpatient surgery"),
        ("Dr. Amanda Foster", "Riverside General Hospital", "WORKS_AT", "Internal medicine department"),
        ("Dr. Michael Torres", "Riverside General Hospital", "WORKS_AT", "Cardiology department"),
        ("Dr. Lisa Nguyen", "Northside Women's Health Center", "WORKS_AT", "Lead obstetrician"),
        ("Dr. David Brooks", "Riverside General Hospital", "WORKS_AT", "Orthopedics department"),
        ("Dr. Amanda Foster", "Maria Gonzalez", "TREATS", "Manages diabetes and hypertension"),
        ("Dr. Michael Torres", "James Wilson", "TREATS", "Heart failure management"),
        ("Dr. Lisa Nguyen", "Sarah Chen", "TREATS", "Postpartum mental health"),
        ("Dr. David Brooks", "Elena Patel", "TREATS", "Hip replacement care"),
    ]

    for source, target, rel_type, description in relationships:
        upsert_relationship(connector, source, target, rel_type, description)
        print(f"✓ {source} -[{rel_type}]-> {target}")


def main() -> None:
    print("🏥 Initializing Healthcare Knowledge Graph\n")

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    connector = Neo4jConnector(uri, user, password, database)
    print(f"✓ Connected to Neo4j at {uri}\n")

    print("👤 Creating healthcare nodes...")
    create_healthcare_nodes(connector)

    print("\n🔗 Creating healthcare relationships...")
    create_healthcare_relationships(connector)

    stats = connector.get_graph_stats()
    print("\n📊 Graph statistics:")
    print(f"  Total nodes: {stats.get('nodes', 0)}")
    print(f"  Total relationships: {stats.get('relationships', 0)}")
    print(f"  Label types: {stats.get('label_count', 0)}")
    print("\n✓ Healthcare knowledge graph loaded successfully!")

    connector.close()


if __name__ == "__main__":
    main()
