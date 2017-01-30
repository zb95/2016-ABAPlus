myAsm(a).
myAsm(b).
myAsm(c).

myPrefLT(a,b).
myPrefLT(c,b).

contrary(a, a_c).
contrary(b, b_c).
contrary(c, c_c).

myRule(b_c, [a,c]).
myRule(a_c, [b,c]).
myRule(c_c, [a,b]).