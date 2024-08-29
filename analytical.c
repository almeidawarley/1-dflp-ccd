#ifndef ANALYTICAL_H
#define ANALYTICAL_H

#include<stdio.h>

int procedure(int I, int J, int T, int *catalogs, float *rewards, int *accumulated, int customer, int *sequence, float * dual_q, float * dual_p, int debug){

    if(debug == 1){

        printf("Analytical procedure\n");
        printf("Running it for customer %d\n", customer);

        printf("Data summary dump: \n");

        // Input sets: I, J, and T
        printf("# locations: %d\n", I);
        printf("# customers: %d\n", J);
        printf("# periods: %d\n", T);

        // Catalogs: a_{ij}
        for(int j = 0; j < J; j++){
            printf("Customer %d is willing to attend: ", j + 1);
            for(int i = 0; i < I; i++){
                if(catalogs[i * I + j] == 1){
                    printf("%d, ", i + 1);
                }
            }
            printf("\n");
        }

        // Rewards: r^{t}_{i}
        for(int i = 0; i < I; i++){
            printf("Location %d has a reward of %f\n", i + 1, rewards[i]);
        }

        // Accumulated demand: D^{lt}_{j}
        for(int j = 0; j < J; j++){
            printf("Accumulated demand for customer %d: ", j + 1);
            for(int l = 0; l < T + 1; l++){
                for(int t = 0; t < T; t++){
                    if(l < t + 1){
                        printf("%d [%d -> %d], ", accumulated[l * T * J + t * J + j], l, t + 1);
                    }
                }
            }
            printf("\n");
        }

        // Location sequence: y^{t}_{i}
        for(int t = 0; t < T; t++){
            printf("Provider installs location %d at time period %d\n", sequence[t], t + 1);
        }
    }

    // Adjust customer index
    customer = customer - 1;

    // Solve the primal problem
    int primal_solution[T + 1];
    for(int l = 0; l < T + 1; l++){
        primal_solution[l] = T; // finish = T
        for(int t = 0; t < T; t++){
            if((l < t + 1) && (sequence[t] != 0 && catalogs[(sequence[t] - 1) * J + customer] == 1)){
                primal_solution[l] = t;
                break;
            }
        }
    }

    /*
    printf("Primal solution for customer %d:\n", customer + 1);
    for(int l = 0; l < T + 1; l++){
        printf("From time period %d, next capture is at time period %d\n", l, primal_solution[l] + 1);
    }
    */

    int location = 0;
    float current = 0.0;

    // First loop, captured periods
    for (int s = T; s >= 0; s--){
        dual_q[s] = 0.0;
        for(int l = 0; l < T + 1; l++){
            for(int t = 0; t < T; t++){
                if((primal_solution[l] == t) && (primal_solution[s] != t) && (l != s) && (s < t + 1)){
                    // printf("1st: l = %d, s = %d, t = %d\n", l, s, t + 1);
                    location = sequence[t] - 1;
                    // printf("rewards R: %f\n", rewards[t * I + location]);
                    // printf("demands A: %d\n", accumulated[s * T * J + t * J + customer]);
                    // printf("demands B: %d\n", accumulated[l * T * J + t * J + customer]);
                    current = rewards[t * I + location] * accumulated[s * T * J + t * J + customer];
                    current -= rewards[t * I + location] * accumulated[l * T * J + t * J + customer];
                    current += dual_q[l];
                    // printf("current: %f\n", current);
                    if(current > dual_q[s]){
                        dual_q[s] = current;
                    }
                    // printf("dual_q[s]: %f\n", dual_q[s]);
                }
            }
        }
    }

    // First loop, free periods
    for (int s = T; s >= 0; s--){
        // dual_q[s] = 0.0;
        for(int l = 0; l < T + 1; l++){
            for(int t = 0; t < T; t++){
                if((primal_solution[l] == t) && (primal_solution[s] == t) && (l != s) && (s < t + 1)){
                    // printf("2nd: l = %d, s = %d, t = %d\n", l, s, t + 1);
                    location = sequence[t] - 1;
                    current = rewards[t * I + location] * accumulated[s * T * J + t * J + customer];
                    current -= rewards[t * I + location] * accumulated[l * T * J + t * J + customer];
                    current += dual_q[l];
                    if(current > dual_q[s]){
                        dual_q[s] = current;
                    }
                }
            }
        }
    }

    float dual_objective = dual_q[0];

    // Second loop
    for(int t = 0; t < T; t++){
        for(int i = 0; i < I; i++){
            if(catalogs[i * J + customer] == 1){
                current = rewards[t * I + i] * accumulated[0 * T * J + t * J + customer];
                current += (dual_q[t + 1] - dual_q[0]);
                dual_p[t * I + i] = current;
                for(int l = 1; l < T + 1; l++){
                    if(l < t + 1){
                        current = rewards[t * I + i] * accumulated[l * T * J + t * J + customer];
                        current += (dual_q[t + 1] - dual_q[l]);
                        if(current > dual_p[t * I + i]){
                            dual_p[t * I + i] = current;
                        }
                    }
                    if(sequence[t] == i + 1){
                        dual_objective += dual_p[t * I + i];
                    }
                }
            }
        }
    }

    /*
    for(int l = 0; l < T + 1; l++){
        printf("%f, ", dual_q[l]);
    }
    printf("\n");

    for(int t = 0; t < T; t++){
        for(int i = 0; i < I; i++){
            if(catalogs[i * J + customer] == 1){
                printf("%f, ", dual_p[t * I + i]);
            }
        }
    }
    printf("\n");
    */

    return dual_objective;
}

#endif
