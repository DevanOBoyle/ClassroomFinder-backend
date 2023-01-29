# This is an EXTREMELY braindead script for getting the info copy/pasted
# from MyUCSC in classes_raw.txt into the format we want it in classes.csv

# classes_raw.txt: raw data. dont use this one
# classes.csv: this is the bad boy you want

def inline_classes():
    infile = open("classes_raw.txt", "r")
    outfile = open("classes_raw2.txt", "w")

    lines = infile.readlines()
    cleaned_lines = []

    for line in lines:
        clean_line = ""
        if line.split(" ")[-1] == "Enrolled\n":
            outfile.write("\n")
            continue
        if line == "Instructor:\n" or line == "Location:\n" or line == "Instruction Mode:\n" or line == "Add to Cart\n" or line == "Textbooks\n" or line == "Course Readers\n" or line == "In Person\n" or line == "Synchronous Online\n" or line == "Asynchronous Online\n" or line == "Hybrid\n":
            continue
        if line == "Day and Time:\n":
            outfile.write(line.rstrip("\n") + " ")
            continue
        outfile.write(line.rstrip("\n") + "|")

    infile.close()
    outfile.close()

def prune_classes():
    infile = open("classes_raw2.txt", "r")
    outfile = open("classes.csv", "w")

    lines = infile.readlines()

    for line in lines:
        try:
            fields = line.split("|")
            outfile.write("".join(fields[0].split("   ")[0].split(" ")[1:]) + ",")
            outfile.write(" ".join(fields[0].split("   ")[1].split(" ")[0:]) + ",")
            outfile.write(fields[1].split(" ")[2] + ",")
            outfile.write(f"\"{fields[2]}\",")
            outfile.write(" ".join(fields[3].split(" ")[1:]) + ",")
            outfile.write(fields[4][14:] + "\n" if len(fields[4]) > 15 else "TBD" + "\n")
        except Exception as ex:
           print(f"{ex} on {line}")

    infile.close()
    outfile.close()

inline_classes()
prune_classes()
