from earley import *
from grammar import *  

extra_terms = ['(', ')', '+', '-', '*', '/']

def write_error():
    with open('out', 'w+') as out:
        out.write("InputError")

def fit():
    nonterms = set()
    terms = set()
    with open("in") as f:
        lines = f.read().splitlines()
    
    if len(lines[0].split()) != 3:
        write_error()
        raise ValueError('Incorrect first input line')
    n, sigma, p = map(int, lines[0].split())
    
    if not(len(lines[1]) == n):
        write_error()
        raise ValueError('Quantity of nonterms not equal to n')
    
    for nonterm in lines[1]:
        if not(nonterm.isupper()):
            write_error()
            raise ValueError(f'Non-terminal symbol {nonterm} is not correct')
        nonterms.add(nonterm)
    
    if not(len(lines[2]) == sigma):
        write_error()
        raise ValueError('Quantity of nonterms not equal to sigma')
    
    for term in lines[2]:
        if not(term.islower() or term.isdigit() or term in extra_terms):
            write_error()
            raise ValueError(f'Terminal symbol {term} is not correct')
        terms.add(term)
    
    grammar = Grammar(nonterms, terms)
    for index in range(p):
        cur_line = lines[index + 3]
        
        if '->' not in cur_line:
            write_error()
            raise ValueError(f'Rule \"{cur_line}\" is incorrect')
        
        rule_parts = cur_line.split('->')
        for index in range(len(rule_parts)):
            rule_parts[index] = rule_parts[index].replace(" ", "")
        
        if len(rule_parts) == 1:
            rule_parts.append('')

        for elem in rule_parts[0]:
            if elem not in nonterms:
                write_error()
                raise ValueError(f'Rule \"{cur_line}\" is incorrect, some symbols in left part are undefined')
        
        for char in rule_parts[1]:
            if not(char in nonterms or char in terms):
                write_error()
                raise ValueError(f'Rule \"{cur_line}\" is incorrect, some symbols in right part are undefined')
        grammar.add_rule(Rule(rule_parts[0], rule_parts[1]))
    
    if not(lines[p + 3].isalpha() and len(lines[p + 3]) == 1):
        write_error()
        raise ValueError(f'Start nonterm is incorrect')
    grammar.add_start_nonterm(lines[p + 3])
    
    if not(grammar.isContextFree()):
        write_error()
        raise ValueError('This grammar is not context free')
    
    earley = Earley(grammar)
    cnt_lines = int(lines[p + 4])
    words = lines[p + 5:]
    if len(words) != cnt_lines:
        write_error()
        raise ValueError('Quantity of words and quantity of lines differ')
    for word in words:
        if not(word.islower()):
            raise ValueError(f'Incorrect input string {word}')

    return (earley, words)

def processQueries():
    (earley, words) = fit()
    with open('out', 'w+') as out:
        for word in words:
            word = word.replace(" ", "")
            if earley.inGrammar(word):
                out.write("Yes\n")
            else:
                out.write("No\n")
                
if __name__ == "__main__": 
    processQueries()