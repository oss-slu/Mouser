from tokenize import String

import requests

RERUM_BASE = "http://localhost:3001/v1/api"

def get_token(path="rerum_server_nodejs/token.txt"):
    with open(path, "r") as f:
        return f.read().strip()

def submit_annotation(annotation_text, experiment_id):
    token = get_token()
    annotation = {
        "@context": "http://www.w3.org/ns/anno.jsonld",
        "type": "Annotation",
        "body": {
            "type": "TextualBody",
            "value": annotation_text
        },
        "target": experiment_id
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{RERUM_BASE}/create", json=annotation, headers=headers)
        if response.status_code in (200, 201):
            data = response.json()
            annotation_id = data.get('@id', None)

            return True, annotation_id
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def get_annotations(experiment_id):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = {"target": experiment_id}
    try:
        response = requests.post(f"{RERUM_BASE}/query", json=query, headers=headers)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.text
    except Exception as e:
        return None, str(e)

def update_annotation(annotation_id, new_text):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    if not annotation_id.startswith("http"):
        annotation_id = f"http://localhost:3001/{annotation_id.lstrip('/')}"

    updated_annotation = {
        "@id": annotation_id,
        "body": {
            "type": "TextualBody",
            "value": new_text,
            "format": "text/plain"
        }
    }

    try:
        response = requests.put(f"{RERUM_BASE}/update", json=updated_annotation, headers=headers)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def delete_annotations_by_experiment(experiment_id):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = {"target": experiment_id}
    try:
        # First, query annotations for the experiment_id
        response = requests.post(f"{RERUM_BASE}/query", json=query, headers=headers)
        if response.status_code != 200:
            return False, f"Failed to query annotations: {response.text}"

        annotations = response.json()
        if not annotations:
            return True, None 

        # Delete each annotation
        for annotation in annotations:
            full_id = annotation['id']
            annotation_id = full_id.split("/")[-1]
            if not annotation_id:
                continue
            delete_response = requests.delete(f"{RERUM_BASE}/delete/{annotation_id}", headers=headers)
            if delete_response.status_code not in (200, 204):
                return False, f"Failed to delete annotation {annotation_id}: {delete_response.text}"

        return True, None
    except Exception as e:
        return False, str(e)
