import numpy as np
import sys
#import birkhoff as bi

f = open("out.txt")
nn = int(sys.argv[1])
N = nn**2

def convert_dense_to_native(clause, N=4):
    clause -= 1
    first = clause % N**2
    i = (clause - (first))/N**2 + 1
    second = first % N
    j = (first - second)/N + 1
    n = second + 1
    return i, j, n

sodoku = np.zeros( (N, N) )
for line in f.readlines():
    if line[0] == "v":
        clauses = line[2:].split(" ")
        for n in clauses:
            n = int(n)
            if n>0:
                i, j, n = convert_dense_to_native(n, N=N)
                sodoku[i-1][j-1] = n

#result = bi.birkhoff_von_neumann_decomposition(2*sodoku/(N*(N+1)))
#for c, p in result:
#    print("coeff ", (N+1)*N*c/2)
#    print("m: ", p)




f_out = open("result.txt", "w+")
f_out.writelines("experiment: generator (Time: 0.1 s)\n")
f_out.writelines("number of tasks: 1\n")
f_out.writelines("task: 1\n")
f_out.writelines("puzzle size: " + str(nn)+"x"+str(nn)+"\n")

def make_numb_str(n, N):
    numb_str = str(int(n))
    while len(numb_str) < N:
        numb_str = " " + numb_str
    return numb_str

a = len(str(int(np.max(sodoku))))

sep_line = nn*("+" + nn*a*"-" + (nn+1)*"-") + "+"
for i in range(N):
    if (i % nn) == 0:
        f_out.writelines(sep_line+"\n")
    line = "|"
    for j in range(N):
        line += " " + make_numb_str(sodoku[i][j], a)
        if (j + 1 ) % nn == 0:
            line += " |"
    f_out.writelines(line+"\n")
f_out.writelines(sep_line+"\n")
f_out.close()
