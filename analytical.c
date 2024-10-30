#ifndef ANALYTICAL_H
#define ANALYTICAL_H

#include <stdio.h>
#include <math.h>


int is_equal_to(float value1, float value2){
    float tolerance = 0.0001;
    return (fabs(value1 - value2) < tolerance);
}

void procedure(int customer, int I, int J, int T, int *catalogs, float *coefficients, float *master_y, float *primal_x, float *dual_q, float *dual_o, float *dual_p, int *patronization, int *futurecapture, int debug){

    // char dump;
    debug = 2;
    if(debug == 1){

        printf("Analytical procedure\n");

        printf("Running customer %d\n", customer);

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

        // Coefficients: G^{lt}_{ij}
        for(int j = 0; j < J; j++){
            printf("Coefficients for customer %d: ", j + 1);
            for(int l = 0; l < T + 1; l++){
                for(int t = 0; t < T + 1; t++){
                    for(int i = 0; i < I; i++){
                        if(l < t + 1 && catalogs[i * J + j] == 1){
                            printf("[%d -> %d, %d] = %f, ", l, t + 1, i + 1, coefficients[l * (T+1) * I * J + t * I * J + i * J + j]);
                        }
                    }
                }
            }
            printf("\n");
        }

        // Master solution: y^{t}_{i}
        for(int t = 0; t < T; t++){
            printf("Locations for time period %d: ", t + 1);
            for(int i = 0; i < I; i++){
                if(master_y[t * I + i] > 0.){
                    printf("%d [= %f], ", i + 1, master_y[t * I + i]);
                }
            }
            printf("\n");
        }

        // Master solution: y^{t}_{i}
        for(int t = 0; t < T; t++){
            printf("Locations for time period %d: ", t + 1);
            for(int i = 0; i < I; i++){
                if(master_y[t * I + i] > 0.){
                    printf("%d [= %f], ", i + 1, master_y[t * I + i]);
                }
            }
            printf("\n");
        }
    }

    // Adjust customer index
    customer = customer - 1;

    /*
    // Solve the primal problem
    // Variables: x^{lt}_{ij}
    for(int l = 0; l < T + 1; l++){
        for(int t = l; t < T + 1; t++){
            // Capturing flag
            int captured = 0;
            int location = -1;
            int transition = -1 * INFINITY;
            for(int i = 0; i < I; i++){
                primal_x[l * (T + 1) * I + t * I + i] = 0;
                if(t == T || (master_y[t * I + i]  > 0 && catalogs[i * J + customer] == 1)){
                    captured = 1;
                    if(coefficients[l * (T+1) * I * J + t * I * J + i * J + customer] > transition){
                        transition = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer];
                        location = i;
                    }
                }
            }
            if(captured == 1){
                primal_x[l * (T + 1) * I + t * I + location] = 1;
                printf("Customer %d captured by location %d [%d -> %d]\n", customer + 1, location + 1, l, t + 1);
                l = t;
                break;
            }
        }
    }
    */

    // Patronization pattern
    // int patronization[T + 1];
    // Future capture pattern
    // int futurecapture[T + 1];
    int placeholder = -2;
    int uncaptured = -1;
    int finalperiod = T + 1;
    for(int l = 0; l < T + 1; l++){
        patronization[l] = uncaptured;
        futurecapture[l] = finalperiod;
    }
    // Customer captured at t = 0
    patronization[0] = placeholder;

    // Compute proper values
    int captured, location;
    float transition;
    for(int l = 0; l < T + 1; l++){
        for(int t = l; t < T; t++){
            captured = 0;
            location = -1;
            transition = -1 * INFINITY;
            for(int i = 0; i < I; i++){
                if(is_equal_to(master_y[t * I + i], 1.) && catalogs[i * J + customer] == 1){
                    captured = 1;
                    if(coefficients[l * (T+1) * I * J + t * I * J + i * J + customer] > transition){
                        transition = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer];
                        location = i;
                    }
                }
            }
            if(captured == 1){
                patronization[t + 1] = location;
                futurecapture[l] = t + 1;
                l = t;
                break;
            }
        }
    }

    if(debug == 1){
        // Print patronization pattern
        for(int l = 0; l < T + 1; l++){
            if(patronization[l] != uncaptured && patronization[l] != placeholder){
                printf("Customer %d captured by location %d at time period %d\n", customer + 1, patronization[l] + 1, l);
            }
        }

        // Print future capture pattern
        for(int l = 0; l < T + 1; l++){
            if(futurecapture[l] != finalperiod){
                printf("Customer %d in transition from time period %d to time period %d\n", customer + 1, l, futurecapture[l]);
            }
        }
    }

    // Reset variables
    dual_q[T] = 0.0;
    for(int t = 0; t < T; t++){
        dual_q[t] = 0.0;
        for(int i = 0; i < I; i++){
            dual_o[t * I + i] = 0.0;
            dual_p[t * I + i] = 0.0;
        }
    }

    // Compute dual_q, CAPTURED
    float maximum, candidate, summing_p, offset, guarantee;
    for(int l = T; l >= 0; l--){
        if(patronization[l] != uncaptured){
            // printf("Computing q^{%d}, captured\n", l);
            maximum = -1 * INFINITY;
            for(int i = 0; i < I; i++){
                if(catalogs[i * J + customer] == 1){
                    // Final period
                    candidate = coefficients[l * (T+1) * I * J + (T) * I * J + i * J + customer];
                    if(candidate > maximum){
                        maximum = candidate;
                        // printf("Updating1 to %f\n", candidate);
                    }
                    // Other periods
                    for(int t = l; t < T; t++){
                        if(is_equal_to(master_y[t * I + i], 1.)){
                            summing_p = 0;
                            for(int k = 0; k < I; k++){
                                summing_p += dual_p[t * I + k];
                            }
                            candidate = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer] + summing_p + dual_q[t + 1];
                            // printf("Coefficient: %f\n", coefficients[l * (T+1) * I * J + t * I * J + i * J + customer]);
                            // printf("Summing p: %f\n", summing_p);
                            // printf("Dual q: %f\n", dual_q[t + 1]);
                            if(candidate > maximum){
                                maximum = candidate;
                                // printf("Updating2 to %f (%d, %d)\n", candidate, t + 1, i + 1);
                            }
                        }
                    }
                }
            }
            dual_q[l] = maximum;
            // printf("Setting q^{%d} = %f\n", l, dual_q[l]);

            if(futurecapture[l] != finalperiod){
                // Adjust dual_p
                // Futurecapture indexed from 0 to T
                // Patronization indexed from 0 to T
                offset = 0.;
                for(int t = l; t < T; t++){
                    for(int k = 0; k < I; k++){
                        if(is_equal_to(master_y[t * I + k], 1.)){
                            offset += dual_p[t * I + k];
                        }
                    }
                }
                guarantee = 0.;
                int s = l;
                int tr = futurecapture[l];
                int i = patronization[tr];
                // printf("Computing p~%d_%d\n", tr, i + 1);
                // printf("Offset: %f\n", offset);
                while(tr != finalperiod){
                    i = patronization[tr];
                    guarantee += coefficients[s * (T+1) * I * J + (tr - 1) * I * J + i * J + customer];
                    // printf("Adding %f (%d, %d) to guarantee\n", coefficients[s * (T+1) * I * J + (tr - 1) * I * J + i * J + customer], tr, i + 1);
                    s = tr;
                    tr = futurecapture[tr];
                }
                // Add transition to final period
                guarantee += coefficients[s * (T+1) * I * J + (tr - 1) * I * J + i * J + customer];
                // printf("Guarantee: %f\n", guarantee);
                tr = futurecapture[l];
                i = patronization[tr];
                // printf("q~%d: %f\n", l, dual_q[l]);
                dual_p[(tr - 1) * I + i] = dual_q[l] - offset - guarantee;
                // printf("Setting p~%d_%d = %f\n", tr, i + 1, dual_p[(tr - 1) * I + i]);
                // scanf("%c", &dump);
            }
        }
    }

    // Compute dual_q, UNCAPTURED
    for(int l = T; l >= 0; l--){
        if(patronization[l] == uncaptured){
            // printf("Computing q^{%d}, uncaptured\n", l);
            maximum = -1 * INFINITY;
            for(int i = 0; i < I; i++){
                if(catalogs[i * J + customer] == 1){
                    // Final period
                    candidate = coefficients[l * (T+1) * I * J + (T) * I * J + i * J + customer];
                    if(candidate > maximum){
                        maximum = candidate;
                        // printf("Updating1 to %f\n", candidate);
                    }
                    // Other periods
                    for(int t = l; t < T; t++){
                        if(is_equal_to(master_y[t * I + i], 1.)){
                            summing_p = 0;
                            for(int k = 0; k < I; k++){
                                summing_p += dual_p[t * I + k];
                            }
                            candidate = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer] + summing_p + dual_q[t + 1];
                            if(candidate > maximum){
                                maximum = candidate;
                                // printf("Updating2 to %f\n", candidate);
                            }
                        }
                    }
                }
            }
            dual_q[l] = maximum;
        }
    }

    for(int t = 0; t < T; t++){
        for(int i = 0; i < I; i++){
            if(catalogs[i * J + customer] == 1){
                if(is_equal_to(master_y[t * I + i], 0.)){
                    // printf("Computing o^{%d}_{%d}\n", t + 1, i + 1);
                    summing_p = 0;
                    for(int k = 0; k < I; k++){
                        summing_p += dual_p[t * I + k];
                    }
                    for(int l = 0; l < T + 1; l++){
                        if(l < t + 1){
                            candidate = coefficients[l * (T+1) * I * J + t * I * J + i * J + customer] - dual_q[l] + dual_q[t + 1] + summing_p;
                            if(candidate > dual_o[t * I + i]){
                                dual_o[t * I + i] = candidate;
                                // printf("Updating3 to %f\n", candidate);
                            }
                        }
                    }
                    // printf("Setting o^{%d}_{%d} = %f\n", t + 1, i + 1, dual_o[t * I + i]);
                }
            }
        }
    }

    if(debug == 1){

        // Compute dual objective
        summing_p = 0;
        for(int t = 0; t < T; t++){
            if(patronization[t] != uncaptured){
                summing_p += dual_p[t * I + patronization[t]];
            }
        }
        float dual_objective = dual_q[0] - summing_p;

        printf("Dual objective: %f\n", dual_objective);
        for(int t = 0; t < T; t++){
            for(int i = 0; i < I; i++){
                if(catalogs[i * J + customer] == 1){
                    // printf("p^{%d}_{%d} = %.1f\n", t + 1, i + 1, dual_p[t * I + i]);
                    printf("p~%d_%d %.1f\n", t + 1, i + 1, dual_p[t * I + i]);
                }
            }
        }
        for(int l = 0; l < T + 1; l++){
            // printf("q^{%d} = %.1f\n", l, dual_q[l]);
            printf("q~%d %.1f\n", l, dual_q[l]);
        }
        for(int t = 0; t < T; t++){
            for(int i = 0; i < I; i++){
                if(catalogs[i * J + customer] == 1){
                    // printf("o^{%d}_{%d} = %.1f\n", t + 1, i + 1, dual_o[t * I + i]);
                    printf("o~%d_%d %.1f\n", t + 1, i + 1, dual_o[t * I + i]);
                }
            }
        }
    }

    // printf("Returning %f\n", dual_objective);
}

#endif
