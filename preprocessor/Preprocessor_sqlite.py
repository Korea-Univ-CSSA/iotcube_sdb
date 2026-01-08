# import os
# import json
# import sqlite3

# # SQLite database file
# db_file_path = "new_transformed_db.sqlite"

# # Connect to SQLite database (creates the file if it doesn't exist)
# conn = sqlite3.connect(db_file_path)
# cursor = conn.cursor()

# # Create table with composite primary key
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS hash_data (
#         hash TEXT,
#         oss_version TEXT,
#         PRIMARY KEY (hash, oss_version)
#     )
# ''')

# # Directory containing the original DB files
# db_dir = "./componentDB_file"

# # Transform and insert the data into the SQLite DB
# for filename in os.listdir(db_dir):
#     if filename.endswith("_sig"):  # Ensure you are only processing the correct files
#         oss_name = filename.split("_sig")[0]  # Extract OSS name from the filename

#         # Open and read the content of the file
#         with open(os.path.join(db_dir, filename), "r") as db_file:
#             data = json.load(db_file)

#             # Insert data into SQLite
#             for entry in data:
#                 hash_value = entry["hash"]
#                 for version in entry["vers"]:
#                     oss_version = f"{oss_name},{version}"
#                     cursor.execute('''
#                         INSERT OR IGNORE INTO hash_data (hash, oss_version)
#                         VALUES (?, ?)
#                     ''', (hash_value, oss_version))

# # Commit and close the connection
# conn.commit()
# conn.close()

# print(f"Data successfully transformed and stored in {db_file_path}")
import os
import json
import sqlite3

# SQLite database file
# db_file_name = "/mnt/sdb1/c_cpp/preprocessor/optimized_transformed_db.sqlite"
db_file_name = "ossfiltering_db.sqlite" 

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect(db_file_name)
cursor = conn.cursor()

# Create table with composite primary key
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hash_data (
        hash TEXT,
        oss_version TEXT,
        PRIMARY KEY (hash, oss_version)
    )
''')

# Directory containing the original DB files
# db_dir = "/mnt/sdb1/c_cpp/preprocessor/componentDB_file"
db_dir = os.getcwd() + "/../testdb/preprocessor/componentDB_file/" 

# Transform and insert the data into the SQLite DB
for filename in os.listdir(db_dir):
    if filename.endswith("_sig"):
        oss_name = filename.split("_sig")[0]

        with open(os.path.join(db_dir, filename), "r") as db_file:
            data = json.load(db_file)

            # Dictionary to store versions by hash
            hash_version_map = {}

            for entry in data:
                hash_value = entry["hash"]
                versions = entry["vers"]

                if hash_value not in hash_version_map:
                    hash_version_map[hash_value] = set()
                
                # Add versions to the set (automatically removes duplicates)
                hash_version_map[hash_value].update(versions)

            # Insert into SQLite, joining all versions for a hash
            for hash_value, versions in hash_version_map.items():
                # Sort versions to keep the order consistent
                sorted_versions = sorted(versions, key=int)
                version_list = ",".join(sorted_versions)
                oss_version = f"{oss_name},{version_list}"
                cursor.execute('''
                    INSERT OR IGNORE INTO hash_data (hash, oss_version)
                    VALUES (?, ?)
                ''', (hash_value, oss_version))

# Commit and close the connection
conn.commit()
conn.close()

print(f"Data successfully transformed and stored in {db_file_name}")
