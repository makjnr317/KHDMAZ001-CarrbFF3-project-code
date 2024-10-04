import re

class CarbUtils:
    """
    A utility class for parsing and processing carbohydrate sequences.
    """
    def __init__(self, casper_sequence):
        """
        Initializes the CarbUtils instance with a carbohydrate sequence.

        :param casper_sequence: The sequence of the carbohydrate in string format.
        """
        self.repeating_linkage = None
        self.casper_sequence = casper_sequence
        self.residues = []
        self.linkages = []

    def parse_sequence(self):
        """
        Parses the carbohydrate sequence to extract residues and linkages.
        If the sequence starts with "-", it denotes a repeating linkage.
        """
        self.residues = self.extract_monosaccharides(self.casper_sequence)
        self.linkages = re.findall(r'\d->\d', self.casper_sequence)

        if self.casper_sequence[0] == "-":
            repeating_linkage = self.casper_sequence[-3] + "->" + self.casper_sequence[2]
            self.linkages.append(repeating_linkage)

    def get_residues(self):
        return self.residues

    def get_linkages(self):
        return self.linkages

    def get_connections(self):
        """
        Generates and returns unique connections between residues based on linkages.

        :return: List of unique connections formatted as "residue1linkageresidue2".
        """
        connections = []
        for i, j, k in zip(self.residues, self.residues[1:], self.linkages):
            connections.append(i + k.replace("->", "") + j)
        return connections

    def extract_monosaccharides(self, input_string):
        """
        Extracts monosaccharide substrings from the input string.

        :param input_string: The carbohydrate sequence string.
        :return: List of monosaccharide substrings.
        """
        substrings = []
        if input_string[0] != "-":
            input_string = ")" + input_string + "("
        i = 0
        while i < len(input_string):
            if input_string[i] == ')' and '(' in input_string[i:]:
                start_index = i + 1
                end_index = input_string.find('(', start_index)
                if end_index != -1:
                    substrings.append(input_string[start_index:end_index])
                    i = end_index + 1
                else:
                    i += 1
            else:
                i += 1
        return substrings