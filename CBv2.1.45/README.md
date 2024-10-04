CarbBuilder is a program for building a reasonable structure of a polysaccharide from a primary structure specification in the CASPER format.  

CarbBuilder is implemented in C# and should be portable across a variety of architectures with support for the .NET framework.

If you use CarbBuilder in your research, please cite this reference:  
M. M. Kuttel, Jonas Stahle, and Goran Widmalm, J. Comput. Chem., J. Comput. Chem., 37(22), 2098-2105 (2016)
M. M. Kuttel et al., Proceedings of the 7th IEEE International Conference on e-Science, 2011, p 395-402, (2016)

==============================================
INSTALLATION

CarbBuiler is installed by downloading and expanding the archive, which contains:
+ CarbBuilder2.exe [the application file]
+ README.md [this README file]
+ structureFile directory [a directory containing structures for building and default settings]

Execution of CarbBuilder on Linux or MacOS X requires installation of Mono, an open source implementation of Microsoft's .NET Framework (http://www.mono-project.com/).
Mono is free for download at http://www.mono-project.com/download/.
==============================================
EXECUTION

Examples of how to run CarbBuilder:

On Windows:  
CarbBuilder2.exe  -i  "->2)aLRha(1->2)aLRha(1->3)aLRha(1->3)bDGlcNAc(1->" -r 6 -o Shigella_Y_RU6

Linux [Note that running under Linux requires installation of the mono framework] :   
mono  CarbBuilder2.exe  -i  "->2)aLRha(1->2)aLRha(1->3)aLRha(1->3)bDGlcNAc(1->" -r 6 -o Shigella_Y_RU6

MacOS  [Note that running under MacOS requires installation of the mono framework]:
mono CarbBuilder2.exe  -i  "->2)aLRha(1->2)aLRha(1->3)aLRha(1->3)bDGlcNAc(1->" -r 6 -o Shigella_Y_RU6

==============================================
COMMAND-LINE ARGUMENTS

The '-i' command line argument is used to specify the primary sequence information in CASPER format.


Possible command line arguments are:

-i [CASPER_sequence]
    (REQUIRED)  
Specify the primary sequence for the carbohydrate in CASPER format

-r [number_of_repeating_units]
    (Optional)
Specify number of repeating units to be built of the primary sequence. This will be ignored if the CASPER notation for a repeating unit is not provided. Example: ->4)aDGlc(->1

-o [outputfile_name]
Write the pdb output to outputfile_name

-d [dihedral_file_name]
User-specified dihedral values for specific linkages.
These must be in this format:
[Res1] 1 [link position] [Res2],2,[phiVal] [psiVal],[altPhiVal1] [altPsiVal1],[altPhiVal2] [altPsiVal2]
e.g:
aDGlc 1 2 aDGlc,2,-26 -36,-39 169,-26 41,-151 24

-all
Generate all possible CarbBuilder structures (i.e. all possible combinations of the dihedral angle alternatives) for a carbohydrate sequence as frames in a single pdb file.  This will be truncated if the number of structures is > 4000. 

-h 
Display this help information


==============================================
CASPER Format examples:

1. Linear: aDGlc(1->4)aDGlc

2. Branched: aDMan(1->4)[aDGal(1->6)]aDGlc

3. Repeating ->6)aDMan(1-4)aDGlc(1->

4. Residue with substituents: aDGlc3Ac4Me

5. Phosphate linkage: aDMan1P(O->6)aDMan   

6. Linkage from the 2-postion: aDNeu5Ac(2->6)aDGlc

=================================================

More examples of how to run CarbBuilder follow.

1. To build a complex, non-repeating N-mannan:

CarbBuilder2.exe  -i  "aDMan(1->6)[aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->3)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->3)[aDMan(1->6)]aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->3)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)aDMan(1->3)[aDMan(1->6)]aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)aDMan(1->3)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)bDMan(1->2)aDMan(1->3)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[bDMan(1->2)bDMan(1->2)bDMan(1->2)bDMan(1->2)aDMan(1->2)aDMan(1->2)aDMan(1->2)]aDMan(1->6)[aDMan(1->2)[bDMan(1->2)bDMan(1->2)bDMan(1->2)aDMan1P(O->6)]aDMan(1->2)aDMan(1->2)]aDMan"  -o NMannan

2. To build 6 RU of meningococcal Y polysaccharide from the 2 residue repeating unit:

../CarbBuilder2.exe  -i  "->6)aDGlc(1->4)aDNeu5Ac(2->" -r 6 -o MenY_6rep



------------------------------------------------------

If you have any questions or suggestions, please email Michelle Kuttel at mkuttel@cs.uct.ac.za

