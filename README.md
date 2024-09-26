Authors: Noa Lichtenstein and Yoav Knaanie

This program accepts bacterial names and mass spectrometry raw files to generate a proteome from the proteins identified in the given samples (mass spectrometry raw files).
It retrieves FASTA files of the relevant organisms from the UniProt website and utilizes FragPipe for processing.
If you download it from github you need to dowload this zip file:
https://drive.google.com/file/d/1CLGhmEn2Fy1XUQ3FfXVvktk5PV_ufetC/view?usp=sharing
Unzip it and move it to the folder which contains the folders python_program and resources.

requirements:
	python 3.9 or above.

directory folder contains:
	resources folder:
        fragpipe_files->(fragger.params, fragpipe.workflow, fragpipe-files.fp-manifest)
	python_program:
		Contains the Python script and the file requirements.txt
	fragpipe folder


before running the program:
	in the command line run the following commands:
		cd path_to_where_application_is_installed\python_program
		pip install -r requirements.txt


running parameters:
	directory: directory containing the folders "resources" and "fragpipe".
	format: "C:\path\to\where\application\is\installed"

	adding_to_existing_fasta: path to an existing fasta file that you wish to expand/"none" if you wish to create a new database.
	format: "C:\path\to\an\existing\fasta\current_proteome.fasta" / "none"

	human_fasta_file: path to an existing fasta file that contains human proteins/"none".
	format: "C:\path\to\an\existing\fasta\human_proteome.fasta" / "none"
	
	raw_files_directory: directory containing the raw files.
	format: "C:\path\to\raw\files\directory"
	
	raw_file_list: list of names of raw files you want to run.
	format: 'raw1','raw2','raw3'...

	organisms_list: list of organisms that you wish to add/build the proteome according to their proteins.
	format: "Actinomyces+naeslundii","Actinomyces+oris","Corynebacterium+amycolatum"...
 
	number_of_fastas_to_download: number of fastas that will be downloaded from each organism for checking fasta files validity from uniprot
	format: 20
	
	output_path: path to the output location, contains the new file name with .fasta postfix.
	format: "C:\path\to\output\directory\filename.fasta"

the input should be in the format:
directory adding_to_existing_fasta raw_files_directory raw_file_list organisms_list number_of_fastas_to_download output_path

input example:
python main.py "C:\path\to\where\application\is\installed" "none" "C:\path\to\an\existing\fasta\human_proteome.fasta" "C:\path\to\raw\files\directory" "raw_file1","raw_file2" "Actinomyces+naeslundii","Actinomyces+oris" 20 "C:\path\to\output\directory\filename.fasta"

output:
	The program creates the file: directory\resources\fasta\combined_proteome.fasta
