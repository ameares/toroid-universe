import requests
from bs4 import BeautifulSoup
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P

def get_all_core_data_values():
    """Extract all core data values from the table."""
    url = "https://www.mag-inc.com/Products/Powder-Cores/Kool-Mu-Cores"
    
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table containing core data
    table = soup.find("table")
    if not table:
        raise ValueError("Could not find the core data table on the page.")
    
    # Extract all core data values from first column
    core_values = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if cols:  # Skip header rows
            core_data = cols[0].get_text(strip=True)
            if core_data:
                core_values.append(core_data)
    
    return sorted(core_values)

def get_kool_mu_core_data(core_data_value):
    url = "https://www.mag-inc.com/Products/Powder-Cores/Kool-Mu-Cores"
    
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table containing core data
    table = soup.find("table")
    if not table:
        raise ValueError("Could not find the core data table on the page.")
    
    # Extract rows from the table
    rows = table.find_all("tr")
    
    # Iterate over rows to find the desired Core Data value
    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue  # Skip header rows
        
        # First column is the Core Data
        core_data = cols[0].get_text(strip=True)
        
        if core_data == str(core_data_value):
            # Extract the rest of the row
            row_data = [str(core_data)]  # Add core data as string first
            for col in cols[1:]:
                text = col.get_text(strip=True)
                if '(' in text:  # Remove link reference
                    text = text.split('(')[0].strip()
                if not text:  # Handle empty strings
                    row_data.append(None)
                else:
                    try:
                        # Convert to float if possible
                        value = float(text)
                        row_data.append(value)
                    except ValueError:
                        # Keep as string if not convertible
                        row_data.append(text)
            
            return row_data
    
    return None  # Core Data not found

def create_core_data_table():
    """Create a table with all core data and save it as an ODS file."""
    core_values = get_all_core_data_values()
    
    # Get data for first core to extract headers
    first_core_data = get_kool_mu_core_data(core_values[0])
    if not first_core_data:
        raise ValueError("Could not get data for first core")
    
    # Create headers based on specified columns
    headers = [
        "Core Data", "14u", "19u", "26u", "40u", "60u", "75u", "90u", 
        "125u", "Le", "Ae", "Ve", "OD", "ID", "HT"
    ]
    
    # Create table with headers as first row
    table_data = [headers]
    
    # Collect data for all cores
    print("Collecting data for all cores...")
    processed = 0
    skipped = 0
    for core_value in core_values:
        print(f"\nProcessing core {core_value}...")
        try:
            core_data = get_kool_mu_core_data(core_value)
            if core_data:
                print(f"  Found data: {core_data}")
                table_data.append(core_data)
                processed += 1
            else:
                print(f"  No data found for core {core_value}")
                skipped += 1
        except Exception as e:
            print(f"  Error processing core {core_value}: {str(e)}")
            skipped += 1
    
    print(f"\nSummary:")
    print(f"  Successfully processed: {processed} cores")
    print(f"  Skipped/failed: {skipped} cores")
    
    # Create ODS document
    doc = OpenDocumentSpreadsheet()
    spreadsheet = Table(name="Sheet 1")
    doc.spreadsheet.addElement(spreadsheet)
    
    # Add all rows
    for row_data in table_data:
        tr = TableRow()
        spreadsheet.addElement(tr)
        for value in row_data:
            tc = TableCell()
            if value is not None:  # Handle None values
                p = P(text=str(value))
                tc.addElement(p)
            tr.addElement(tc)
    
    # Save to file
    doc.save("kool_mu_cores.ods")
    return len(table_data) - 1  # Subtract 1 for header row

# Example usage
if __name__ == "__main__":
    try:
        # First get all available core data values
        core_values = get_all_core_data_values()
        num_cores = len(core_values)
        print(f"Found {num_cores} core data values:")
        print(f"Length of core_data list: {num_cores}")
        print(", ".join(core_values))
        
        # Create the complete table
        print("\nCreating core data table...")
        num_processed = create_core_data_table()
        print(f"\nProcessed {num_processed} cores and saved to kool_mu_cores.ods")
        
    except Exception as e:
        print(f"Error: {e}")
