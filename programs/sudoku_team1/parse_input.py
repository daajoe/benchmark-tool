import sys
import numpy as np

def convert_nativ_to_dense(N, i, j, n):
    n = N**2*(i-1) + N*(j-1) + (n-1) + 1
    return str(n) + " "

def read_inital_values(file_name, N):
    file_ptr = open(file_name)
    out_file = open("sudoku.cnf", "w+")
    i = 1
    for line in file_ptr.readlines():
        if line.startswith("|"):
            line = line.replace("| ", "")
            line = line.replace(" |" , "")
            line = line.replace("\n", "")
            numbers = line.split()
            for j, nn in enumerate(numbers):
                if nn != "_" and nn != "__" and nn != "___":
                    nn = int(nn)
                    out_file.write(str(convert_nativ_to_dense(N, i, j+1, nn)) + "0\n")
            i += 1
    file_ptr.close()
    out_file.close()

def get_model_information(file_name):
    file_ptr = open(file_name)
    for line in file_ptr.readlines():
        if "puzzle size:" in line:
            n = line.split(" ")[-1].split("x")[-1]
            N_sqrt = int(np.sqrt(int(n)))
            N = int(n)
            break

    file_ptr.close()
    return N, N_sqrt

def main():
    file_name = sys.argv[1]
    N, N_sqrt = get_model_information(file_name)
    read_inital_values(file_name, N)
    print(N_sqrt)




if __name__ == "__main__":
    main()



