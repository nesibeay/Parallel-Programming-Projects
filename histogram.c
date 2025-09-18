#include <omp.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
 
#define BINS 256 
 
int main(int argc, char* argv[]) { 
    if (argc != 4) { 
        fprintf(stderr, "Usage: %s <data_size> <num_threads> <schedule_type>\n", argv[0]); 
        fprintf(stderr, "schedule_type: static | dynamic | guided\n"); 
        return 1; 
    } 
 
    int DATA_SIZE = atoi(argv[1]); 
    int NUM_THREADS = atoi(argv[2]); 
    char *schedule_type = argv[3]; 
 
    int *data = malloc(sizeof(int) * DATA_SIZE); 
    int histogram[BINS] = {0}; 
 
    for (int i = 0; i < DATA_SIZE; i++) { 
        data[i] = rand() % BINS; 
    } 
 
    omp_set_num_threads(NUM_THREADS); 
 
    int num_threads; 
    #pragma omp parallel 
    { 
        #pragma omp single 
        num_threads = omp_get_num_threads(); 
    } 
 
    int **local_histograms = malloc(sizeof(int*) * num_threads); 
    for (int i = 0; i < num_threads; i++) { 
        local_histograms[i] = calloc(BINS, sizeof(int)); 
    } 
 
    double start = omp_get_wtime(); 
 
    #pragma omp parallel 
    { 
        int tid = omp_get_thread_num(); 
        int *local = local_histograms[tid]; 
 
        if (strcmp(schedule_type, "static") == 0) { 
            #pragma omp for schedule(static) 
            for (int i = 0; i < DATA_SIZE; i++) 
                local[data[i]]++; 
 
        } else if (strcmp(schedule_type, "dynamic") == 0) { 
            #pragma omp for schedule(dynamic, 1000) 
            for (int i = 0; i < DATA_SIZE; i++) 
                local[data[i]]++; 
 
        } else if (strcmp(schedule_type, "guided") == 0) { 
            #pragma omp for schedule(guided, 1000) 
            for (int i = 0; i < DATA_SIZE; i++) 
                local[data[i]]++; 
 
        } else { 
            if (tid == 0) 
                fprintf(stderr, "Invalid schedule_type: %s\n", schedule_type); 
        } 
 
        #pragma omp critical 
        { 
            for (int b = 0; b < BINS; b++) 
                histogram[b] += local[b]; 
        } 
    } 
 
    double end = omp_get_wtime(); 
    printf("Schedule: %s, Data size: %d, Threads: %d, Time: %.6f seconds\n", 
           schedule_type, DATA_SIZE, NUM_THREADS, end - start); 
 
    for (int i = 0; i < num_threads; i++) 
        free(local_histograms[i]); 
    free(local_histograms); 
    free(data); 
 
    return 0; 
} 
 
 
 
 
 

