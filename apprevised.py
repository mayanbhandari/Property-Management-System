from flask import Flask, render_template, request, jsonify, send_file
import psycopg2
import datetime
import csv
import io
import pandas as pd  # For Excel export

app = Flask(__name__)

# Function to connect to the database
def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="MCSUITE",
            user="postgres",
            password="postgres",
            host="10.197.214.16",
            port="5432"
        )
        return connection
    except Exception as e:
        print("Error connecting to PostgreSQL:", e)
        return None

@app.route('/')
def index():
    current_date = datetime.datetime.now().strftime('%d/%m/%Y')
    return render_template('index.html', current_date=current_date)

@app.route('/search', methods=['POST'])
def search_property():
    property_address = request.json.get('searchQuery', '').strip().upper()
    upic_value = request.json.get('upicQuery', '').strip().upper()
    ward_value = request.json.get('wardQuery', '').strip().upper()
    colony_value = request.json.get('colonyQuery', '').strip().upper()
    zone_value = request.json.get('zoneQuery', '').strip().upper()
    property_type = request.json.get('propertyType', '').strip().upper()
    property_category = request.json.get('propertyCategory', '').strip().upper()

    connection = connect_to_db()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'})

    try:
        cursor = connection.cursor()

        # Base query
        query = '''
            SELECT upic, upper(trim(property_address)), owner_name, pincode,
                   lane, sector, property_type_name, ward_name, mobile_number, floor_count, is_drafted, zone_name,
                   is_registered, floor_names, colony_name, to_char(created_date,'dd-MM-yyyy') as created_date, to_char(modified_date,'dd-MM-yyyy') as modified_date
            FROM "property"."rnd_data"
            WHERE property_address IS NOT NULL
            AND property_address != ''
            AND owner_name IS NOT NULL
            AND owner_name != ''
        '''

        # Add conditions based on inputs
        query_params = []
        if property_address:
            query += " AND upper(trim(property_address)) LIKE %s"
            query_params.append(f"%{property_address}%")
        if upic_value:
            query += " AND upper(trim(upic)) = %s"
            query_params.append(upic_value)
        if ward_value:
            query += " AND upper(trim(ward_name)) = %s"
            query_params.append(ward_value)
        if colony_value:
            query += " AND upper(trim(colony_name)) = %s"
            query_params.append(colony_value)
        if zone_value:
            query += " AND upper(trim(zone_name)) = %s"
            query_params.append(zone_value)
        if property_type:
            query += " AND upper(trim(property_type_name)) = %s"
            query_params.append(property_type)
        if property_category:
            query += " AND upper(trim(property_category)) = %s"
            query_params.append(property_category)

        # Finalize query
        query += " ORDER BY property_address DESC;"

        cursor.execute(query, tuple(query_params))  # Execute with parameterized query
        rows = cursor.fetchall()

        data = [
            {
                'upic': row[0],
                'property_address': row[1],
                'owner_name': row[2],
                'pincode': row[3],
                'lane': row[4],
                'sector': row[5],
                'property_type_name': row[6],
                'ward_name': row[7],
                'mobile_number': row[8],
                'floor_count': row[9],
                'is_drafted': row[10],
                'zone_name': row[11],
                'is_registered': row[12],
                'floor_name': row[13],
                'colony_name': row[14],
                'created_date': row[15],
                'modified_date': row[16]
            }
            for row in rows
        ]
        return jsonify(data)

    except Exception as error:
        print("Error while fetching data from PostgreSQL:", error)
        return jsonify({'error': 'Error while fetching data from the database'})
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/download_csv', methods=['POST'])
def download_csv():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data to download'})

    # Prepare CSV data
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    
    # Write header
    if data:
        header = data[0].keys()
        writer.writerow(header)
    
    # Write data rows
    for row in data:
        writer.writerow(row.values())

    # Create a response
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='property_data.csv')

@app.route('/download_excel', methods=['POST'])
def download_excel():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data to download'})

    df = pd.DataFrame(data)
    
    # Create an in-memory buffer
    excel_buffer = io.BytesIO()
    
    # Use pandas to write the DataFrame to the buffer
    df.to_excel(excel_buffer, index=False)
    
    # Rewind the buffer to the beginning
    excel_buffer.seek(0)

    return send_file(excel_buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='property_data.xlsx')

@app.route('/find_duplicate_upics', methods=['POST'])
def find_duplicate_upics():
    property_address = request.json.get('property_address', '').strip().upper()

    connection = connect_to_db()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'})

    try:
        cursor = connection.cursor()
        query = '''
            SELECT upic, COUNT(*)
            FROM "property"."rnd_data"
            WHERE upper(trim(property_address)) = %s
            GROUP BY upic
            HAVING COUNT(*) > 1;
        '''
        cursor.execute(query, (property_address,))
        rows = cursor.fetchall()

        duplicates = [{'upic': row[0], 'count': row[1]} for row in rows]
        return jsonify(duplicates)

    except Exception as e:
        print("Error finding duplicate UPICs:", e)
        return jsonify({'error': 'Error finding duplicate UPICs'})
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
