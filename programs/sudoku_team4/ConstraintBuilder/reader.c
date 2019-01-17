#define _CRT_SECURE_NO_DEPRECATE

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "reader.h"
#include <string.h>

int** read_sudoku(char* path, int* matrix_size, int* no_cells)
{
	*no_cells = 0;

    FILE * fp;
    char * line = NULL;
    size_t len = 0;
    size_t read;

    char* prefix = "puzzle size: ";

    int state_size = 0;
    int state_ignore = 1;
    int state_number = 2;
    int state_finished = 3;

    int state = state_size;
    int counter = 0;
    int size = 0;

    fp = fopen(path, "r");
    if (fp == NULL)
    {
        printf("Error loading file!\n");
        exit(EXIT_FAILURE);
    }

    int** matrix = NULL;
	char** lines = NULL;

    int block_size;

    while ((read = getline(&line, &len, fp)) != -1) {
        if(state == state_size)
        {
            if(strlen(prefix) < strlen(line) && strncmp(prefix, line, strlen(prefix)) == 0)
            {
                strtok(line, "x");
                char* num = strtok(NULL, "\n");
                block_size = (int) atoi(num);

                size = block_size * block_size;
                state = state_ignore;
                matrix = malloc(size * sizeof(int*));
				lines = malloc(size * sizeof(char*));

                *matrix_size = block_size;
            }
         }
         else if(state == state_ignore)
        {
            if(size == counter)
            {
                state = state_finished;
            } else
            {
                state = state_number;
            }
        } else if(state == state_number)
        {
            char* temp = (char*) malloc(len * sizeof(char));
            strcpy(temp, line);

            lines[counter] = temp;
            counter++;

            if(counter % block_size == 0)
            {
                state = state_ignore;
            }
        }
    }

    for(int i = 0; i < size; i++)
    {
        int* row = (int*) malloc(size * sizeof(int));
        char* line = lines[i];

        strtok(line, " ");

        for(int j = 1; j <= size; j++)
        {
            char* cell = NULL;

            while ((cell = strtok(NULL, " "))[0]== ' ');

            if(cell[0] == '_') row[j - 1] = -1;
			else
			{
				row[j - 1] = atoi(cell);
				(*no_cells)++;
			}

            //printf("%i ", row[j - 1]);

            if(j % block_size == 0) strtok(NULL, " ");

        }

        //printf("\n");

        matrix[i] = row;
    }



    fclose(fp);
    if (line)
        free(line);

	free(lines);

    return matrix;
}