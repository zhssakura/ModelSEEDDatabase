#!/usr/bin/env python
import os, sys
from difflib import Differ

sys.path.append('../../Libs/Python')
from BiochemPy import Compounds #, Reactions

DifferObj=Differ()

#Load Compounds
CompoundsHelper = Compounds()
Compounds_Dict = CompoundsHelper.loadCompounds()

#Load Curated Structures
Ignored_Structures=dict()
with open("../../Biochemistry/Structures/Curation/Ignore_Structures.txt") as ignore_file:
    for line in ignore_file.readlines():
        array=line.split('\t')
        Ignored_Structures[array[0]]=1
ignore_file.close()

#Load Structures and Aliases
Structures_Dict = CompoundsHelper.loadStructures(["SMILE","InChIKey","InChI"],["KEGG","MetaCyc"])
MS_Aliases_Dict =  CompoundsHelper.loadMSAliases(["KEGG","MetaCyc"])


unique_structs_file = open("../../Biochemistry/Structures/Unique_ModelSEED_Structures.txt",'w')
master_structs_file = open("../../Biochemistry/Structures/All_ModelSEED_Structures.txt",'w')
inchi_conflicts_file = open("InChI_Conflicts.txt",'w')
smile_conflicts_file = open("SMILE_Conflicts.txt",'w')
unique_structs_file.write("ID\tType\tAliases\tStructure\n")
for msid in sorted(MS_Aliases_Dict.keys()):

    #Build collection of all structures for the ModelSEED ID
    Structs = dict()
    for source in 'KEGG','MetaCyc':
        if(source not in MS_Aliases_Dict[msid].keys()):
            continue

        for struct_type in sorted(Structures_Dict.keys()):
            for external_id in sorted(MS_Aliases_Dict[msid][source]):
                if(external_id not in Structures_Dict[struct_type]):
                    continue

                for struct_stage in sorted(Structures_Dict[struct_type][external_id].keys()):
                    if(struct_type not in Structs):
                        Structs[struct_type]=dict()

                    if(struct_stage not in Structs[struct_type]):
                        Structs[struct_type][struct_stage]=dict()

                    for structure in sorted(Structures_Dict[struct_type][external_id][struct_stage].keys()):
                            
                        #Write to master
                        master_structs_file.write("\t".join([msid,struct_type,struct_stage,external_id,source,structure])+"\n")    

                        if(external_id in Ignored_Structures):
                            continue

                        if(structure not in Structs[struct_type][struct_stage]):
                            Structs[struct_type][struct_stage][structure]=dict()

                        Structs[struct_type][struct_stage][structure][external_id]=source

    if(len(Structs.keys())==0):
        continue
                        
    ms_structure = "null"
    ms_structure_type = "null"
    ms_external_ids = list()

    if("SMILE" in Structs):
        if("Charged" in Structs["SMILE"]):
            if(len(Structs["SMILE"]["Charged"])==1):
                structure = list(Structs["SMILE"]["Charged"].keys())[0]
                ms_structure = structure
                ms_structure_type = "SMILE"
                ms_external_ids = Structs["SMILE"]["Charged"][structure].keys()
            else:
                for structure in Structs["SMILE"]["Charged"]:
                    for external_id in Structs["SMILE"]["Charged"][structure]:
                        smile_conflicts_file.write(msid+"\tCharged\t"+external_id+"\t"+structure+"\t"+Structs["SMILE"]["Charged"][structure][external_id]+"\n")
                pass

        elif("Original" in Structs["SMILE"]):
            if(len(Structs["SMILE"]["Original"])==1):
                structure = list(Structs["SMILE"]["Original"].keys())[0]
                ms_structure = structure
                ms_structure_type = "SMILE"
                ms_external_ids = Structs["SMILE"]["Original"][structure].keys()
            else:
                #Establish rules for checking/curating SMILE strings
                for structure in Structs["SMILE"]["Original"]:
                    for external_id in Structs["SMILE"]["Original"][structure]:
                        smile_conflicts_file.write(msid+"\tOriginal\t"+external_id+"\t"+structure+"\t"+Structs["SMILE"]["Original"][structure][external_id]+"\n")
                pass
    else:
        pass

    if(ms_structure != "null"):
        unique_structs_file.write("\t".join([msid,ms_structure_type,";".join(sorted(ms_external_ids)),ms_structure])+"\n")
    else:
        #There are possible problems that arise where we can't find a unique SMILE structure, but we can find a unique InChI structure
        #I don't yet know why, but I've a feeling it's to do with how some valences are assigned within a MOL file which
        #is normalized using InChI as a standard, but breaks down when generating SMILE strings
        #A good example is Protoheme: cpd00028
        pass

    ms_structure="null"
    if("InChIKey" in Structs):

        #Default to structures charged by MarvinBeans
        if("Charged" in Structs["InChIKey"]):

            if(len(Structs["InChIKey"]["Charged"])==1):
                structure = list(Structs["InChIKey"]["Charged"].keys())[0]
                ms_structure = structure
                ms_structure_type = "InChIKey"
                ms_external_ids = Structs["InChIKey"]["Charged"][structure].keys()
            else:
                #Establish rules for checking/curating InChIKey strings
                pass

        elif("Original" in Structs["InChIKey"]):
            if(len(Structs["InChIKey"]["Original"])==1):
                structure = list(Structs["InChIKey"]["Original"].keys())[0]
                ms_structure = structure
                ms_structure_type = "InChIKey"
                ms_external_ids = Structs["InChIKey"]["Original"][structure].keys()
            else:
                #Establish rules for checking/curating InChIKey strings
                pass

    if(ms_structure != "null"):
        unique_structs_file.write("\t".join([msid,ms_structure_type,";".join(sorted(ms_external_ids)),ms_structure])+"\n")

    ms_structure="null"
    if("InChI" in Structs):

        #Default to structures charged by MarvinBeans
        if("Charged" in Structs["InChI"]):

            if(len(Structs["InChI"]["Charged"])==1):
                structure = list(Structs["InChI"]["Charged"].keys())[0]
                ms_structure = structure
                ms_structure_type = "InChI"
                ms_external_ids = Structs["InChI"]["Charged"][structure].keys()
            elif(len(Structs["InChI"]["Charged"])>1):
#                structures = list(Structs["InChI"]["Charged"].keys())
#                result = DifferObj.compare(structures[0], structures[1])
#                sys.stdout.writelines(result)

                for structure in Structs["InChI"]["Charged"]:
                    for external_id in Structs["InChI"]["Charged"][structure]:
                        inchi_conflicts_file.write(msid+"\tCharged\t"+external_id+"\t"+structure+"\t"+Structs["InChI"]["Charged"][structure][external_id]+"\n")
                pass

        elif("Original" in Structs["InChI"]):
            if(len(Structs["InChI"]["Original"])==1):
                structure = list(Structs["InChI"]["Original"].keys())[0]
                ms_structure = structure
                ms_structure_type = "InChI"
                ms_external_ids = Structs["InChI"]["Original"][structure].keys()
            else:
                for structure in Structs["InChI"]["Original"]:
                    for external_id in Structs["InChI"]["Original"][structure]:
                        inchi_conflicts_file.write(msid+"\tOriginal\t"+external_id+"\t"+structure+"\t"+Structs["InChI"]["Original"][structure][external_id]+"\n")
                pass

    if(ms_structure != "null"):
        unique_structs_file.write("\t".join([msid,ms_structure_type,";".join(sorted(ms_external_ids)),ms_structure])+"\n")

master_structs_file.close()
unique_structs_file.close()
inchi_conflicts_file.close()
smile_conflicts_file.close()
