import json
import os
from pathlib import Path
from arcgis.gis import GIS

def _handle_add_result_errors(add_result):
    """prints add_result errors and returns True if add_result was successful, False otherwise"""
    has_error = False
    for group_name, result in add_result.items():
        if result.get("notAdded"):
            has_error = True
            print(f"Failed to add users to group '{group_name}': {', '.join(result['notAdded'])}")
    return not has_error

def set_group_membership(portal_url, username, password, group_membership_config):
    gis = GIS(username=username, password=password, url=portal_url)
    if not gis.admin:
        print("Authenticated user does not have administrative privileges. Exiting.")
        exit(1)
    
    add_results = {}
    for group_name, group_info in group_membership_config.get("groups", {}).items():
        members = group_info.get("members", [])
        add_results[group_name] = _set_group_membership(gis, group_name, members)
    
    completed_successfully = _handle_add_result_errors(add_results)
    if completed_successfully:
        print("Group membership set successfully.")
    else:
        print("Failed to set group membership.")
        exit(1)

def _set_group_membership(gis, group_name, members):
    groups = gis.groups.search(query=f"title:{group_name}", max_groups=1)
    if not groups:
        groups = [gis.groups.create(title=group_name, access="org")]
        print(f"Group '{group_name}' created.")
    
    group = groups[0]
    current_usernames = set([member['username'] for member in group.get_members()['users']])

    users_to_add = [user for user in members if user not in current_usernames]

    if users_to_add:
        add_result = group.add_users(users_to_add)
        print(f"Added users to group '{group_name}': {', '.join(users_to_add)}")
        return add_result
    return {}


if __name__ == "__main__":
    portal_url = os.getenv("ARCGIS_PORTAL_URL")
    username = os.getenv("ARCGIS_PORTAL_USERNAME")
    password = os.getenv("ARCGIS_PORTAL_PASSWORD")

    if not portal_url or not username or not password:
        print("Environment variables ARCGIS_PORTAL_URL, ARCGIS_PORTAL_USERNAME, and ARCGIS_PORTAL_PASSWORD must be set. Exiting.")
        exit(1)
    
    group_membership_path = Path("PROD/configurations/group_membership.json")
    if not group_membership_path.is_file():
        print(f"Group membership file not found at: {group_membership_path.resolve()}. Exiting.")
        exit(1)

    group_membership_raw_json = group_membership_path.read_text()
    try:
        group_membership = json.loads(group_membership_raw_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse group membership JSON: {e}. Exiting.")
        exit(1)

    set_group_membership(portal_url, username, password, group_membership)