import streamlit as st
from google.auth import default
from google.auth.transport.requests import AuthorizedSession
from google.cloud import dataplex_v1

catalog_client = dataplex_v1.CatalogServiceClient()

@st.cache_data(ttl=600)
def search_glossary_terms_rest(project_id, location, glossary_id, query_text):
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    session = AuthorizedSession(credentials)

    base_url = (
        f"https://dataplex.googleapis.com/v1/projects/{project_id}"
        f"/locations/{location}/glossaries/{glossary_id}/terms"
    )

    terms = []
    page_token = None

    while True:
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token

        response = session.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        for term in data.get("terms", []):
            display_name = term.get("displayName", "")
            if query_text.lower() in display_name.lower():
                terms.append({
                    "name": display_name,
                    "description": term.get("description", ""),
                    "term_name": term.get("name"),
                    "labels": term.get("labels", {}),
                })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return terms

@st.cache_data(ttl=600)
def get_glossary_term_details(term_name: str):
    credentials, _ = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)

    url = f"https://dataplex.googleapis.com/v1/{term_name}"
    response = session.get(url)
    response.raise_for_status()

    return response.json()

@st.cache_data(ttl=600)


def get_term_aspects_from_dataplex(entry_name: str):
    """
    Obtiene los aspectos (Metadata Types) vinculados a la entrada del catálogo.
    """
    try:
        # Usamos la vista FULL para asegurarnos de traer todos los aspectos vinculados
        entry = catalog_client.get_entry(
            name=entry_name, 
            view=dataplex_v1.EntryView.FULL 
        )
        
        # El objeto entry.aspects es un mapa (dict-like) 
        # donde la llave es el ID del Aspect Type
        return entry.aspects or {}
    except Exception as e:
        st.error(f"Error al obtener aspectos: {e}")
        return {}