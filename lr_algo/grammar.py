import queue

class Rule:
    def __init__(self, left: str, right: str):
        self.left = left
        self.right = right
    
    def __eq__(self, other) -> bool:
        return (self.left == other.left) and (self.right == other.right)
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.left, self.right))
    
class Grammar:
    def __init__(self, nonterms: set[str], terms: set[str]):
        self.nonterms = nonterms
        self.terms = terms
        terms.add('$')
        nonterms.add('?')
        self.rules = dict()
        self.rules['?'] = list()
        self.rules['?'].append('S')
        self.rule_helper = [('?', 'S')]
        self.first = dict()
    
    def add_rule(self, rule: Rule):
        if rule.left not in self.rules.keys():
            self.rules[rule.left] = list()

        self.rule_helper.append((rule.left, rule.right))
        self.rules[rule.left].append(rule.right)
        
    def add_start_nonterm(self, start_nonterm: str):
        self.start_nonterm = start_nonterm

    def get_rules(self) -> set[Rule]:
        return self.rules
    
    def isNonterm(self, symbol: str):
        return symbol in self.nonterms
    
    def isTerm(self, symbol: str):
        return symbol in self.terms
    
    def isContextFree(self) -> bool:
        for start in self.rules.keys():
            if start not in self.nonterms or len(start) != 1:
                return False
        
        return True

    def get_first(self, symbol: str) -> set:
        if symbol in self.nonterms:
            return {symbol}

        if symbol not in self.first.keys():
            result = set()
            used = dict()
            for char in self.nonterms:
                used[char] = False
                
            char_queue = queue.Queue()
            char_queue.put(symbol)
            while not(char_queue.empty()):
                cur_char = char_queue.get()
                used[cur_char] = True
                for right in self.rules[cur_char]:
                    if len(right) == 0:
                        result.add("")
                        continue
                    if self.grammar.isTerm(right[0]):
                        result.add(right[0])
                    elif not(used[right[0]]):
                        char_queue.put(right[0])
            self.first[symbol] = result
            
        return self.first[symbol]
        
    def eps_generator(self, nonterm: str) -> bool:
        if nonterm not in self.nonterms:
            raise ValueError('Checking eps-generative for undefined nonterm')
        
        return ("" in self.get_first(nonterm))
    
    def First(self, alpha: str) -> set:
        if len(alpha) == 0:
            raise ValueError("Empty string given First")
        
        if alpha[0] in self.terms:
            return {alpha[0]}
        
        if alpha[0] in self.nonterms:
            if self.eps_generator(alpha[0]) and len(alpha) > 1:
                result = (self.get_first(alpha[0])).union(self.get_first(alpha[1]))
                return result
            else:
                return self.get_first(alpha[0])
        
        raise ValueError(f"Unknown string {alpha}")
        

    
    