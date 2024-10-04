import re
def make_dehidrals(molecules):
    """Generate a list of dihedral angles based on selected angles."""
    connections = []
    for molecule in molecules:
        monosaccharide = (re.split(r'\d\d', molecule))
        linkage = (re.findall(r'\d\d', molecule))[0]
        connections.append(f"{monosaccharide[0]} {linkage[0]} {linkage[1]} {monosaccharide[1]}")


    with open("Dihedrals/dihedrals.txt","r") as file:
        dihedrals = file.readlines()

    output =[]

    for connection in connections:
        for dihedral in dihedrals:
            if dihedral.count(",")<2 or dihedral[0] == "#":
                continue

            if connection == dihedral[:dihedral.index(",")]:
                output.append(dihedral.split(",")[:2])



    print(output)
    return output