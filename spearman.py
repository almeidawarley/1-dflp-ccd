import pandas as pd
from scipy.stats import spearmanr

# Load the dataset
file_path = "results/paper1/summary.csv"  # Replace with the correct file path
data = pd.read_csv(file_path)

# Columns to encode (categorical)
categorical_columns = ['rewards', 'preferences', 'demands']

# Encode categorical columns using pandas' factorize method
for col in categorical_columns:
    data[col] = pd.factorize(data[col])[0]

# Columns for correlation computation
attributes = ['locations', 'customers', 'periods', 'facilities'] + categorical_columns
runtimes = ['cold_lrz_runtime', 'cold_net_runtime', 'bbd_runtime']

# Compute Spearman correlations
correlation_results = {
    runtime: {attr: spearmanr(data[attr], data[runtime])[0] for attr in attributes}
    for runtime in runtimes
}

# Convert to DataFrame for readability
correlation_df = pd.DataFrame(correlation_results)

# Save the results to a CSV file (optional)
output_path = "spearman_correlations.csv"
correlation_df.to_csv(output_path)

# Print the results
print("Spearman's correlation coefficients:")
print(correlation_df)