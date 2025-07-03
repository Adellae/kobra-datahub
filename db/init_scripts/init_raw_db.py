from db.db_utils import initialize_db

if __name__ == "__main__":
    initialize_db(db_path = "data/database/raw.db", schema_path = "db/schema/raw_schema.sql")