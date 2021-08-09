# Version 1, passed a1 sanity checker; Mechanisms Updated
from pathlib import Path



# When The CMD == 'L'
# When option is equal to "-f"
def file_only_Return(list_of_Paths):
    """
    【Purpose】Return a string containing the names of all files in a directory
    【Input】Path of the Directory
    【Output】a string containing the names of all files in this directory
    """
    OUTPUT = []
    for path in list_of_Paths:
        if path.is_dir():
            pass
        else:
            OUTPUT.append(path)
    return OUTPUT


# When option is equal to "-r"
def filename_Return(dir_path, show_all=False, ):
    """
    【Purpose】Return a list of all files in a directory including all subdirectories and its files
    【Input】Path of the Directory,Optional:show all folders
    【Output】a string containing the names of all files and folders
     """
    OUTPUT = []
    p = Path(dir_path)
    # Return all the NONE Dir first
    for object in p.iterdir():
        if object.is_dir():
            pass
        else:
            OUTPUT.append(object)
    # Now that all files in the destination are already returned
    for object in p.iterdir():
        if object.is_dir():
            sub_foo_path = str(object)
            OUTPUT.append(object)
            if show_all:
                OUTPUT += filename_Return(sub_foo_path)
        else:
            pass  # Already Returned

    return OUTPUT


# When option is equal to "-r" "-s"
def file_search_byName(file_name, list_of_Paths):
    """
    【Purpose】Search the directory by name Recursivelly
    【Input】all_object_names
    【Output】the directories of the files that matched the file_name
    """
    OUTPUT = []
    for path in list_of_Paths:
        if path.name == file_name:
            OUTPUT.append(path)
    return OUTPUT


# When option is equal to "-r" "-e"
def file_search_bySuffix(file_suffix, list_of_Paths):
    """
    【Purpose】Search the directory by Suffix Recursivelly
    【Input】all_object_names
    【Output】the directories of the files that matched the file_name
    """
    file_suffix = "." + file_suffix
    OUTPUT = []
    for path in list_of_Paths:
        try:
            if path.suffix == file_suffix:
                OUTPUT.append(path)
        except:
            pass

    return OUTPUT


#  When the CMD == "C"
# Create a file with name -n xxx
def file_add(dir_path, file_name):
    "Add a file at designated file path"
    file_name += '.gpk'
    p = Path(dir_path)
    f = p / file_name
    if not f.exists():
        w = f.open("w")
        w.close()
    return f


# When the CMD == "D"
# Delete a the file at designated file path
def file_delete(file_path):
    "Delete a file at designated file path"
    if file_path == "":
        return
    if file_path.split("\\")[-1].split(".")[-1] == "gpk":
        f = Path(file_path)
        Path.unlink(f)
        print(file_path + " DELETED")
        return
    else:
        file_path_revised = input("ERROR")
        file_delete(file_path_revised)
    # When the CMD == 'R':


# Read the file
def file_read(file_path):
    "Read a file"
    try:
        if file_path == "":
            return
        if file_path.split("\\")[-1].split(".")[-1] == "gpk":
            f = Path(file_path)
            r = f.open('r')
            LINES = r.readlines()
            if LINES == []:
                print("EMPTY")
            else:
                for line in LINES:
                    print(line.strip("\n"))
            r.close()
            return
        else:
            print("ERROR")
    except FileNotFoundError as fnfe:
        file_path_revised = input("ERROR")
        file_read(file_path_revised)

    # File Explore Shell


def File_Exp(entry=None, RETURN = False, input_mode = False):
    """
    This is a 'Shell' for the program which takes cmd inputs from the user and directs to corresponding functions
    :param entry: Cmd format: [COMMAND] [INPUT] [[-]OPTION] [INPUT]
    :param input_mode: by default, File_Exp takes in cmds without input.
    :return: None
    """
    Menu_script = '''
                  [Menu]
                  Cmd format: [COMMAND] [INPUT] [[-]OPTION] [INPUT]
                  - [Q]uit the program by [Q]
                  - [L]ook the file paths by [L]
                  - [C]reate new files by [C]
                  - [D]elete files by [D]
                  - [R]ead files by [R]
                  '''
    while True:
        if input_mode == True:
            entry = input()
        if entry == "Q":
            break
        try:
            entry = entry.split(" ")
            # Collect Cmd Info
            cmd = entry[0]
            INPUT1 = entry[1]
            INPUT2 = entry[-1]
            OPTION = []
            for item in entry:
                if item[0] == "-":
                    OPTION.append(item)
            PASS = True
        except:
            print("ERROR")
            print(Menu_script)
            PASS = False

        if PASS:
            try:
                # Functions
                if cmd == "L":
                    dir_path = INPUT1
                    file_path = entry[1]
                    list_of_Paths = result = filename_Return(dir_path)  # Default Mode
                    for opt in OPTION:
                        if opt == "-f":  # -f Output only files, excluding directories in the results.
                            list_of_Paths = result = file_only_Return(list_of_Paths)
                        elif opt == "-r":  # -r Output directory content recursively.
                            list_of_Paths = result = filename_Return(dir_path, show_all=True)
                        elif opt == "-s":  # -s Output only files that match a given file name.
                            file_name = INPUT2
                            result = file_search_byName(file_name, list_of_Paths)
                        elif opt == "-e":  # -e Output only files that match a give file extension.
                            file_suffix = INPUT2
                            result = file_search_bySuffix(file_suffix, list_of_Paths)
                        else:
                            PASS = False
                            print("ERROR")
                            break
                    if PASS:  # If opt does make sense
                        if RETURN:
                            return result # A list of paths
                        else:
                            for path in result:
                                print(path)  # Finally
                elif cmd == "C":
                    dir_path = INPUT1
                    opt = OPTION[0]
                    if opt == "-n":
                        file_name = INPUT2
                    file_path = file_add(dir_path, file_name)
                    if RETURN:
                        return file_path
                    else:
                        print (file_path)

                elif cmd == "D":
                    file_path = INPUT1
                    file_delete(file_path)
                elif cmd == "R":
                    file_path = INPUT1
                    file_read(file_path)
                else:
                    print(Menu_script)
            except Exception as ex :
                print("ERROR:\n",ex)

        # Finally
        if not input_mode:
            break

if __name__ == "__main__":
    File_Exp()
