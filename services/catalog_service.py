from api.dataplex_client import list_lakes, list_zones, list_assets
import streamlit as st


def get_catalog_tree(project_id, location):
    tree = []

    lakes = list_lakes(project_id, location)

    for lake in lakes:
        lake_id = lake.name.split("/")[-1]

        lake_obj = {
            "name": lake_id,
            "zones": []
        }

        zones = list_zones(project_id, location, lake_id)

        for zone in zones:
            zone_id = zone.name.split("/")[-1]

            zone_obj = {
                "name": zone_id,
                "datasets": []
            }

            assets = list_assets(project_id, location, lake_id, zone_id)

            for asset in assets:
                # extraer dataset de BigQuery
                resource = asset.resource_spec.name

                # ejemplo:
                # //bigquery.googleapis.com/projects/xxx/datasets/yyy
                dataset = resource.split("/")[-1]

                zone_obj["datasets"].append({
                "name": dataset,
                "project": project_id
                })

            lake_obj["zones"].append(zone_obj)

        tree.append(lake_obj)

    return tree

@st.cache_data(ttl=300)
def get_catalog_tree_cached(project_id, location):
    return get_catalog_tree(project_id, location)