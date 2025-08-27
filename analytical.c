#ifndef ANALYTICAL_H
#define ANALYTICAL_H

#include <stdio.h>
#include <math.h>

/*
    Analytical procedure adapted for multiple facilities: commit 9ff14ce
*/


int is_equal_to(float value1, float value2){
    float tolerance = 0.0001;
    return (fabs(value1 - value2) < tolerance);
}

void procedure(int customer, int I, int J, int T, int *catalogs, float *coefficients, float *master_y, float *primal_x, float *dual_q, float *dual_o, float *dual_p, int *patronization, int *futurecapture, int debug){

    // Adjust customer index
    customer = customer - 1;

    // Build compatible sequence
    int sequence[T];
    for(int t = 0; t < T; t++){
        sequence[t] = 0;
        for(int i = 0; i < I; i++){
            if(is_equal_to(master_y[t * I + i], 1.)){
                sequence[t] = i + 1;
                break;
            }
        }
    }

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
                    location = sequence[t] - 1;
                    current = coefficients[s * (T+1) * I * J + t * I * J + location * J + customer];
                    current -= coefficients[l * (T+1) * I * J + t * I * J + location * J + customer];
                    current += dual_q[l];
                    if(current > dual_q[s]){
                        dual_q[s] = current;
                    }
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
                    location = sequence[t] - 1;
                    current = coefficients[s * (T+1) * I * J + t * I * J + location * J + customer];
                    current -= coefficients[l * (T+1) * I * J + t * I * J + location * J + customer];
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
                current = coefficients[0 * (T+1) * I * J + t * I * J + i * J + customer];
                current += (dual_q[t + 1] - dual_q[0]);
                dual_p[t * I + i] = current;
                for(int l = 1; l < T + 1; l++){
                    if(l < t + 1){
                        current = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer];
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
}

#endif
