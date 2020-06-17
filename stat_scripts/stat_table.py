f = open("a")
table_dict = {"ACTI":{"total":0}, "ANAT":{"total":0}, "CHED":{"total":0}, "CONC": {"total":0}, "DEVI": {"total":0}, "DISO":{"total":0}, "GENE":{"total":0}, "GEOG":{"total":0},
              "LIVB":{"total":0}, "OBJC": {"total":0}, "OCCU":{"total":0}, "ORGA":{"total":0}, "PHEN":{"total":0}, "PHYS":{"total":0}, "PROC":{"total":0}, "UnknownType":{"total":0},
              "disease":{"total":0}, "body_location": {"total":0}, "severity": {"total":0}, "symptom": {"total":0},
              "treatment":{"total":0}, "drug":{"total":0}, "course":{"total":0}, "modificator":{"total":0}}

for line in f:
    if line != "\n":
        if line.split(" ")[1] != "O":
            tag = line.split(" ")[2].split("-")[1]
            table_dict[tag]["total"] +=1
            if line.split(" ")[2][:-1] != "O":
                pred = line.split(" ")[1].split("-")[1]
            else:
                pred = "O"
            if pred in table_dict[tag]:
                table_dict[tag][pred] += 1
            else:
                table_dict[tag][pred] = 1

for key in table_dict:
    #for k in table_dict[key]:
     #   if k != "total":
      #      table_dict[key][k] = table_dict[key][k]/table_dict[key]["total"]
    print("{} {}".format(key,table_dict[key]))
