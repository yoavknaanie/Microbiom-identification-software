import os
import requests
from msfragger_runner import current_date_argument


# def download_proteomes_table(organism_name):
#     """
#         download proteomes table of chosen organism
#         param: organism_name "Clostridium+perfringens"
#     """
#     try:
#         response = requests.get(f"https://rest.uniprot.org/proteomes/stream?format=list&query=%28{organism_name}%29")
#     proteome_list = []
#     if response.status_code == 200:
#         for row in response.iter_lines(decode_unicode=True):
#             proteome_list.append(row.strip())
#     else:
#         print(f"{organism_name} not found in Uniprot!")
#     if len(proteome_list) == 0:
#         print(f"{organism_name} not found in Uniprot!")
#     return proteome_list
def download_proteomes_table(organism_name):
    """
    Download the proteomes table of the chosen organism.

    param: organism_name: str, e.g., "Clostridium+perfringens"
    """
    proteome_list = []

    try:
        response = requests.get(f"https://rest.uniprot.org/proteomes/stream?format=list&query=%28{organism_name}%29")
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        for row in response.iter_lines(decode_unicode=True):
            proteome_list.append(row.strip())

        if len(proteome_list) == 0:
            print(f"No proteomes found for {organism_name} in UniProt!")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")

    return proteome_list

def download_fastas(proteome_list, directory_path):
    """
        for each item in list download fasta file and creates folder with the same name as the fasta file.
        first try to download from:
        https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28%28proteome%3A{UP_number}%29%29
        file name:
        uniprotkb_proteome_{UP_number}_{cur_date}
        * cur_date format: year_month_day

        if that doesn't work, try:
        https://rest.uniprot.org/uniparc/stream?format=fasta&query=%28%28upid%3A{UP_number}%29%29
        file name:
        uniparc_upid_{UP_number}_{cur_date}
        :return
        folder names list

    """
    folder_names = []
    temp_dir = f"{directory_path}\\fasta"
    create_directory(directory_path)
    cur_date = current_date_argument()
    for proteome in proteome_list:
        create_directory(directory_path)
        proteome_downloaded = False
        try:
            response1 = requests.get(f"https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28%28proteome%3A"
                                 f"{proteome}%29%29")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")

        if response1.status_code == 200 and response1.content:
            # fasta_file_name = f"uniprotkb_proteome_{proteome}_{cur_date}"
            fasta_file_name = proteome
            with open(f"{directory_path}\\fasta\\{fasta_file_name}.fasta", 'wb') as fasta_file:
                fasta_file.write(response1.content)
                fasta_file.close()
            os.rename(temp_dir, f"{directory_path}\\{fasta_file_name}")
            folder_names.append(fasta_file_name)
            proteome_downloaded = True

        if not proteome_downloaded:
            try:
                response2 = requests.get(f"https://rest.uniprot.org/uniparc/stream?format=fasta&query=%28%28upid%3A"
                                                                                f"{proteome}%29%29")
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except requests.exceptions.ConnectionError as conn_err:
                print(f"Connection error occurred: {conn_err}")
            except requests.exceptions.Timeout as timeout_err:
                print(f"Timeout error occurred: {timeout_err}")
            except requests.exceptions.RequestException as req_err:
                print(f"An error occurred: {req_err}")

            if response2.status_code == 200 and response2.content:
                # fasta_file_name = f"uniparc_upid_{proteome}_{cur_date}"
                fasta_file_name = proteome
                with open(f"{directory_path}\\fasta\\{fasta_file_name}.fasta", 'wb') as fasta_file:
                    fasta_file.write(response2.content)
                os.rename(temp_dir, f"{directory_path}\\{fasta_file_name}")
                folder_names.append(fasta_file_name)
                proteome_downloaded = True
        if not proteome_downloaded:
            os.rmdir(temp_dir)
            print(proteome, "fasta file was not found in uniprot")
    return folder_names


def create_directory(directory_path):
    try:
        os.makedirs(f"{directory_path}\\fasta")
    except OSError as e:
        print(f"Error creating folder: {str(e)}")


def download_all_fastas_of_organism(organism_name, directory_path):
    """
        creates a folder contains the proteomes fasta file.
        return list of names of folders (same as fasta files names)
    """
    proteome_list = download_proteomes_table(organism_name)
    folder_list = download_fastas(proteome_list, directory_path)
    return folder_list


def download_all_fastas_of_organism_random(organism_name, directory_path, fastas_number):
    proteome_list = download_proteomes_table(organism_name)
    jump = len(proteome_list) // fastas_number
    final_list = []
    if len(proteome_list) > fastas_number:
        print("jump:", jump)
        print("range(fastas_number):", range(fastas_number))
        for i in range(fastas_number):
            final_list.append(proteome_list[i*jump])
        folder_list = download_fastas(final_list, directory_path)
    else:
        folder_list = download_fastas(proteome_list, directory_path)
    with open(rf"{directory_path}/{organism_name}_fasta_list.txt", "w") as file:
        for fasta in folder_list:
            file.write(fasta + "\n")
    return folder_list
