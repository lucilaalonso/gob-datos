import streamlit as st
from config import (
    PROJECT_ID,
    LOCATION,
    GLOSSARY_ID,
    TABLE_LABEL_DESCRIPTIONS
)
from api.bigquery_client import (
    get_dataset_info,
    list_tables,
    get_table_schema
)
from api.dataplexcatalog_client import (
    search_glossary_terms_rest, 
    get_glossary_term_details,
    get_term_aspects_from_dataplex
)


def render_main():

    st.title("Portal de Datos")

    selected = st.session_state.get("selected")

    # =====================================================
    # 📊 SECCIÓN DATASET
    # =====================================================

    if not selected:
        st.info("Seleccioná un dataset")
    else:
        project = selected["project"]
        dataset = selected["dataset"]

        # INFO DATASET
        st.subheader(f"📦 Dataset: {dataset}")

        info = get_dataset_info(project, dataset)

        st.write("**Ubicación:**", info["location"])

        # TABLAS
        st.markdown("### 📋 Tablas")

        tables = list_tables(project, dataset)
        st.write(f"Total de tablas: {len(tables)}")

        if not tables:
            st.warning("No hay tablas en este dataset")
        else:
            selected_table = st.selectbox("Seleccionar tabla", tables)

            if selected_table:

                st.markdown("### 🧱 Esquema")

                # estado persistente
                if "schema" not in st.session_state:
                    st.session_state.schema = None

                # botón lazy loading
                if st.button("🔍 Ver esquema"):
                    with st.spinner("Cargando esquema..."):
                        st.session_state.schema = get_table_schema(
                            project,
                            dataset,
                            selected_table
                        )

                # mostrar resultado
                if st.session_state.schema:
                    st.dataframe(st.session_state.schema)


    # =====================================================
    # 📚 SECCIÓN GLOSARIO DE NEGOCIO (DATAPLEX)
    # =====================================================

    st.markdown("---")
    st.markdown("## 📚 Glosario de negocio")

    search_text = st.text_input("🔍 Buscar término")

    if search_text and len(search_text) > 2:
        with st.spinner("Buscando términos en el glosario..."):
            results = search_glossary_terms_rest(
                PROJECT_ID,
                LOCATION,
                GLOSSARY_ID,
                search_text
            )

        if not results:
            st.info("No se encontraron términos")
        else:
            names = [t["name"] for t in results]
            selected_term_name = st.selectbox("Resultados", names)

            term = next(t for t in results if t["name"] == selected_term_name)

            # Traigo el detalle del término Dataplex
            term_details = get_glossary_term_details(term["term_name"])

            # Extraigo el Entry de Data Catalog asociado
            catalog_entry_name = (
                term_details
                .get("catalogEntry", {})
                .get("name")
            )

            st.markdown(f"### 📖 {term['name']}")
            st.write(term["description"] or "Sin descripción")

            if term["labels"]:
                labels = term["labels"]

                st.markdown("### 🏷️ Uso del término en tablas")
                st.markdown(
                    "En las siguientes tablas del dominio aparece este término."
                )

                for key, value in labels.items():
                    if key.startswith("table_"):
                        table_name = TABLE_LABEL_DESCRIPTIONS.get(key, value)
                        st.markdown(f"• **{table_name}**")
                
                st.markdown("### 🧭 Clasificación del término")

                if "dominio" in labels:
                    st.markdown(f"**Dominio:** {labels['dominio']}")

                if "tipo" in labels:
                    st.markdown(f"**Tipo:** {labels['tipo']}")
           
            # =====================================================
            # 🧩 SECCIÓN GOBIERNO (METADATA TYPES / ASPECTS)
            # =====================================================
            if catalog_entry_name:
                with st.spinner("Cargando aspectos de gobierno..."):
                    aspects = get_term_aspects_from_dataplex(catalog_entry_name)

                if aspects:
                    st.markdown("---")
                    st.markdown("### 🧩 Gobierno del dato")

                    for aspect_id, aspect in aspects.items():
                        # Limpiamos el ID para mostrar un título amigable
                        display_name = aspect_id.split('/')[-1].replace('_', ' ').title()
                        
                        with st.expander(f"📋 {display_name}", expanded=True):
                            # Accedemos a .data (que es donde están los campos del template)
                            fields = getattr(aspect, "data", {})
                            if fields:
                                for key, value in fields.items():
                                    # Formateamos la clave para que sea legible
                                    label = key.replace('_', ' ').capitalize()
                                    st.markdown(f"**{label}:** {value}")
                            else:
                                st.info("Este aspecto no tiene valores cargados.")
                else:
                    st.info("El término no tiene metadata adicional (aspects).")
            else:
                st.warning("No se encontró una entrada de catálogo vinculada a este término.")

    elif search_text:
        st.info("Ingresá al menos 3 caracteres")
