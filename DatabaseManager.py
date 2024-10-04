import sqlite3
import os
import json

class DatabaseManager:
    _instance = None

    def __init__(self, db_name='carbFF3.db'):
        """Initialize the database connection and create the table if it doesn't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create the pmfs and configurations tables if they don't already exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS pmfs (
            file_id TEXT PRIMARY KEY,
            data TEXT
        )
        ''')

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS configurations (
                    config_id TEXT PRIMARY KEY,
                    molecule_name TEXT,
                    data TEXT
                )
                ''')
        self.conn.commit()

    def save_configuration(self, config_id, molecule_name, config_data):
        """Save a configuration to the database, including the molecule name."""
        json_data = self.convert_data_to_json(config_data)

        # Check if the configuration ID already exists
        self.cursor.execute('SELECT COUNT(*) FROM configurations WHERE config_id = ?', (config_id,))
        exists = self.cursor.fetchone()[0]

        if exists == 0:
            self.cursor.execute(
                'INSERT INTO configurations (config_id, molecule_name, data) VALUES (?, ?, ?)',
                (config_id, molecule_name, json_data)
            )
        else:
            self.cursor.execute(
                'UPDATE configurations SET molecule_name = ?, data = ? WHERE config_id = ?',
                (molecule_name, json_data, config_id)
            )

        self.conn.commit()

    def load_configuration(self, config_id):
        """Load a configuration from the database by config_id."""
        self.cursor.execute('SELECT config_data FROM configurations WHERE config_id = ?', (config_id,))
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def read_file_data(self, file_path):
        """Read coordinate data from a file and return it as a list of tuples."""
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = []
            for line in lines:
                if "#" in line or line == "\n":
                    continue
                parts = line.split()
                x, y, z = map(float, parts)
                data.append((x, y, z))
            return data

    def convert_data_to_json(self, data):
        """Convert a list of coordinate tuples to a JSON string."""
        return json.dumps(data)

    def convert_json_to_data(self, json_data):
        """Convert a JSON string to a list of coordinate tuples."""
        return json.loads(json_data)

    def insert_data_into_db(self, file_id, data):
        """Insert a list of coordinate tuples into the database as a JSON string if not already present."""
        json_data = self.convert_data_to_json(data)

        # Check if the file_id already exists in the table
        self.cursor.execute('SELECT COUNT(*) FROM pmfs WHERE file_id = ?', (file_id,))
        exists = self.cursor.fetchone()[0]

        # Insert the data only if the file_id does not exist
        if exists == 0:
            self.cursor.execute('INSERT INTO pmfs (file_id, data) VALUES (?, ?)', (file_id, json_data))
            self.conn.commit()

    def process_files(self, file_directory):
        """Process all files in a directory and insert their data into the database."""
        for file_name in os.listdir(file_directory):
            if file_name.endswith('.pmf'):
                file_path = os.path.join(file_directory, file_name)
                file_id = os.path.splitext(file_name)[0]  # Extract file name
                data = self.read_file_data(file_path)
                self.insert_data_into_db(file_id, data)

    def query_data_by_file(self, file_id):
        """Query and return all coordinate data associated with a specific file_id."""
        self.cursor.execute('SELECT data FROM pmfs WHERE file_id = ?', (file_id,))
        result = self.cursor.fetchone()
        if result:
            json_data = result[0]
            return self.convert_json_to_data(json_data)
        return None

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Example Usage
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Process all files in a directory
    db_manager.process_files('PMF')  # Update with your directory path

    # Query data for a specific file
    data = db_manager.query_data_by_file('aDFuc13bDMan')
    if data:
        for row in data:
            print(row)

    # Close the database connection
    db_manager.close()
