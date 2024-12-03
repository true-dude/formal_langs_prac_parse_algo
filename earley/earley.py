from grammar import *
from copy import deepcopy

class Earley:
    class Situation:
        def __init__(self, rule: Rule, i: int, point_position: int):
            self.rule = rule
            self.i = i
            self.point_position = point_position
            self.completed = False
            self.predicted = False
            
        def __eq__(self, other) -> bool:
            return self.rule == other.rule and self.i == other.i and self.point_position == other.point_position
    
        def __ne__(self, other) -> bool:
            return not self.__eq__(other)
        
        def __hash__(self):
            return hash((self.rule, self.i, self.point_position))
        
        def passed(self):
            return len(self.rule.right) == self.point_position
            
    def undo(self, situation : Situation) -> Situation:
        copy = deepcopy(situation)
        copy.completed = False
        copy.predicted = False
        return copy
        
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.d_helper = dict()
        self.d = dict()
        
    def add_formal_rule(self):
        self.d_helper[0] = [self.Situation(Rule('?', self.grammar.start_nonterm), 0, 0)]
        self.d[0] = {self.Situation(Rule('?', self.grammar.start_nonterm), 0, 0)}
        
    def scan(self, j: int, word: str):
        if j == 0:
            return
        for situation in self.d_helper[j - 1]:
            if situation.point_position < len(situation.rule.right):
                symbol = situation.rule.right[situation.point_position]
                if self.grammar.isTerm(symbol) and symbol == word[j - 1]:
                    print(f"scan: [{situation.rule.left} -> {situation.rule.right[:situation.point_position]}*{situation.rule.right[situation.point_position:]}, {situation.i}]")
                    new_situation = situation
                    new_situation = self.undo(new_situation)
                    new_situation.point_position += 1
                    if not(new_situation in self.d[j]):
                        self.d[j].add(new_situation)
                        self.d_helper[j].append(new_situation)
                        print(f"scan: adding to D_{j} [{new_situation.rule.left} -> {new_situation.rule.right[:new_situation.point_position]}*{new_situation.rule.right[new_situation.point_position:]}, {new_situation.i}]")
    
    def complete(self, j: int):
        for_adding = set()
        for index in range(len(self.d_helper[j]) - 1, -1, -1):
            situation1 = self.d_helper[j][index]
            if situation1.completed and not(situation1.i == j):
                continue
            print(f"complete: [{situation1.rule.left} -> {situation1.rule.right[:situation1.point_position]}*{situation1.rule.right[situation1.point_position:]}, {situation1.i}]")
            self.d_helper[j][index].completed = True
            if situation1.passed():
                for situation2 in self.d[situation1.i]:
                    if not(situation2.passed()) and situation2.rule.right[situation2.point_position] == situation1.rule.left:
                        new_situation = self.undo(situation2)
                        new_situation.point_position += 1
                        if not(new_situation in self.d[j]):
                            for_adding.add(new_situation)

        for situation in for_adding:
            print(f"complete: adding to D_{j} [{situation.rule.left} -> {situation.rule.right[:situation.point_position]}*{situation.rule.right[situation.point_position:]}, {situation.i}]")
            self.d[j].add(situation)
            self.d_helper[j].append(situation)
       
    def predict(self, j: int):
        for_adding = set()
        for index in range(len(self.d_helper[j]) - 1, -1, -1):
            situation = self.d_helper[j][index]
            if situation.predicted:
                break
            print(f"predict: [{situation.rule.left} -> {situation.rule.right[:situation.point_position]}*{situation.rule.right[situation.point_position:]}, {situation.i}]")
            self.d_helper[j][index].predicted = True
            if not(situation.passed()) and self.grammar.isNonterm(situation.rule.right[situation.point_position]):
                # print(situation.rule.right[situation.point_position])
                # print(self.grammar.rules[situation.rule.right[situation.point_position]])
                for right_part in self.grammar.rules[situation.rule.right[situation.point_position]]:
                    # print(f"right part is {right_part}")
                    new_situation = self.Situation(Rule(situation.rule.right[situation.point_position], right_part), j, 0)
                    # print(f"new_situation: [{new_situation.rule.left} -> {new_situation.rule.right[:new_situation.point_position]}*{new_situation.rule.right[new_situation.point_position:]}, {new_situation.i}]")
                    if not(new_situation in self.d[j]):
                        for_adding.add(new_situation)
        
        # print(len(for_adding))
        for situation in for_adding:
            print(f"predict: adding to D_{j} [{situation.rule.left} -> {situation.rule.right[:situation.point_position]}*{situation.rule.right[situation.point_position:]}, {situation.i}]")
            self.d[j].add(situation)
            self.d_helper[j].append(situation)
    
    def execute(self, word: str) -> bool:
        for j in range(len(word) + 1):
            print(f"--------------- j = {j} --------------")
            if j not in self.d:
                self.d[j] = set()
                self.d_helper[j] = list()

            self.scan(j, word)
            prev_size = len(self.d[j])
            while True:
                self.complete(j)
                self.predict(j)
                cur_size = len(self.d[j])
                print(prev_size, cur_size)
                if prev_size == cur_size:
                    break
                prev_size = cur_size
        
        return self.Situation(Rule('?', self.grammar.start_nonterm), 0, 1) in self.d[len(word)]
    
        
    def inGrammar(self, word: str) -> bool:
        print(f"\n\nNEW QUERY \"{word}\"\n\n")
        self.d.clear()
        self.d_helper.clear()
        self.add_formal_rule()
        return self.execute(word)
