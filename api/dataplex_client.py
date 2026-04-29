from google.cloud import dataplex_v1

client = dataplex_v1.DataplexServiceClient()


def list_lakes(project_id, location):
    parent = f"projects/{project_id}/locations/{location}"
    return client.list_lakes(parent=parent)


def list_zones(project_id, location, lake_id):
    parent = f"projects/{project_id}/locations/{location}/lakes/{lake_id}"
    return client.list_zones(parent=parent)


def list_assets(project_id, location, lake_id, zone_id):
    parent = f"projects/{project_id}/locations/{location}/lakes/{lake_id}/zones/{zone_id}"
    return client.list_assets(parent=parent)