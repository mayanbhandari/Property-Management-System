# Property Management System

## Description
A Property Management System built with Flask and PostgreSQL to manage, search, and filter property records. The system provides advanced search queries, duplicate UPIC detection, and data export in CSV/Excel formats.

## Features
- Advanced property search by Address, UPIC, Ward, Zone, and Property Type.
- Duplicate UPIC detection.
- Export property data in CSV and Excel formats.
- Simple and responsive UI using HTML/CSS.
- Easily deployable with Docker support.

## Technologies Used
- Flask (Python)
- PostgreSQL
- Pandas
- HTML/CSS
- Docker (Optional for deployment)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mayanbhandari/Property-Management-System.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Property-Management-System
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the database connection in the `config.py` file.
5. Run the application:
   ```bash
   python app.py
   ```

## Exporting Data
- Data can be exported in **CSV** and **Excel** formats from the web interface.
- The system supports bulk property record downloads.

## License
This project is licensed under the MIT License.

