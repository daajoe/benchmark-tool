#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int convert(int x, int y, int z, int outer_size)
{
    return (z - 1) * (outer_size * outer_size) + (y - 1) * outer_size + (x - 1) + 1;
}

int** build(int** matrix, int size, int no_cells)
{
    // prepare clauses array
    int outer_size = size * size;

	// 2*n^4*(n^4-n^2+2) + no_cells
	size_t no_clauses = 2 * outer_size * outer_size * (outer_size * outer_size - outer_size + 2) + no_cells;
	int no_vars = outer_size * outer_size * outer_size;

	FILE *f = fopen("output.cnf", "w");

	fprintf(f, "p cnf %d %ld\n", no_vars, no_clauses);

    // at least one number in each entry
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int y = 1; y < outer_size + 1; y++)
        {
			if (matrix[x - 1][y - 1] != -1) continue;

            for(int z = 1; z < outer_size + 1; z++)
            {
                fprintf(f, "%d ", convert(x, y, z, outer_size));
            }

			fprintf(f, "0\n");
        }
    }

    // each number appears at most once in each row
    for(int y = 1; y < outer_size + 1; y++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
            for(int x = 1; x < outer_size + 1; x++)
            {
				if (matrix[x - 1][y - 1] == -1)
				{
					for (int i = x + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d %d 0\n", -convert(x, y, z, outer_size), -convert(i, y, z, outer_size));
					}
				}
				else if (matrix[x - 1][y - 1] == z)
				{
					for (int i = x + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d 0\n", -convert(i, y, z, outer_size));
					}
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
				if (matrix[x - 1][y - 1] == -1)
				{
					for (int i = y + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d %d 0\n", -convert(x, y, z, outer_size), -convert(x, i, z, outer_size));
					}
				}
				else if (matrix[x - 1][y - 1] == z)
				{
					for (int i = y + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d 0\n", -convert(x, i, z, outer_size));
					}
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
						if (matrix[i * size + x - 1][j * size + y - 1] == -1)
						{
							for (int k = y + 1; k < size + 1; k++)
							{
								fprintf(f, "%d %d 0\n", -convert(size * i + x, size * j + y, z, outer_size), -convert(size * i + x, size * j + k, z, outer_size));
							}
						}
						else if (matrix[i * size + x - 1][j * size + y - 1] == z)
						{
							for (int k = y + 1; k < size + 1; k++)
							{
								fprintf(f, "%d 0\n", -convert(size * i + x, size * j + k, z, outer_size));
							}
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
						if (matrix[i * size + x - 1][j * size + y - 1] == -1)
						{
							for (int k = x + 1; k < size + 1; k++)
							{
								for (int l = 1; l < size + 1; l++)
								{
									fprintf(f, "%d %d 0\n", -convert(size * i + x, size * j + y, z, outer_size), -convert(size * i + k, size * j + l, z, outer_size));
								}
							}
						}
						else if (matrix[i * size + x - 1][j * size + y - 1] == z)
						{
							for (int k = x + 1; k < size + 1; k++)
							{
								for (int l = 1; l < size + 1; l++)
								{
									fprintf(f, "%d 0\n", -convert(size * i + k, size * j + l, z, outer_size));
								}
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
				if (matrix[x - 1][y - 1] == -1)
				{
					for (int i = z + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d %d 0\n", -convert(x, y, z, outer_size), -convert(x, y, i, outer_size));
					}
				}
				else if (matrix[x - 1][y - 1] == z)
				{
					for (int i = z + 1; i < outer_size + 1; i++)
					{
						fprintf(f, "%d 0\n", -convert(x, y, i, outer_size));
					}
				}
                
            }
        }
    }

    // Each number appears at least once in each row
    for(int y = 1; y < outer_size + 1; y++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
			int found = 0;
			for (int x = 1; x < outer_size + 1; x++)
			{
				if (matrix[x - 1][y - 1] == z)
				{
					found = 1;
					break;
				}
			}

			if (found) break;

            for(int x = 1; x < outer_size + 1; x++)
            {
				fprintf(f, "%d ", convert(x, y, z, outer_size));
            }

			fprintf(f, "0\n");
        }
    }

    // Each number appears at least once in each column
    for(int x = 1; x < outer_size + 1; x++)
    {
        for(int z = 1; z < outer_size + 1; z++)
        {
			int found = 0;
			for (int y = 1; y < outer_size + 1; y++)
			{
				if (matrix[x - 1][y - 1] == z)
				{
					found = 1;
					break;
				}
			}

			if (found) break;

            for(int y = 1; y < outer_size + 1; y++)
            {
				fprintf(f, "%d ", convert(x, y, z, outer_size));
            }

			fprintf(f, "0\n");
        }
    }

    // Each number appears at least once in each 3x3 sub-grid
    for(int z = 1; z < outer_size + 1; z++)
    {
        for(int i = 0; i < size; i++)
        {
            for(int j = 0; j < size; j++)
            {
				int found = 0;

				for (int x = 1; x < size + 1; x++)
				{
					for (int y = 1; y < size + 1; y++)
					{
						if (matrix[i * size + x - 1][j * size + y - 1] == z)
						{
							found = 1;
							break;
						}
					}

					if (found) break;
				}

				if (found) break;

                for(int x = 1; x < size + 1; x++)
                {
                    for(int y = 1; y < size + 1; y++)
                    {
						fprintf(f, "%d ", convert(i * size + x, j * size + y, z, outer_size));
                    }    
                }

				fprintf(f, "0\n");
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
				fprintf(f, "%d 0\n", convert(x + 1, y + 1, z, outer_size));
				//printf("%d\n", z);
            }
        }
    }

	fclose(f);


    

}

