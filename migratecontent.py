import os
import sys
from pathlib import Path
from arcgis.gis import GIS

def migrate_content(portal_url, username, password, migrations_directory):
    gis = GIS(username=username, password=password, url=portal_url)
    if not gis.admin:
        print("Authenticated user does not have administrative privileges. Exiting.")
        sys.exit(1)
    
    epk_files = list(migrations_directory.glob("*.epk"))
    if not epk_files:
        print(f"No .epk files found in migrations directory: {migrations_directory.resolve()}. Exiting.")
        sys.exit(0)
    
    for epk_file in epk_files:
        title = f"{epk_file.stem}_epk_migration"
        epk_item_matches = gis.content.search(query=f"title:{title} AND tags:migration AND tags:epk", max_items=1)
        if epk_item_matches:
            print(f"Item with title '{title}' already exists. Skipping import of {epk_file.name}.")
            continue
        print(f"Importing content from {epk_file.name}...")
        root_folder = gis.content.folders.get("/")
        epk_item = root_folder.add(
            item_properties={
                "title": title, 
                "snippet": f"Content migrated from {epk_file.name}",
                "tags": "migration, epk",
                "type": "Export Package"
            },
            file=str(epk_file.resolve())
        )
        print(epk_item)

        group_name = f"{epk_file.stem}_group"
        group = gis.groups.search(query=f"title:{group_name}", max_groups=1)[0]
        if not group:
            group = gis.groups.create(
                title=group_name, access="org", tags=f"{group_name}, migration", 
                description=f"Group for {epk_file.name} migration", snippet=f"{group_name} group",
            )
        group_migration = group.migration
        epk_import_job = group_migration.load(epk_item=epk_item)
        epk_import_job_result = epk_import_job.result()
        
if __name__ == "__main__":
    portal_url = os.getenv("ARCGIS_PORTAL_URL")
    username = os.getenv("ARCGIS_PORTAL_USERNAME")
    password = os.getenv("ARCGIS_PORTAL_PASSWORD")

    if not portal_url or not username or not password:
        print("Environment variables ARCGIS_PORTAL_URL, ARCGIS_PORTAL_USERNAME, and ARCGIS_PORTAL_PASSWORD must be set. Exiting.")
        sys.exit(1)

    migrations_directory = Path("PROD/migrations")
    if not migrations_directory.is_dir():
        print(f"Migrations directory not found at: {migrations_directory.resolve()}. Exiting.")
        sys.exit(1)
    migrate_content(portal_url, username, password, migrations_directory)
