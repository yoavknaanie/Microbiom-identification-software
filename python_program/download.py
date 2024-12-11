import fasta_download
import msfragger_runner
import os
import shutil


def multiple_run_msfragger_runner(fragpipe_directory, directory, all_proteomes_folder, proteomes_fasta_list, raw_name, organism_name):
    """
        return list of folder names of all completed runs
    """
    completed_analysis = []
    #  raw_folder, fasta_folder, work_folder, fasta_file, raw_file = inputs
    counter = 0
    with open(rf"{all_proteomes_folder}\{organism_name}_completed_runs.txt", 'w') as file:
        for prot in proteomes_fasta_list:
            fasta_folder = rf'{all_proteomes_folder}\{organism_name.replace("+", "_")}\{prot}'
            # folder with the name of the fasta
            work_folder = rf'{all_proteomes_folder}\{organism_name.replace("+", "_")}\{prot}\{raw_name}'
            check_work_folder = os.listdir(work_folder)
            if not check_work_folder:
                msfragger_runner.run_process(
                    [fragpipe_directory, directory, all_proteomes_folder, fasta_folder, work_folder, rf'{prot}.fasta', raw_name])
                # fragpipe_directory, raw_folder, fasta_folder, work_folder, fasta_file, raw_file = inputs
                counter += 1
            completed_analysis.append(prot)
            file.write(f"{prot}\n")
            print(f"-----------------------------------finished {counter} runs----------------------------------------")

    file.close()
    return completed_analysis


def create_raw_folder(directory_path, raw_name):
    try:
        os.makedirs(rf"{directory_path}\{raw_name}")
    except OSError as e:
        print(f"Error creating folder: {str(e)}")


def convert_list_to_file(folder, organism_name, fasta_list):
    with open(fr"{folder}\{organism_name}.txt", 'w') as file:
        for prot in fasta_list:
            file.write(f"{prot}\n")
        file.close()


def convert_file_to_list(folder, organism_name):
    fasta_list = []
    with open(rf"{folder}\{organism_name}.txt", 'r') as file:
        line = file.readline()

        while line:
            fasta_list.append(line.strip())
            line = file.readline()

        file.close()
    return fasta_list


def create_fasta_folder_from_propeties(all_proteomes_folder, organism_name):
    # to convert file_path to a fasta file names file
    path = fr'{all_proteomes_folder}\{organism_name}_properties.txt'
    fasta_list = []
    with open(f"{path}", 'r') as file:
        line = file.readline()

        while line:
            fasta_list.append(line.strip().split("\"")[6][:-1])
            line = file.readline()

        file.close()

    with open(fr"{all_proteomes_folder}\{organism_name}.txt", 'w') as file:
        for prot in fasta_list:
            file.write(f"{prot}\n")
        file.close()


def combine_human_and_bacteria(first_step, proteomes_fasta_list, organism_name):
    for prot in proteomes_fasta_list:
        new_folder_name = rf"{first_step}\{organism_name.replace('+','_')}\{prot}"
        with open(fr"{new_folder_name}\{prot}.fasta", 'a') as new_file, open(
                fr"{first_step}\human_proteome.fasta", 'r') as human:
            to_copy = human.read()
            new_file.write(to_copy)
        new_file.close()
        human.close()


def combine_human_and_bacteria_and_move_fastas(old_proteomes_folder, first_step, proteomes_fasta_list):
    for prot in proteomes_fasta_list:
        new_folder_name = fr"{first_step}\{prot}"
        os.makedirs(new_folder_name)
        shutil.copy(fr"{old_proteomes_folder}\{prot}\{prot}.fasta", rf"{new_folder_name}\{prot}.fasta")
        with open(fr"{new_folder_name}\{prot}.fasta", 'a') as new_file, open(
                fr"{first_step}\human_proteome.fasta", 'r') as human:
            to_copy = human.read()
            new_file.write(to_copy)
        new_file.close()
        human.close()


def download_organisms_main(fragpipe_directory, directory, raw_list, organisms, first_step, number_of_fastas_download):
    """
    creates: organism folder -> fasta file folder -> raw folder -> results

    res folder should contain the raw files
    """
    for organism_name in organisms:
        cur_organism_folder = rf'{first_step}\{organism_name.replace("+", "_")}'
        # Checks if the folder already exists
        if os.path.exists(cur_organism_folder):
            print(f"{organism_name} directory already exist")
            continue
        else:
            os.makedirs(cur_organism_folder)
            proteomes_fasta_list = fasta_download.download_all_fastas_of_organism_random(organism_name,
                                                                                         cur_organism_folder,
                                                                                         number_of_fastas_download)
            combine_human_and_bacteria(first_step, proteomes_fasta_list, organism_name)

            # creating raw folders in fasta folder for each raw file
            for proteome in proteomes_fasta_list:
                for raw_name in raw_list:
                    create_raw_folder(rf'{cur_organism_folder}\{proteome}', raw_name)

        # running of raw_list in each fasta folder
        for raw_name in raw_list:
            completed_analysis = multiple_run_msfragger_runner(fragpipe_directory, directory, first_step, proteomes_fasta_list,
                                                raw_name, organism_name)

            print(completed_analysis)




