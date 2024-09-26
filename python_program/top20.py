import numpy as np
import pandas as pd
import os
import shutil

import msfragger_runner
from download import convert_file_to_list
from main import CONTAM_NOTATION

BGAL_ECOLI_CONTAMINANT = "sp|P00722|BGAL_ECOLI"


def calculate_proteomes_sizes(all_proteomes_folder, fas):
    """
    return number of protein in fasta file
    """
    prot_num = 0
    with open(f"{all_proteomes_folder}\\{fas}\\{fas}.fasta") as file:
        for line in file:
            line = line.strip()
            if line.startswith('>'):
                prot_num += 1
    return prot_num


# imported functions
def fasta_peptide_dict(raw, proteomes_fasta_list, folder_path):
    """
    creates a dictionary of {fasta file name: peptide's array}
    """
    dictionary = {}
    for fas in proteomes_fasta_list:
        if "peptide.tsv" in os.listdir(f'{folder_path}\\{fas}\\{raw}'):
            df = pd.read_csv(f"{folder_path}\\{fas}\\{raw}\\peptide.tsv", sep="\t")
            col_name = 'Peptide'
            col_array = df[col_name].values
            dictionary[fas] = col_array
    return dictionary


def fasta_pandas_df_dict(raw, proteomes_fasta_list, folder_path):
    """
    dict {fasta file name: pandas file of peptide}
    """
    dictionary = {}
    for fas in proteomes_fasta_list:
        if "peptide.tsv" in os.listdir(f'{folder_path}\\{fas}\\{raw}'):
            df = pd.read_csv(f"{folder_path}\\{fas}\\{raw}\\peptide.tsv", sep="\t")
            dictionary[fas] = df
    return dictionary


def fasta_bacteria_protein_dict(peptides_dictionary, df_dictionary, contam_notation):
    """
    creates dict of number of peptides.
    values are lists of proteins for each fasta file (key) (length = number of peptides found)
    """
    contaminants_cleaned_dict = {}
    iterable_keys = np.array(list(peptides_dictionary.keys()), dtype=object)
    for fas in iterable_keys:
        # if (len(human_proteins_dictionary[fas]) >= 200) and (len(human_proteins_dictionary[fas]) <= 240):
        contaminants_cleaned_dict[fas] = []
        for val in df_dictionary[fas]["Protein"].values:
            if val.split("_")[-1] not in contam_notation and val != BGAL_ECOLI_CONTAMINANT:
                contaminants_cleaned_dict[fas].append(val)

    return contaminants_cleaned_dict


def copy_relevant_proteins(file, chosen_proteome, cur_folder, organism_name, found_organism_proteins_names):
    count = 1
    to_write = False
    proteins_found = []
    with open(rf"{cur_folder}\{chosen_proteome}.fasta", 'r') as fasta_file:
        for line in fasta_file:
            if line[0] == '>':
                if line.split(" ")[0].split("_")[-1] != 'HUMAN':
                    if line.split(" ")[0][1:] in found_organism_proteins_names:
                        protein_name = f'>bacteria_{organism_name.replace("+", "_")}_{count}'
                        proteins_found.append(protein_name[1:])
                        count += 1
                        line = protein_name + " " + " ".join(line.split(" ")[1:])
                        to_write = True
                    else:
                        to_write = False
                else:
                    to_write = False
            if to_write:
                file.write(line)

    fasta_file.close()
    return proteins_found


def combine_human_and_bacteria(human_fasta, combined_bacteria):
    with open(combined_bacteria, 'a') as new_file, open(human_fasta, 'r') as human:
        to_copy = human.read()
        new_file.write(to_copy)
    new_file.close()
    human.close()


def top20_main_function(raw_list, organisms, directory, chosen_fastas_folder):
    """
    creates a unified proteome Fasta files of the organisms res_folder\combined_proteome.fasta
    """
    found_proteins_names = set()
    with open(rf"{chosen_fastas_folder}\combined_proteome.fasta", 'a') as combined_proteome_file, open(
            rf"{chosen_fastas_folder}\proteins_per_bacteria.txt", 'a') as proteins_per_bacteria_file:

        for organism_name in organisms:
            cur_organism_folder = f'{directory}\\{organism_name.replace("+", "_")}'
            organism_fasta_list = convert_file_to_list(directory, f"{organism_name}_completed_runs")

            fasta_peptides_count = {}

            all_raws_bacteria_peptides_dict = {}

            for raw_name in raw_list:
                # dict {fasta file name: pandas file of peptide}
                df_dictionary = fasta_pandas_df_dict(raw_name, organism_fasta_list, cur_organism_folder)

                # creates a dictionary of {fasta file name: peptide's array}
                peptides_dictionary = fasta_peptide_dict(raw_name, organism_fasta_list, cur_organism_folder)

                # dictionary: values are lists of proteins for each fasta file (key) (length = number of peptides found)
                bacteria_peptides_dict = fasta_bacteria_protein_dict(peptides_dictionary, df_dictionary,
                                                                       CONTAM_NOTATION)
                all_raws_bacteria_peptides_dict[raw_name] = bacteria_peptides_dict

                for fasta in bacteria_peptides_dict.keys():
                    if fasta in fasta_peptides_count:
                        fasta_peptides_count[fasta] += len(bacteria_peptides_dict[fasta])
                    else:
                        fasta_peptides_count[fasta] = len(bacteria_peptides_dict[fasta])

            proteome_length_dict = {}
            for fas in organism_fasta_list:
                proteome_length_dict[fas] = calculate_proteomes_sizes(cur_organism_folder, fas)

            # Sorting the dictionary by values in descending order
            sorted_dict_desc = dict(sorted(fasta_peptides_count.items(), key=lambda item: item[1], reverse=True))
            top_5_keys = list(sorted_dict_desc.keys())[:5]
            # Find the key with the highest value in proteome_length_dict among the top 5 keys
            if len(top_5_keys) == 1:
                chosen_proteome = top_5_keys[0]
            elif len(top_5_keys) == 0:
                print(f"{organism_name} is not found!")
                continue
            else:
                chosen_proteome = max(top_5_keys, key=proteome_length_dict.get)

            found_organism_proteins_names = set()
            for raw_name in raw_list:
                if chosen_proteome in all_raws_bacteria_peptides_dict[raw_name]:
                    found_organism_proteins_names.update(all_raws_bacteria_peptides_dict[raw_name][chosen_proteome])

            print(f"\n{organism_name}")
            # Display the results
            print("The proteome with the most found peptides in uniprot (proteome_length_dict) among the top 5 is:",
                  chosen_proteome,
                  "proteome length: ", proteome_length_dict[chosen_proteome])
            print("peptide count: ", fasta_peptides_count[chosen_proteome])
            organism_fasta_folder = rf"{chosen_fastas_folder}\{organism_name.replace('+', '_')}"

            if organism_name == "Negativicoccus+succinicivorans":
                for raw_name in raw_list:
                    msfragger_runner.delete_files(rf"{directory}\{organism_name.replace('+', '_')}\{chosen_proteome}\{raw_name}")

            shutil.copytree(rf"{directory}\{organism_name.replace('+', '_')}\{chosen_proteome}", organism_fasta_folder)

            list_of_organism_prot = copy_relevant_proteins(combined_proteome_file, chosen_proteome,
                                                           organism_fasta_folder, organism_name,
                                                           found_organism_proteins_names)
            found_proteins_names.update(found_organism_proteins_names)
            # adding name /n proteins names of current organism
            proteins_per_bacteria_file.write(f"*{organism_name.replace('+', '_')}\n")
            for name in list_of_organism_prot:
                proteins_per_bacteria_file.write(name + "\n")

    combined_proteome_file.close()
    proteins_per_bacteria_file.close()
