#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "reader.h"
#include <time.h>
#include <string.h>
#include "cnf_builder.h"

const char* PATH_RISS = "riss %s";
const char* PATH_GLUCOSE = "glucose %s -model";

int main(int argc, char* argv[])
{
	char* path = NULL;

    if(argc <= 1)
    {
        printf("Must specify sudoku path!\n");
        exit(EXIT_FAILURE);
    }

	if (argc <= 2)
	{
		printf("Must specify solver: riss or glucose\n");
		exit(EXIT_FAILURE);
	}

	if (strncmp("riss", argv[2], 4) == 0) path = PATH_RISS;
	else if (strncmp("glucose", argv[2], 7) == 0) path = PATH_GLUCOSE;
	else
	{
		printf("Must specify solver: riss or glucose\n");
		exit(EXIT_FAILURE);
	}

    time_t t0 = clock();

    int size = 0;
	int no_cells = 0;
    int** matrix = read_sudoku(argv[1], &size, &no_cells);

    build(matrix, size, no_cells);

	char cmd[64];
	snprintf(cmd, sizeof(cmd), PATH_GLUCOSE, "output.cnf");

	FILE* fp = popen(cmd, "r");
	if (fp == NULL)
	{
		printf("Failed to run solver!\n");
		exit(EXIT_FAILURE);
	}

	char* block = (char*) malloc(size*size*size*size*100 * sizeof(char*));

	int c = 0;

	int* vars = (int*)malloc(size*size*size*size * sizeof(int*) + 64);

	while (fgets(block, size*size*size*size * 100 * sizeof(char*) - 1, fp) != NULL)
	{
		// read output
		if (block[0] == 'v')
		{
			strtok(block, " ");

			char* number = strtok(NULL, " ");

			int num = atoi(number);
			if (num > 0)
			{
				vars[c++] = num;
			}

			while ((number = strtok(NULL, " ")) != NULL)
			{
				int num = atoi(number);

				if (num > 0)
				{
					vars[c++] = num;
				}
			}
		}
	}

	// Write vars (True literals) to temporary file
	// Structure: Line 0: inner size
	//			  Line i: literal

	FILE *f = fopen("temp", "w");
	fprintf(f, "%d\n", size);
	fprintf(f, "%d", vars[0]);

	for (int i = 1; i < c; i++)
	{
		fprintf(f, " %d", vars[i]);
	}
	fclose(f);


	// run python checker
	// char* cmd_python = "python3 ../python-checker/main.py temp";
	// fp = popen(cmd_python, "r");

	// block = (char*)malloc(4096 * sizeof(char*));

	// while (fgets(block, 4095, fp) != NULL)
	// {
	// 	printf("%s", block);
	// }

    exit(EXIT_SUCCESS);
}