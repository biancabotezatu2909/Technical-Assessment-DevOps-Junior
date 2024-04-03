import requests
import pandas as pd
from datetime import datetime

class DrivingLicenseAuthorityAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_data(self, total_records=150):
        data_points = [] # here we will store all the data points meaning all the drivers' records fetched
        for _ in range(total_records // 30): # we iterate 5 times to fetch the desired total_records (30 records per iteration)
            response = requests.get(f"{self.base_url}/drivers-licenses/list", params={"length": 30})
            # we make a request to the API to load 30 drivers' records each time (the data may change with each request, since the API is designed dinamically)
            if response.status_code == 200: # check if the request is succesfull
                data_points.extend(response.json()) # adds the list of records fetched from the request
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
        return data_points


    # filter the drivers' records based on the 'suspendat' field
    def list_suspended_licenses(self, data_points):
        return [dp for dp in data_points if dp['suspendat']]

    # filter the drivers' records based on 'dataDeExpirare' field, comparing with today's date
    def extract_valid_licenses(self, data_points):
        today = datetime.today().date()
        return [dp for dp in data_points if datetime.strptime(dp['dataDeExpirare'], '%d/%m/%Y').date() >= today]

    # we make a dictionary where each key is a category name and its content is the number of licenses that have the corresponding category
    def count_licenses_by_category(self, data_points):
        categories = {}
        for dp in data_points:
            category = dp['categorie']
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        return categories

def main():
    # initialize API client for local Driving License Authority server and fetch and store data from it
    api = DrivingLicenseAuthorityAPI("http://localhost:30000")
    data = api.fetch_data()

    all_drivers_df = pd.DataFrame(data)
    # export the DataFrame containing all drivers' records to an Excel file
    all_drivers_df.to_excel("all_drivers_records.xlsx", index=False)
    print("All drivers' records exported to all_drivers_records.xlsx")

    print("Select an operation:")
    print("1. List suspended licenses")
    print("2. Extract valid licenses issued until today's date")
    print("3. Find licenses based on category and their count")
    operation = input("Enter operation ID: ")

    if operation == '1':
        # fetch suspended license records and convert to DataFrame
        suspended_licenses = api.list_suspended_licenses(data)
        df = pd.DataFrame(suspended_licenses)
        df.to_excel("suspended_licenses.xlsx", index=False)
        print("Suspended licenses exported to suspended_licenses.xlsx")
    elif operation == '2':
        # fetch valid licenses records and convert to DataFrame
        valid_licenses = api.extract_valid_licenses(data)
        df = pd.DataFrame(valid_licenses)
        df.to_excel("valid_licenses.xlsx", index=False)
        print("Valid licenses exported to valid_licenses.xlsx")
    elif operation == '3':
        license_counts = api.count_licenses_by_category(data)
        # convert the dictionary to a DataFrame for exporting
        df = pd.DataFrame(list(license_counts.items()), columns=['Category', 'Count'])
        df.to_excel("license_counts_by_category.xlsx", index=False)
        print("License counts by category exported to license_counts_by_category.xlsx")
    else:
        print("Invalid operation ID.")

if __name__ == "__main__":
    main()
