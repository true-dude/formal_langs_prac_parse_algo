from grammar import *
import queue

class LR1:
    class Situation:            
        def __init__(self, rule: Rule, char: str, point_position: int):
            self.rule = rule
            self.char = char
            self.point_position = point_position
            
        def __eq__(self, other) -> bool:
            return self.rule == other.rule and self.char == other.char and self.point_position == other.point_position
    
        def __ne__(self, other) -> bool:
            return not self.__eq__(other)
        
        def __hash__(self):
            return hash((self.rule, self.char, self.point_position))
        
        def passed(self):
            return len(self.rule.right) == self.point_position
        
    class Node:
        def __init__(self):
            self.situations = set()
            self.index = 0
            self.reducable = False
            
        def __eq__(self, other) -> bool:
            return self.situations == other.situations
            
        def __ne__(self, other) -> bool:
            return not self.__eq__(other)
        
        def add_situation(self, situation):
            self.situations.add(situation)
        
    class Action:
        def __init__(self, type: str, value: int) -> None:
            self.type = type
            self.value = value
        
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.nodes = list()
        self.graph = list()
    
    def closure(self, node) -> None:
        prev_len = len(node.situations)
        while True:
            for situation in node.situations.copy():
                if situation.passed():
                    node.reducable = True
                if not(situation.passed()) and self.grammar.isNonterm(situation.rule.right[situation.point_position]) and situation.rule.right[situation.point_position] in self.grammar.rules.keys():
                    # print(self.grammar.rules[situation.rule.right[situation.point_position]][0])
                    for right_part in self.grammar.rules[situation.rule.right[situation.point_position]]:
                        for new_char in self.grammar.First(situation.rule.right[situation.point_position + 1:] + situation.char):
                            new_situation = self.Situation(Rule(situation.rule.right[situation.point_position], right_part), new_char, 0)
                            node.add_situation(new_situation)
            
            cur_len = len(node.situations)
            if cur_len == prev_len:
                break
            prev_len = cur_len
        
        for situation1 in node.situations:
            for situation2 in node.situations:
                if situation1 == situation2:
                    continue
                
                if situation1.point_position > 0 and situation1.rule.right[:situation1.point_position] == situation2.rule.right[:situation2.point_position] and situation1.char == situation2.char:
                    prefix = situation1.rule.right[:situation1.point_position]
                    ok = True
                    for elem in prefix:
                        if self.grammar.isNonterm(elem):
                            ok = False                    
                    if ok:
                        raise ValueError(f"GRAMMAR IS NOT LR(1)\nFOUND matches:\n[{situation1.rule.left} -> {situation1.rule.right}, {situation1.char}]\n[{situation2.rule.left} -> {situation2.rule.right}, {situation2.char}]")
    
    def goto(self, node, char: str) -> None:
        new_node = self.Node()
        for elem in node.situations:
            if not(elem.passed()) and elem.rule.right[elem.point_position] == char:
                new_situation = self.Situation(elem.rule, elem.char, elem.point_position + 1)
                new_node.add_situation(new_situation)
        
        self.closure(new_node)
        
        if new_node not in self.nodes:
            new_node.index = len(self.nodes)
            self.nodes.append(new_node)
            self.graph.append(list())
        else:
            new_node.index = self.nodes.index(new_node)
    
        if (new_node.index, char) not in self.graph[node.index]:
            self.graph[node.index].append((new_node.index, char))
        
    def get_symbols_for_goto(self, node) -> set:
        result = set()
        for elem in node.situations:
            # print(elem.rule.right, elem.pa)
            if not(elem.passed()):
                result.add(elem.rule.right[elem.point_position])
        # print(result)
        return result
 
    def build_graph(self):
        first_node = self.Node()
        first_node.add_situation(self.Situation(Rule("?", self.grammar.start_nonterm), '$', 0))
        self.closure(first_node)
        self.nodes.append(first_node)
        self.graph.append(list())
        node_queue = queue.Queue()
        node_queue.put(first_node)
        while not(node_queue.empty()):
            prev_len = len(self.nodes)
            cur_node = node_queue.get()
            for symbol in self.get_symbols_for_goto(cur_node):
                # print(symbol)
                self.goto(cur_node, symbol)
            
            for i in range(prev_len, len(self.nodes)):
                node_queue.put(self.nodes[i])
        
    def build_table(self):
        for i in range(len(self.nodes)):
            print(f'\nNode number: {i}\n++++++++++++++++++++++++++')
            for situation in self.nodes[i].situations:
                print(f"[{situation.rule.left} -> {situation.rule.right[:situation.point_position]}*{situation.rule.right[situation.point_position:]}, {situation.char}]")
            print("++++++++++++++++++++++++++\n")
                
        self.table = list()
        for node_from in range(len(self.graph)):
            self.table.append(dict())
            for elem in self.graph[node_from]:
                to, char = elem
                print(f"go from {node_from} via {char} -> {to} ")
                if self.grammar.isNonterm(char):
                    self.table[node_from][char] = self.Action("default", to)
                elif self.grammar.isTerm(char):
                    self.table[node_from][char] = self.Action("shift", to)
                else:
                    raise ValueError(f"build table: symbol {char} not in Non-terms and not in Terms")
        
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            if node.reducable:
                for situation in node.situations:
                    if situation.passed():
                        index = self.grammar.rule_helper.index((situation.rule.left, situation.rule.right)) 
                        if situation.char not in self.table[i].keys():
                            self.table[i][situation.char] = self.Action("reduce", index)
                            
        print("i\t?\tS\ta\tb\t$")
        temp = ["?", "S", "a", "b", "$"]
        for i in range(len(self.nodes)):
            print(i, end = "\t"),
            # print(self.table[i].items())
            for char in temp:
                if char in self.table[i].keys():
                    if self.table[i][char].type == "default":
                        print(self.table[i][char].value, end="\t")
                    if self.table[i][char].type == "shift":
                        print(f"s({self.table[i][char].value})", end="\t")
                    if self.table[i][char].type == "reduce":
                        print(f"r({self.table[i][char].value})", end="\t")
                else:
                    print("-", end="\t")
            print()
        
    def process(self, word: str) -> bool:
        word = word + '$'
        pos = 0
        stack_char = []
        stack_int = [0]
        while pos < len(word):
            a = word[pos]   
            q = stack_int[-1]
            # print("stack_char is:", stack_char)
            # print("stack_int is: ", stack_int)
            # print("q, a:", q, a)
            if a not in self.table[q].keys():
                return False
            
            match self.table[q][a].type:
                case "shift":
                    stack_char.append(a)
                    pos += 1
                    stack_int.append(self.table[q][a].value)
                case "reduce":
                    # print(f'reduce value is {self.table[q][a].value}')
                    if self.table[q][a].value == 0:
                        return True
                    
                    left, right = self.grammar.rule_helper[self.table[q][a].value]
                    if len(stack_char) < len(right):
                        return False
                    
                    test = ""
                    for i in range(len(stack_char) - len(right), len(stack_char)):
                        test = test + stack_char[i]

                    if test != right:
                        return False
                
                    for i in range(len(right)):
                        stack_char.pop()
                        stack_int.pop()
                    
                    stack_char.append(left)
                    if len(stack_int) == 0:
                        return False
                    if left not in self.table[stack_int[-1]].keys():
                        return False

                    stack_int.append(self.table[stack_int[-1]][left].value)
                    
                case _:
                    return False
        
    def inGrammar(self, word: str) -> bool:
        print(f"\nNEW QUERY \"{word}\"\n")
        return self.process(word)
