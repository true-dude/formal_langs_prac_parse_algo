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
        self.rules = dict()
    
    def add_rule(self, rule: Rule):
        if rule.left not in self.rules.keys():
            self.rules[rule.left] = list()

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
    