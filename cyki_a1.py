'''CYK Algorithm. Determine wheter a string is in the set L(G),
where G is a ctext-free grammar.
obs: G must be in Chomskys Normal Form
obs2: input grammar must be inverted, i.e. DERIVATION --> SYMBOL. Also, a dictionary.
obs3: start symbol must be S
Igor de C e S C - 2018'''

def part_str(string): #enter a string. return a list with all bipartitions of the list.
    l = []
    for i in range(1,len(string)):
        l.append([string[:i],string[i:]])
    return l

def CYK(string, grammar):
    str_len = len(string)
    half_matrix = []

    for i in range(str_len): #height of the semi-matrix

        half_matrix.append([]) #new line
        new_line_size = len(string) - i

        if i == 0: #first line. dont part_str
            for letter in range(len(string)):
                if string[letter] in grammar:
                    half_matrix[0].append(grammar[string[letter]])
                else: #letter not in the alphabet - return fail
                    return False

        else: #superior levels

            for j in range(new_line_size):
                half_matrix[-1].append([])
                pairs = part_str(string[j:j+i])

                for pair in pairs:
                    line_1, line_2 = len(pair[0]), len(pair[1]) #height to look for
                    box_1, box_2 = half_matrix[line_1-1][j], half_matrix[line_2-1][j+line_1]
                    rules = []

                    for left in box_1:
                        for right in box_2:
                            rules.append(str(left+right))

                    for rule in rules:
                        if rule in grammar:
                            half_matrix[-1][-1] += grammar[rule]

    if 'S' in half_matrix[-1][0]:
        print ('Context-Free Grammar G accepts the string :', string)
    print ('\nParsing tree (possibilities): ',half_matrix)




'''test cases'''


test_grammar = {    #generates L(a^+bb)
    'S':['AB'],
    'A':['AA', 'AB', 'a'],
    'B':['b']
}

test_grammar_inv = {    #pairs/terminals --> rules
    'AB' : ['A', 'S'],
    'AA' : ['A'],
    'a'  : ['A'],
    'b'  : ['B']
}

CYK('aaabb', test_grammar_inv)
