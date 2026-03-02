import json
import os
from pathlib import Path
from arcgis.gis import GIS

def update_security_settings(portal_url, username, password, security_settings):
    gis = GIS(username=username, password=password, url=portal_url)
    if not gis.admin:
        print("Authenticated user does not have administrative privileges. Exiting.")
        exit(1)

    print(f"Updating Organization Settings if different.")
    security_settings = gis.admin.ux.security_settings
    system_properties = gis.admin.system.properties
    disabled_creation_builtin_accounts = system_properties['disableSignup']
 
    # Apply Changes if different
    if security_settings.anonymous_access != git_settings['anonymous_access']:
        security_settings.anonymous_access = git_settings['anonymous_access']
    if str(security_settings.enable_https) != git_settings['enable_https']:
        security_settings.enable_https = ast.literal_eval(git_settings['enable_https'])
    if str(security_settings.show_social_media) != git_settings['show_social_media']:
        security_settings.show_social_media = ast.literal_eval(git_settings['show_social_media'])
    if str(disabled_creation_builtin_accounts) != git_settings['disableSignup']:
        system_properties['disableSignup'] = git_settings['disableSignup']
        gis.admin.system.properties = system_properties
        
    print("Organization Settings Updated successfully.")

if __name__ == "__main__":
    portal_url = os.getenv("ARCGIS_PORTAL_URL")
    username = os.getenv("ARCGIS_PORTAL_USERNAME")
    password = os.getenv("ARCGIS_PORTAL_PASSWORD")

    if not portal_url or not username or not password:
        print("Environment variables ARCGIS_PORTAL_URL, ARCGIS_PORTAL_USERNAME, and ARCGIS_PORTAL_PASSWORD must be set. Exiting.")
        exit(1)
    
    security_settings_file = Path("PROD/configurations/enterprise_prod_security_settings.json")
    if not security_settings_file.is_file():
        print(f"Organization Security Settings file not found at: {security_settings_file.resolve()}. Exiting.")
        exit(1)

    with open(security_settings_file.resolve()) as json_file:
        security_settings = json.load(json_file)

    update_security_settings(portal_url, username, password, security_settings)