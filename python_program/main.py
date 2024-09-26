# authors: Noa Lichtenstein and Yoav Knaanie
import shutil
import time
import fasta_download
import top20
import download
import os
import sys

CONTAM_NOTATION = ['HUMAN', 'PIG', 'BOVIN', 'SHEEP', 'YEAST']
INPUT_NUMBER = 9


def change_raw_names(raw_list, directory):
    new_raw_list = []
    for i, raw in enumerate(raw_list):
        new_name = rf"{directory}\first_step\raw{i + 1}.raw"
        old_name = rf"{directory}\first_step\{raw}.raw"
        os.rename(old_name, new_name)
        new_raw_list.append(f"raw{i + 1}")
    return new_raw_list


def copy_file_to_folder(file_path, folder_path):
    try:
        # Construct the destination path
        destination_path = os.path.join(folder_path, os.path.basename(file_path))

        # copy the file
        shutil.copy(file_path, destination_path)
        return destination_path
    except OSError as e:
        print(f"ERROR: the file path {file_path} is invalid. Notice that each raw file name supposed to contain just"
              f"file name without a path to the folder and without .raw suffix!")
        delete_temp_folders()
        sys.exit(1)


def delete_temp_folders():
    shutil.rmtree(working_directory)
    shutil.rmtree(chosen_fastas_folder)

def rename_file(old_path, new_name):
    try:
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)

    except OSError as e:
        print(f"ERROR: Renaming the file {old_path} failed")
        delete_temp_folders()
        sys.exit(1)


def move_files(raw_list, existing_fasta, chosen_fastas_folder, human_fasta_path, working_directory, raw_directory, directory):
    # up until this point everything is the same
    if existing_fasta != "none":
        moved_fasta_path = copy_file_to_folder(existing_fasta, chosen_fastas_folder)
        # Rename the file in the new location to "combined_proteome.fasta"
        rename_file(moved_fasta_path, "combined_proteome.fasta")

        # for only, expanding the proteome it is not necessary.
        # shutil.copy(rf"{directory}\resources\fasta\proteins_per_bacteria.txt", chosen_fastas_folder)
    if human_fasta_path != "none":
        moved_fasta_path = copy_file_to_folder(human_fasta_path, chosen_fastas_folder)
        moved_path_first_step = copy_file_to_folder(human_fasta_path, working_directory)
        rename_file(moved_fasta_path, "human_proteome.fasta")
        rename_file(moved_path_first_step, "human_proteome.fasta")

    # moving raw files to first step directory validate the raw files names
    for raw_file in raw_list:
        copy_file_to_folder(rf"{raw_directory}\{raw_file}.raw", working_directory)
    return change_raw_names(raw_list, directory)


def create_folder(directory):
    try:
        os.mkdir(directory)
    except OSError as e:
        print(f"Error creating folder: {str(e)}")


def delete_all_in_folder(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        print(item_path)
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
                print(f"Deleted file: {item_path}")
            except OSError as e:
                print(f"Error: {str(e)}")
        elif os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
                print(f"Deleted directory: {item_path}")
            except OSError as e:
                print(f"Error: {str(e)}")


def move_unified_proteome_to_destenation(chosen_fastas_folder, output_path):
    shutil.copy(rf"{chosen_fastas_folder}\combined_proteome.fasta", output_path)
    try:
        os.remove(rf"{chosen_fastas_folder}\combined_proteome.fasta")
    except PermissionError as e:
        print(f"ERROR: Unable to remove {chosen_fastas_folder}\combined_proteome.fasta {str(e)}")
        delete_temp_folders()
        sys.exit(1)
    try:
        shutil.rmtree(chosen_fastas_folder)
    except PermissionError as e:
        print(f"ERROR: Unable to remove {chosen_fastas_folder} {str(e)}")
        delete_temp_folders()
        sys.exit(1)


def delete_unnecessary_files(working_directory):
    # After finishing all operations
    delete_all_in_folder(working_directory)
    try:
        shutil.rmtree(working_directory)
    except PermissionError as e:
        print(f"ERROR: Unable to remove directory {working_directory}. {str(e)}")
        sys.exit(1)


def handle_input():
    if len(sys.argv) != INPUT_NUMBER:
        sys.exit(
            "Invalid input. the input should be in the format: directory existing_fasta_path human_fasta_directory "
            "raw_files_directory raw_file_list(format: 'raw1','raw2','raw3'...) "
            "organisms_list(format example: 'Actinomyces+naeslundii','Actinomyces+oris','Corynebacterium+amycolatum'..."
            " number_of_fastas_to_download output_path\n"
            "existing_fasta_path and human_fasta_directory can be 'none'")
    directory = sys.argv[1]
    fragpipe_directory = rf"{directory}\fragpipe"  # The folder in which the fragpipe was installed
    existing_fasta = sys.argv[2]
    human_fasta_path = sys.argv[3]
    raw_directory = sys.argv[4]
    raw_list = sys.argv[5].split(',')
    organisms = sys.argv[6].replace("'", "").split(',')
    number_of_fastas_download = int(sys.argv[7])  # number of fasta files to download from Uniprot
    output_path = sys.argv[8]

    if number_of_fastas_download < 1:
        print("ERROR: number_of_fastas_to_download supposed to be a positive integer!")
        sys.exit(1)

    print(f"raw_list == {raw_list}")
    print(f"organisms == {organisms}")
    return directory, fragpipe_directory, existing_fasta, human_fasta_path, raw_directory, raw_list, organisms, number_of_fastas_download, output_path


if __name__ == '__main__':
    """
    directory: should contain: resources/fragpipe_files->(fragger.params, fragpipe.workflow, fragpipe-files.fp-manifest)    
    creates chosen_fastas folder in directory containing the unified proteome
    creates first_step
    """
    (directory, fragpipe_directory, existing_fasta, human_fasta_path, raw_directory,
     raw_list, organisms, number_of_fastas_download, output_path) = handle_input()
    # create working directory, chosen_fastas_folder
    working_directory = rf"{directory}\first_step"
    create_folder(working_directory)
    chosen_fastas_folder = rf'{directory}\chosen_fastas'

    if not os.path.isdir(chosen_fastas_folder):
        create_folder(chosen_fastas_folder)

    raw_list = move_files(raw_list, existing_fasta, chosen_fastas_folder, human_fasta_path, working_directory,
                          raw_directory, directory)

    start_time = time.time()
    # download only if there is no already a folder
    download.download_organisms_main(fragpipe_directory, directory, raw_list, organisms, working_directory,
                                     number_of_fastas_download)
    end_time = time.time()
    running_time = end_time - start_time
    print(f"download running time: {running_time} seconds")

    # main function -----------------------------------------
    # shutil.copy(rf"{directory}\resources\fasta\Human_Top_100.fasta", chosen_fastas_folder) # should delete?
    top20.top20_main_function(raw_list=raw_list, organisms=organisms, directory=working_directory,
                              chosen_fastas_folder=chosen_fastas_folder)
    move_unified_proteome_to_destenation(chosen_fastas_folder, output_path)
    delete_unnecessary_files(working_directory)







    # input examples:
    # directory = r"C:\Users\owner\Microbiome\Building_a_Unified_Proteome"
    # raw_list = [
    #     "2022_05_25_09_PreNatal3_Sample1_S1_SCX_p2",
    #     "2022_05_25_07_PreNatal3_Sample2_S1_SCX_p2",
    #     "2022_05_25_05_PreNatal3_Sample3_S1_SCX_p2",
    #     "2022_05_25_03_PreNatal3_Sample4_S1_SCX_p2",
    #     "2022_05_25_01_PreNatal3_Sample5_S1_SCX_p2",
    #     "2021_12_10_11_PreNatal2_Sample2_S1_p2",
    #     "2021_12_10_13_PreNatal2_Sample3_S1_p2",
    #     "2021_12_10_07_PreNatal1_Sample1_S1_p2",
    #     "2021_12_10_09_PreNatal1_Sample2_S1_p2",
    #     "2021_12_10_01_PreNatal1_Sample3_S1_p2",
    #     "2021_12_10_02_PreNatal2_Sample1_S1_p2"
    # ]
    # organisms = [
    #     'Actinomyces+naeslundii',
    #     'Actinomyces+oris',
    #     'Corynebacterium+amycolatum',
    #     'Corynebacterium+striatum',
    #     'Dermabacter+hominis',
    #     'Rothia+mucilaginosa',
    #     'Cutibacterium+avidum',
    #     'Gemella+haemolysans',
    #     'Staphylococcus+epidermidis',
    #     'Staphylococcus+hominis',
    #     'Enterococcus+faecalis',
    #     'Lactobacillus+rhamnosus',
    #     'Streptococcus+infantis',
    #     'Streptococcus+salivarius',
    #     'Clostridium+perfringens',
    #     'Negativicoccus+succinicivorans',
    #     'Veillonella+atypica',
    #     'Veillonella+parvula',
    #     'Finegoldia+magna',
    #     'Citrobacter+braakii',
    #     'Citrobacter+youngae',
    #     'Enterobacter+cloacae_complex',
    #     'Escherichia+coli',
    #     'Klebsiella+aerogenes',
    #     'Klebsiella+michiganensis',
    #     'Klebsiella+oxytoca',
    #     'Klebsiella+pneumoniae',
    #     'Kluyvera+ascorbata',
    #     'Proteus+mirabilis'
    # ]
