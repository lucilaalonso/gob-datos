import streamlit as st
from google.cloud import bigquery

client = bigquery.Client()


def get_table_schema(project_id, dataset_id, table_id):
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = client.get_table(table_ref)

    return [
        {
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode
        }
        for field in table.schema
    ]


def get_dataset_schema(project, dataset):
    tables = list(client.list_tables(f"{project}.{dataset}"))

    if not tables:
        return []

    table_id = tables[0].table_id
    return get_table_schema(project, dataset, table_id)


def get_data_quality(project, dataset):
    query = f"""
    SELECT
        table_name,
        dimension,
        score
    FROM `{project}.data_quality.results`
    WHERE dataset_id = '{dataset}'
    """

    return client.query(query).to_dataframe()

def get_dataset_info(project, dataset):
    from google.cloud import bigquery
    client = bigquery.Client()

    dataset_ref = client.get_dataset(f"{project}.{dataset}")

    return {
        "name": dataset,
        "description": dataset_ref.description,
        "location": dataset_ref.location
    }

def list_tables(project, dataset):
    from google.cloud import bigquery
    client = bigquery.Client()

    tables = client.list_tables(f"{project}.{dataset}")

    return [t.table_id for t in tables]

@st.cache_data(ttl=300)
def list_tables(project, dataset):
    tables = client.list_tables(f"{project}.{dataset}")
    return [t.table_id for t in tables]

@st.cache_data(ttl=300)
def get_table_schema(project_id, dataset_id, table_id):
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = client.get_table(table_ref)

    return [
        {
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode
        }
        for field in table.schema
    ]
