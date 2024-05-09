import csv
import json

def csv_to_json(csv_file, obc_name):
    bc_dict = {}
    bc_dict = []

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Comment']:
                continue
            elif row['Name'].startswith('BC_'):
                bc_name = row['Name']
                bc_id = int(row['BCID'])
                bc_dict.append({"name": bc_name, "id": bc_id})

    return bc_dict

def connect_json(aobc_csv_file, tobc_csv_file, mif_csv_file):
    data = []
    aobc_bc_dict = csv_to_json(aobc_csv_file, "AOBC")
    tobc_bc_dict = csv_to_json(tobc_csv_file, "TOBC")
    mif_bc_dict = csv_to_json(mif_csv_file, "MIF")

    data.append({"obc_name": "AOBC", "bc": aobc_bc_dict, "el": [], "eh": []})
    data.append({"obc_name": "TOBC", "bc": tobc_bc_dict, "el": [], "eh": []})
    data.append({"obc_name": "MIF", "bc": mif_bc_dict, "el": [], "eh": []})

    return data

def main(json_path, aobc_csv_path, tobc_csv_path, mif_csv_path):

    json_data = connect_json(aobc_csv_path, tobc_csv_path, mif_csv_path)

    with open(json_path, 'w') as outfile:
        json.dump(json_data, outfile, indent=2)


if __name__ == "__main__":

    json_path = '/home/kosuke/issl/temp/output.json'
    aobc_csv_path = '/home/kosuke/issl/temp/ISSL6U_TOBC_CMD_DB_BCT.csv'
    tobc_csv_path = '/home/kosuke/issl/temp/ISSL6U_TOBC_CMD_DB_BCT.csv'
    mif_csv_path = '/home/kosuke/issl/temp/ISSL6U_TOBC_CMD_DB_BCT.csv'

    main(json_path, aobc_csv_path, tobc_csv_path, mif_csv_path)
