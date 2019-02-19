/*

#include <math.h>
#include <stdlib.h>

int convert(int x, int y, int z, int outer_size)
{
    return (z - 1) * (outer_size * outer_size) + (y - 1) * outer_size + (x - 1) + 1;
}

int** build(int** matrix, int size, size_t* no_clauses)
{
    // prepare clauses array
    int outer_size = size * size;

    // should be sufficient
    // TODO: Find lower upper bound
    size_t max_size = 40 * pow(outer_size, 4);
    int** clauses = (int*) malloc(max_size * sizeof(int*));

    for(size_t i = 0; i < max_size; i++)
    {
        clauses[i] = NULL;
    }

    *no_clauses = 0;

    // at least one number in each entry
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int y = 1; y < outer_size + 1; y++)
        {
            int* clause = (int*) malloc((outer_size + 1) * sizeof(int));

            for(int z = 1; z < outer_size + 1; z++)
            {
                clause[z - 1] = convert(x, y, z, outer_size);
            }

            clause[outer_size] = 0;

            clauses[(*no_clauses)++] = clause;
        }
    }

    // each number appears at most once in each row
    for(int y = 1; y < outer_size + 1; y++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
            for(int x = 1; x < outer_size + 1; x++)
            {
                for(int i = x + 1; i < outer_size + 1; i++)
                {
                    int* clause = (int*) malloc(3 * sizeof(int));
                    clause[0] = -convert(x, y, z, outer_size);
                    clause[1] = -convert(i, y, z, outer_size);
                    clause[2] = 0;

                    clauses[(*no_clauses)++] = clause;
                }
            }
        }
    }

    // each number appears at most once in each column
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
            for(int y = 1; y < outer_size + 1; y++)
            {
                for(int i = y + 1; i < outer_size + 1; i++)
                {
                    int* clause = (int*) malloc(3 * sizeof(int));
                    clause[0] = -convert(x, y, z, outer_size);
                    clause[1] = -convert(x, i, z, outer_size);
                    clause[2] = 0;

                    clauses[(*no_clauses)++] = clause;
                }
            }
        }
    }

    // each number appears at most once in each subgrid
    for(int z = 1; z < outer_size + 1; z++)
    {
        for(int i = 0; i < size; i++)
        {
            for(int j = 0; j < size; j++)
            {
                for(int x = 1; x < size + 1; x++)
                {
                    for(int y = 1; y < size + 1; y++)
                    {
                        for(int k = y + 1; k < size + 1; k++)
                        {
                            int* clause = (int*) malloc(3 * sizeof(int));
                            clause[0] = -convert(size * i + x, size * j + y, z, outer_size);
                            clause[1] = -convert(size * i + x, size * j + k, z, outer_size);
                            clause[2] = 0;

                            clauses[(*no_clauses)++] = clause;
                        }
                    }    
                }
            }
        }    
    }

    for(int z = 1; z < outer_size + 1; z++)
    {
        for(int i = 0; i < size; i++)
        {
            for(int j = 0; j < size; j++)
            {
                for(int x = 1; x < size + 1; x++)
                {
                    for(int y = 1; y < size + 1; y++)
                    {
                        for(int k = x + 1; k < size + 1; k++)
                        {
                            for(int l = 1; l < size + 1; l++)
                            {
                                int* clause = (int*) malloc(3 * sizeof(int));
                                clause[0] = -convert(size * i + x, size * j + y, z, outer_size);
                                clause[1] = -convert(size * i + k, size * j + l, z, outer_size);
                                clause[2] = 0;

                                clauses[(*no_clauses)++] = clause;    
                            }
                        }
                    }    
                }
            }
        }    
    }

    // There is at most one number in each cell
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int y = 1; y < outer_size + 1; y++)
        {
            for(int z = 1; z < outer_size; z++)
            {
                for(int i = z + 1; i < outer_size + 1; i++)
                {
                    int* clause = (int*) malloc(3 * sizeof(int));
                    clause[0] = -convert(x, y, z, outer_size);
                    clause[1] = -convert(x, y, i, outer_size);
                    clause[2] = 0;

                    clauses[(*no_clauses)++] = clause;
                }
            }
        }
    }

    // Each number appears at least once in each row
    for(int y = 1; y < outer_size + 1; y++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
            int* clause = (int*) malloc((outer_size + 1) * sizeof(int));

            for(int x = 1; x < outer_size + 1; x++)
            {
                clause[x - 1] = convert(x, y, z, outer_size);
            }

            clause[outer_size] = 0;

            clauses[(*no_clauses)++] = clause;
        }
    }

    // Each number appears at least once in each column
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
            int* clause = (int*) malloc((outer_size + 1) * sizeof(int));

            for(int y = 1; y < outer_size + 1; y++)
            {
                clause[y - 1] = convert(x, y, z, outer_size);
            }

            clause[outer_size] = 0;

            clauses[(*no_clauses)++] = clause;
        }
    }

    // Each number appears at least once in each 3x3 sub-grid
    for(int z = 1; z < outer_size + 1; z++)
    {
        for(int i = 0; i < size; i++)
        {
            for(int j = 0; j < size; j++)
            {
                int* clause = (int*) malloc((outer_size + 1) * sizeof(int));

                for(int x = 1; x < size + 1; x++)
                {
                    for(int y = 1; y < size + 1; y++)
                    {
                        clause[(x - 1) * size + y - 1] = convert(i * size + x, j * size + y, z, outer_size);
                    }    
                }

                clause[outer_size] = 0;

                clauses[(*no_clauses)++] = clause;
            }
        }    
    }

    // initially set fields
    for(int x = 0; x < outer_size; x++)
    {
        for(int y = 0; y < outer_size; y++)
        {
            int z = matrix[x][y];

            if(z != -1)
            {
                int* clause = (int*) malloc(2 * sizeof(int));
                clause[0] = convert(x + 1, y + 1, z, outer_size);
                clause[1] = 0;
                clauses[(*no_clauses)++] = clause;
            }
        }
    }

    return clauses;

}

*/