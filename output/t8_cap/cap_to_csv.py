import pickle
import pandas as pd
import os

def convert_pickle_to_csv(pickle_file="qtcad_output_cap.pickle", csv_file="capacitance_matrix.csv"):
    if not os.path.exists(pickle_file):
        print(f"Error: {pickle_file} not found in current directory.")
        return

    try:
        with open(pickle_file, "rb") as f:
            data = pickle.load(f)
        
        # If it's a dictionary with tuple keys like {('A', 'B'): value}
        if isinstance(data, dict):
            # 1. Find all unique component names
            components = sorted(list(set([name for pair in data.keys() for name in pair])))
            
            # 2. Create an empty square DataFrame
            df = pd.DataFrame(index=components, columns=components)
            
            # 3. Populate the DataFrame
            for (row, col), value in data.items():
                df.loc[row, col] = value
            
            # 4. Save to CSV
            df.to_csv(csv_file)
            print(f"Success! Square capacitance matrix saved to {csv_file}")
            print("\nComponent Names found:", components)
            
        elif isinstance(data, pd.DataFrame):
            data.to_csv(csv_file)
            print(f"Success! DataFrame saved to {csv_file}")
        else:
            print("Unknown data format. Saving raw output.")
            pd.DataFrame([data]).to_csv(csv_file, index=False)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    convert_pickle_to_csv()
