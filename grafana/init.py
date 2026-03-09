import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD")

PG_HOST = os.getenv("POSTGRES_HOST")
PG_DB = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT")


def wait_for_grafana(max_retries=30, delay=2):
    """Wait for Grafana to be ready"""
    print("Waiting for Grafana to be ready...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("✓ Grafana is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"  Attempt {attempt + 1}/{max_retries}...")
        time.sleep(delay)
    
    print("✗ Grafana not ready")
    return False


def create_api_key():
    """Create service account and token (Grafana 9+)"""
    print("Creating service account and token...")
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    headers = {"Content-Type": "application/json"}
    
    sa_payload = {"name": "ProgrammaticAccess", "role": "Admin", "isDisabled": False}
    
    # Try to create service account
    response = requests.post(
        f"{GRAFANA_URL}/api/serviceaccounts",
        auth=auth,
        headers=headers,
        json=sa_payload
    )
    
    if response.status_code in [200, 201]:
        sa_id = response.json()["id"]
        print(f"✓ Service account created (ID: {sa_id})")
    elif response.status_code == 400 or response.status_code == 409:
        # Account already exists, find it
        print("Service account already exists, finding it...")
        search_response = requests.get(
            f"{GRAFANA_URL}/api/serviceaccounts/search",
            auth=auth,
            params={"query": "ProgrammaticAccess"}
        )
        
        if search_response.status_code == 200:
            accounts = search_response.json().get("serviceAccounts", [])
            if accounts:
                sa_id = accounts[0]["id"]
                print(f"✓ Using existing service account (ID: {sa_id})")
                
                # Delete old tokens to avoid conflicts
                tokens_response = requests.get(
                    f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens",
                    auth=auth
                )
                if tokens_response.status_code == 200:
                    for token in tokens_response.json():
                        if token["name"] == "api-token":
                            print(f"  Deleting existing token: {token['name']}")
                            requests.delete(
                                f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens/{token['id']}",
                                auth=auth
                            )
            else:
                print("✗ Service account not found")
                return None
        else:
            print(f"✗ Search failed: {search_response.text}")
            return None
    else:
        print(f"✗ Service account error: {response.text}")
        return None
    
    # Create token
    token_payload = {"name": "api-token"}
    token_response = requests.post(
        f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens",
        auth=auth,
        headers=headers,
        json=token_payload
    )
    
    if token_response.status_code in [200, 201]:
        token = token_response.json()["key"]
        print("✓ Token created")
        return token
    else:
        print(f"✗ Token error: {token_response.text}")
        return None


def create_or_update_datasource(api_key):
    """Create or update PostgreSQL datasource"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    datasource_payload = {
        "name": "PostgreSQL",
        "type": "postgres",
        "url": PG_HOST,  # Just hostname, no port
        "access": "proxy",
        "user": PG_USER,
        "database": PG_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {
            "sslmode": "disable",
            "postgresVersion": 1300,
            "port": int(PG_PORT)  # Port goes here
        },
        "secureJsonData": {"password": PG_PASSWORD},
    }

    print("\nConfiguring datasource:")
    print(f"  Host: {PG_HOST}")
    print(f"  Port: {PG_PORT}")
    print(f"  Database: {PG_DB}")
    print(f"  User: {PG_USER}")

    # Check if datasource exists
    response = requests.get(
        f"{GRAFANA_URL}/api/datasources/name/PostgreSQL",
        headers=headers,
    )

    if response.status_code == 200:
        # Update existing
        existing_datasource = response.json()
        datasource_id = existing_datasource["id"]
        print(f"\nUpdating existing datasource (ID: {datasource_id})")
        response = requests.put(
            f"{GRAFANA_URL}/api/datasources/{datasource_id}",
            headers=headers,
            json=datasource_payload,
        )
    else:
        # Create new
        print("\nCreating new datasource")
        response = requests.post(
            f"{GRAFANA_URL}/api/datasources",
            headers=headers,
            json=datasource_payload
        )

    if response.status_code in [200, 201]:
        print("✓ Datasource configured successfully")
        result = response.json()
        return result.get("datasource", {}).get("uid") or result.get("uid")
    else:
        print(f"✗ Datasource error: {response.status_code}")
        print(f"  {response.text}")
        return None


def create_dashboard(api_key, datasource_uid):
    """Create or update dashboard"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    dashboard_file = "dashboard.json"

    # Check if file exists
    if not os.path.exists(dashboard_file):
        print(f"\n⚠️  {dashboard_file} not found, skipping dashboard creation")
        return None

    try:
        with open(dashboard_file, "r") as f:
            dashboard_json = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Error decoding {dashboard_file}: {str(e)}")
        return None

    print(f"\n✓ Dashboard JSON loaded from {dashboard_file}")

    # Update datasource UID in panels
    panels_updated = 0
    for panel in dashboard_json.get("panels", []):
        if isinstance(panel.get("datasource"), dict):
            panel["datasource"]["uid"] = datasource_uid
            panels_updated += 1
        elif isinstance(panel.get("targets"), list):
            for target in panel["targets"]:
                if isinstance(target.get("datasource"), dict):
                    target["datasource"]["uid"] = datasource_uid
                    panels_updated += 1

    print(f"  Updated {panels_updated} panel datasource references")

    # Remove keys that cause conflicts
    dashboard_json.pop("id", None)
    dashboard_json.pop("uid", None)
    dashboard_json.pop("version", None)

    # Prepare payload
    dashboard_payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": "Updated by init script",
    }

    # Create/update dashboard
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        headers=headers,
        json=dashboard_payload
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Dashboard created successfully")
        print(f"  URL: {GRAFANA_URL}{result.get('url', '')}")
        return result.get("uid")
    else:
        print(f"✗ Dashboard creation failed: {response.status_code}")
        print(f"  {response.text}")
        return None


def main():
    """Main setup function"""
    
    # Create API key
    print("\n" + "-"*60)
    api_key = create_api_key()
    if not api_key:
        print("\n✗ Failed to create API key")
        return
    
    # Create/update datasource
    print("\n" + "-"*60)
    datasource_uid = create_or_update_datasource(api_key)
    if not datasource_uid:
        print("\n✗ Failed to configure datasource")
        return
    
    # Create/update dashboard
    print("\n" + "-"*60)
    create_dashboard(api_key, datasource_uid)
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()