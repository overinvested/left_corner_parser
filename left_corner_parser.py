from copy import deepcopy
from nltk import Tree


grammar = {
            'S': ['NP VP', 'Aux NP VP', 'VP'],
            'NP': ['Pro', 'Prop', 'Det Nom'],
            'Nom': ['N', 'N PP'], #['N', 'Nom N', 'Nom PP'],
            'VP': ['V', 'V NP', 'V NP PP', 'V PP'], #['V', 'V NP', 'V NP PP', 'V PP', 'VP PP'],
            'PP': ['Prep NP'],
            'Det': ['that', 'this', 'the', 'a', 'my'],
            'N': ['book', 'flight', 'meal', 'money', 'pajamas', 'elephant', 'shot', 'can'],
            'V': ['book', 'include', 'prefer', 'shot', 'can', 'sing', 'died'],
            'Pro': ['I', 'she', 'me', 'he'],
            'Prop': ['Mary', 'Vincent', 'Houston', 'NWA'],
            'Aux': ['does', 'can'],
            'Prep': ['from', 'to', 'on', 'near', 'through', 'in']
            }

left_corner_table = {}
            # expected table
            # {
            # 'S': ['NP', 'Aux', 'VP'],
            # 'NP': ['Pro', 'Prop', 'Det'],
            # 'Nom': ['N'],
            # 'VP': ['V'],
            # 'PP': ['Prep'],
            # 'Det': ['that', 'this', 'the', 'a', 'my'],
            # 'N': ['book', 'flight', 'meal', 'money', 'pajamas', 'elephant', 'shot', 'can'],
            # 'V': ['book', 'include', 'prefer', 'shot', 'can', 'sing', 'died'],
            # 'Pro': ['I', 'she', 'me', 'he'],
            # 'Prop': ['Mary', 'Vincent', 'Houston', 'NWA'],
            # 'Aux': ['does', 'can'],
            # 'Prep': ['from', 'to', 'on', 'near', 'through', 'in']
            # }



sentence1 = 'can she book the flight through Houston'
sentence2 = 'I shot the elephant in my pajamas'
sentence3 = 'can Mary sing'
sentence4 = 'Vincent died'


def main():
    generate_left_corner_table(left_corner_table)
    parse(sentence1)
    parse(sentence2)
    parse(sentence3)
    parse(sentence4)


def generate_left_corner_table(table: dict) -> dict:
    """
    generate_left_corner_table\n
    Populates the left corner table by isolating the left-most symbols in each rule
    @param {dict} table: the table to be populated
    @return {dict} table: the populated table
    """
    for lhs in grammar:
        left_corners = []
        for rhs in grammar[lhs]:
            symbols = rhs.split()
            if not symbols[0] in left_corners:
                left_corners.append(symbols[0])
        table[lhs] = left_corners
    
    return table


def get_left_corner_rules(word: str) -> list:
    """
    get_left_corner_rules\n
    Gets all rules with a given word as their left corner
    @param {str} word: the word that should be the left corner of the rules
    @return {list} rules: all of the rules with word as their left corner
    """
    rules = []
    for lhs in grammar:
        for rhs in grammar[lhs]:
            symbols = rhs.split()
            if symbols[0] == word:
                rules.append([lhs, rhs])
          
    return rules


def possible_actions(sentence: list, categories: list, constituents: list) -> list:
    """
    possible_actions\n
    Finds all possible actions in a given state
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @return {list} actions: the possible actions in the current state
    """
    actions = []
    if not sentence == [] and not categories == [] and not categories[0] == '$':
        left_corner_rules = get_left_corner_rules(sentence[0])
        if left_corner_rules:
            for lc in left_corner_rules:
                if is_left_corner_reachable(lc[0], categories[0]):
                    actions.append(['reduce', lc])
    
    if not categories == [] and categories[0] == '$' and constituents is not []:
        actions.append('move')
    
    if not sentence == [] and not categories == []:
        if sentence[0] == categories[0]:
            actions.append('remove')
    
    return actions


def result(action: str or list, sentence: list, categories: list, constituents: list, structure: list) -> tuple[list, list, list, list]:
    """
    result\n
    Takes a state-action pair and produces the resultant state
    @param {str or list} action: the action to be performed
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @param {list} structure: the current partial structure of the parse tree
    @return {tuple[list, list, list, list]} (sentence, categories, constituents, structure): the contents of the resultant state
    """
    if action == 'remove':
        sentence, categories, constituents, structure = remove(sentence, categories, constituents, structure)
    if action == 'move':
        sentence, categories, constituents = move(sentence, categories, constituents)
    if type(action) == list:
        sentence, categories, constituents, structure = reduce(sentence, categories, constituents, structure, action[1])
    
    return sentence, categories, constituents, structure


def reduce(sentence: list, categories: list, constituents: list, structure: list, rule: list) -> tuple[list, list, list, list]:
    """
    reduce\n
    Uses a rule to reduce a word or category into the starting symbol of the grammar
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @param {list} structure: the current partial structure of the parse tree
    @param {list} rule: the rule we are using to reduce
    @return {tuple[list, list, list, list]} (sentence, categories, constituents, structure): the contents of the resultant state
    """
    lc = sentence.pop(0)
    if not ' ' in rule[1]:
        categories = ['$'] + categories
    else:
        categories = [x for x in rule[1].split()[1:]] + ['$'] + categories
    constituents = [rule[0]] + constituents

    lhs = rule[0]
    
    structure = structure_after_reduction(lhs, lc, structure)

    return sentence, categories, constituents, structure


def move(sentence: list, categories: list, constituents: list) -> tuple[list, list, list]:
    """
    move\n
    Moves a constituent into the sentence for further reduction
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @return {tuple[list, list, list]} (sentence, categories, constituents): the contents of the resultant state
    """
    sentence = [constituents.pop(0)] + sentence
    categories.pop(0)
    
    return sentence, categories, constituents


def remove(sentence: list, categories: list, constituents: list,  structure: list) -> tuple[list, list, list, list]:
    """
    remove\n
    Matches a predicted category with one that was recognized
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @param {list} structure: the current partial structure of the parse tree
    @return {tuple[list, list, list, list]} (sentence, categories, constituents, structure): the contents of the resultant state
    """
    structure = structure_after_removal(constituents, structure)
    sentence.pop(0)
    categories.pop(0)

    return sentence, categories, constituents, structure


def structure_after_reduction(lhs: str, left_corner: str, structure: list) -> list:
    """
    structure_after_reduction\n
    Modifies the structure when a reduction is performed
    @param {str} lhs: the lefthand side of a rule used for reduction
    @param {str} left_corner: the symbol at the left corner of the rule
    @param {list} structure: the current partial structure of the parse tree
    @return {list} structure: the modified partial structure of the parse tree
    """
    if structure == []:
        structure = [[lhs, [left_corner]] + structure]
    elif not structure[0][0] == left_corner:
        new_constituent = [lhs, [left_corner]]
        structure.insert(0, new_constituent)
    else:
        child = structure.pop(0)
        new_constituent = [lhs, child]
        structure.insert(0, new_constituent)
    
    return structure


def structure_after_removal(constituents: list, structure: list) -> list:
    """
    structure_after_removal\n
    Modifies the structure when a removal is performed
    @param {list} constituents: the categories we have successfully matched
    @param {list} structure: the current partial structure of the parse tree
    @return {list} structure: the modified partial structure of the parse tree
    """
    if constituents == []:
        return structure

    if len(structure) > 1:
        child = structure.pop(0)
        parent = structure.pop(0)
        if type(child) == str:
            child = [child]
        if type(parent) == str:
            parent = [parent]
        parent.append(child)
        structure.insert(0, parent)
    
    return structure


def is_left_corner_reachable(word: str, category: str) -> bool:
    """
    is_left_corner_reachable\n
    Determines whether a word can be reached using only left corners starting from an initial symbol
    @param {str} word: the word we want to recognize
    @param {str} category: the initial symbol
    @return {bool} is_left_corner_reachable: True or False
    """
    if category not in left_corner_table:
        return False
    if word in left_corner_table[category] or word == category:
        return True
    for sub_category in left_corner_table[category]:
        if is_left_corner_reachable(word, sub_category):
            return True


def parse(sentence: str):
    """
    parse\n
    A wrapper method for left-corner parsing, initializes state
    @param {str} sentence: the sentence we want to parse
    """
    sentence = sentence.split()
    left_corner_parse(sentence, ['S'], [], [])


def left_corner_parse(sentence: list, categories: list, constituents: list, structure: list) -> bool:
    """
    left_corner_parse\n
    Backtracking implementation of a left-corner parse
    @param {list} sentence: the input symbols yet to be processed
    @param {list} categories: the categories we predict we will see/are trying to match
    @param {list} constituents: the categories we have successfully matched
    @param {list} structure: the current partial structure of the parse tree
    @return {bool} left_corner_parse: the parse was or was not successful
    """
    if sentence == categories == constituents == []:
        structure = structure[0]
        # nltk Tree structure for readable representation
        test = Tree.fromlist(structure)
        test.pretty_print()
        return True

    actions = possible_actions(sentence, categories, constituents)
    derivations = []
    if actions:
        for action in actions:
            derivations.append(result(action, deepcopy(sentence), deepcopy(categories), deepcopy(constituents), deepcopy(structure)))
    if derivations:
        for d in derivations:
            sentence, categories, constituents, structure = d
            left_corner_parse(sentence, categories, constituents, structure)

    return False


if __name__ == '__main__':
    main()