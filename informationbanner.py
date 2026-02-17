import os
from pathlib import Path
from arcgis.gis import GIS

def set_information_banner(portal_url, username, password, information_banner):
    gis = GIS(username=username, password=password, url=portal_url)
    if not gis.admin:
        print("Authenticated user does not have administrative privileges. Exiting.")
        exit(1)

    print(f"Setting information banner to: {information_banner}")
    set_banner_success = gis.admin.ux.security_settings.set_informational_banner(information_banner, enabled=True)
    if not set_banner_success:
        print("Failed to set information banner.")
        exit(1)

    print("Information banner set successfully.")

if __name__ == "__main__":
    portal_url = os.getenv("ARCGIS_PORTAL_URL")
    username = os.getenv("ARCGIS_PORTAL_USERNAME")
    password = os.getenv("ARCGIS_PORTAL_PASSWORD")

    if not portal_url or not username or not password:
        print("Environment variables ARCGIS_PORTAL_URL, ARCGIS_PORTAL_USERNAME, and ARCGIS_PORTAL_PASSWORD must be set. Exiting.")
        exit(1)
    
    information_banner_path = Path("PROD/configurations/informationbanner.txt")
    if not information_banner_path.is_file():
        print(f"Information banner file not found at: {information_banner_path.resolve()}. Exiting.")
        exit(1)

    information_banner = information_banner_path.read_text()

    set_information_banner(portal_url, username, password, information_banner)
