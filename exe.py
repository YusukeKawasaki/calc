import itertools
import math
from tqdm import tqdm

global count
count = 0

def is_significant(x) -> bool:
    """
    計算結果として有意な値か否か
    """
    big = 300000
    floatok = False
    round=lambda x:(x*2+1)//2 #四捨五入

    ans = True
    if math.isnan(x):
        return False
    if abs(x) > big:
        return False
    if not math.isclose(x, round(x)):
        ans = floatok
    return ans

def s(x):
    return math.sqrt(x)

def f(x):
    if x < 11:
        return math.factorial(x)
    else:
        return None

def pow_big(x, y):
    ans = 1
    for i in range(int(y)):
        ans *= x
        if ans > 1000000000:
            return True
    return False

class Charactors():
    '''
    数字の列。C。
    これに演算子を加えてFormula(式)とMember(項)を作る。
    部分列(c_parts)も同様にCharactorsで定義される。
    CharactorList: strのリスト
    isroot: 列全体ならTrue, 部分列ならFalse
    position: 部分列の位置, (int, int)
    '''
    def __init__(self, CharactorList, is_root = True, position = None):
        self.list = CharactorList
        self.len = len(self.list)

        self.formulas = []
        self.members = []

        self.alljoin = Member(''.join(CharactorList), need_brackets = False, weight = 0)
        self.position = position

        if is_root:
            self.position = (0, self.len)
            global c_parts
            c_parts = [[None for i in range(self.len+1)] for j in range(self.len+1)]
            for i in range(self.len):
                for j in range(self.len+1):
                    if i < j:
                        c_parts[i][j] = Charactors(self.list[i:j], position = (i, j), is_root=False)
            for k in range(1, self.len):
                for i in range(self.len):
                    for j in range(self.len+1):
                        if j - i == k:
                            c_parts[i][j].solve_m()
                            c_parts[i][j].solve_f()
            self.solve_f()
            self.solve_m()

    def solve_f(self):
        if self.formulas:
            return 0
        if self.len > 1:
            splits = self.split() #自身を分割したCのpositionのリスト、自身を除く
            for positions in splits:
                for M_product in list(itertools.product(*[c_parts[i][j].members for i, j in positions])):
                    F = make_formula(M_product)
                    self.formulas.append(F)
            self.formulas = remove_dup(self.formulas)

    def solve_m(self):
        if self.members:
            return 0
        
        self.members += make_member(self.alljoin, num = 1)
        self.members.append(self.alljoin)
        if self.len > 1:
            cuts = self.cut() #自身を2分割したCのリスト座標のリスト
            for positions in cuts:
                for FM_product in list(itertools.product(*[c_parts[i][j].formulas + c_parts[i][j].members for i, j in positions])):
                    Ms = make_member(FM_product, num = 2)
                    self.members += Ms
            for F in self.formulas: #Fに対して一項演算子をかけたもの
                Ms = make_member(F, num = 1)
                self.members += Ms
            self.members = remove_dup(self.members)
    
    def split(self):
        '''
        イメージ　0 1 2 3 4 -> 0 1|2 3|4
        出力：[(0, 2), (2, 4), (4, 5)] のような組み合わせ全てのリスト

        start と end の間にある整数のうちどれかを採用してどれかを採用しない、その組を全て求める
        → start+1からend-1までの整数の列からなる列を全て出力し、startとendを加えたものを用意
        → しりとりして出力 '''
        ans = []
        start, end = self.position
        temp = list(range(start + 1, end))
        for k in range(1, len(temp) + 1):
            for comb in itertools.combinations(temp, k):
                temp2 = [start] + list(comb) + [end] #要素はk + 2個
                temp3 = []
                for i in range(k+1):
                    temp3.append((temp2[i], temp2[i+1]))
                ans.append(temp3)
        return ans

    def cut(self):
        '''
        イメージ　0 1 2 3 4 -> 0 1|2 3 4
        出力：[(0, 2), (2, 5)] のような二分割の組み合わせ全てのリスト
        '''

        ans = []
        for i in range(self.position[0]+1, self.position[1]):
            ans.append([(self.position[0], i), (i, self.position[1])])
        return ans

class Formula():
    def __init__(self, label: str, weight, need_brackets = True):
        self.label = label
        self.significant, self.value = self.calc() #有意な値か否か
        self.need_brackets = need_brackets

        self.b_label = self.make_b_label()
        self.weight = weight #重みを付けてみる
    
    def calc(self):
        try:
            # print(self.label)
            global count
            count += 1
            value = eval(self.label)
            return (is_significant(value), int(value)) 
        except:
            return (False, None)
    
    def make_b_label(self):
        if self.need_brackets:
            return '({})'.format(self.label)
        else:
            return self.label
    
class Member():
    def __init__(self, label: str, weight, need_brackets = True):
        self.label = label
        self.significant, self.value = self.calc() #有意な値か否か
        self.need_brackets = need_brackets

        self.b_label = self.make_b_label()
        self.weight = weight #重みを付けてみる
    
    def calc(self):
        try:
            # print(self.label)
            global count
            count += 1
            value = eval(self.label)
            return (is_significant(value), value)
        except:
            return (False, None)
    
    def make_b_label(self):
        if self.need_brackets:
            return '({})'.format(self.label)
        else:
            return self.label

def make_formula(members):
    '''
        Mを全て足したFを生成するだけ
    '''
    label = ''
    weight = 0
    if len(members) == 1:
        print('members length is 1.')
        exit()
    for i, M in enumerate(members):
        if M.label[0] == '-':
            label += M.label
            weight += (M.weight + 1)
        elif i == 0:
            label += M.label
            weight += M.weight
        else:
            label += '+'
            label += M.label
            weight += (M.weight + 1)
    return Formula(label, weight = weight)

def make_member(arg, num):
    Ms = []
    if num == 1: #F単体の場合
        F = arg
        Ms.append(Member('-{}'.format(F.b_label), need_brackets = True, weight = F.weight + 1)) #負にする +1の重み
        Ms.append(Member('s({})'.format(F.b_label), need_brackets = False, weight = F.weight + 100)) #平方根にする +100の重み
        Ms.append(Member('f({})'.format(F.b_label), need_brackets = False, weight = F.weight + 100)) #階乗にする +100の重み
    else: #2つの要素がある場合
        (F1, F2) = (arg[0], arg[1])
        weight = F1.weight + F2.weight
        M1 = Member('{}*{}'.format(F1.b_label, F2.b_label), need_brackets = False, weight = weight+1)
        Ms.append(M1)
        M2 = Member('{}/{}'.format(F1.b_label, F2.b_label), need_brackets = False, weight = weight+1)
        Ms.append(M2)
        if not pow_big(F1.value, F2.value):
            M3 = Member('{}**{}'.format(F1.b_label, F2.b_label), need_brackets = True, weight = weight+10)
            Ms.append(M3)
    return [M for M in Ms if M.significant]

def remove_dup(FM_list):
    ans = []
    FM_list.sort(key = lambda x:(x.value, x.weight))
    if FM_list:
        ans.append(FM_list[0])
        for i in range(len(FM_list)-1):
            if int(FM_list[i+1].value) > int(FM_list[i].value):
                ans.append(FM_list[i+1])
    return ans

l = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
C = Charactors(l)
ans = C.formulas + C.members
ans = remove_dup(ans)
for F in ans:
    if int(F.value) == 114514:
        print(F.label)