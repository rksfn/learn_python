"""
Exercise 2: Giving and Receiving Code Review Feedback

In this exercise, you'll practice both giving and receiving code review feedback.
The file contains a data analysis module with several functions that need review.

PART 1: You'll act as the reviewer for this code.
PART 2: You'll receive sample feedback and practice responding to it.

This exercise focuses on the communication aspects of code reviews.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from typing import Dict, List, Union, Tuple, Any, Optional


class DataAnalyzer:
    """A class for analyzing and visualizing data from CSV files."""
    
    def __init__(self, data_folder: str = 'data'):
        """
        Initialize the DataAnalyzer with a folder path.
        
        Args:
            data_folder: Path to the folder containing CSV files
        """
        self.data_folder = data_folder
        self.dataframes = {}
        self.loaded_files = []
        
    def load_data(self, filename: str) -> bool:
        """
        Load data from a CSV file into a pandas DataFrame.
        
        Args:
            filename: Name of the CSV file to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.data_folder, filename)
            
            # Extract dataset name from filename (remove .csv extension)
            dataset_name = filename.replace('.csv', '')
            
            # Load the CSV file
            df = pd.read_csv(filepath)
            
            # Store the DataFrame
            self.dataframes[dataset_name] = df
            self.loaded_files.append(filename)
            
            # Print basic info
            print(f"Loaded {filename} with {len(df)} rows and {len(df.columns)} columns")
            return True
        
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
            return False
    
    def get_dataframe(self, dataset_name: str) -> pd.DataFrame:
        """
        Get a DataFrame by name.
        
        Args:
            dataset_name: Name of the dataset (without .csv extension)
            
        Returns:
            The pandas DataFrame or None if not found
        """
        return self.dataframes.get(dataset_name)
    
    def clean_data(self, dataset_name: str) -> bool:
        """
        Clean the specified dataset by:
        1. Removing duplicate rows
        2. Removing rows with missing values
        3. Converting column names to lowercase
        
        Args:
            dataset_name: Name of the dataset to clean
            
        Returns:
            True if successful, False otherwise
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return False
        
        try:
            # Store original shape
            original_shape = df.shape
            
            # Remove duplicates
            df.drop_duplicates(inplace=True)
            
            # Remove rows with missing values
            df.dropna(inplace=True)
            
            # Convert column names to lowercase
            df.columns = [col.lower() for col in df.columns]
            
            # Update the DataFrame
            self.dataframes[dataset_name] = df
            
            # Print summary
            print(f"Cleaned {dataset_name}:")
            print(f"  Original: {original_shape[0]} rows, {original_shape[1]} columns")
            print(f"  After cleaning: {df.shape[0]} rows, {df.shape[1]} columns")
            
            return True
        
        except Exception as e:
            print(f"Error cleaning {dataset_name}: {str(e)}")
            return False
    
    def filter_data(self, dataset_name: str, column: str, value: any) -> pd.DataFrame:
        """
        Filter a dataset by a specific column and value.
        
        Args:
            dataset_name: Name of the dataset to filter
            column: Column to filter on
            value: Value to filter for
            
        Returns:
            Filtered DataFrame or None if error
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return None
        
        # Check if column exists
        if column not in df.columns:
            print(f"Column {column} not found in {dataset_name}")
            return None
        
        # Filter the data
        filtered_df = df[df[column] == value]
        return filtered_df
    
    def aggregate_data(self, dataset_name: str, group_by: str, agg_column: str, 
                       agg_function: str = 'mean') -> pd.DataFrame:
        """
        Aggregate a dataset by a specified column and aggregation function.
        
        Args:
            dataset_name: Name of the dataset to aggregate
            group_by: Column to group by
            agg_column: Column to aggregate
            agg_function: Aggregation function to use ('mean', 'sum', 'count', 'min', 'max')
            
        Returns:
            Aggregated DataFrame or None if error
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return None
        
        # Check if columns exist
        if group_by not in df.columns:
            print(f"Column {group_by} not found in {dataset_name}")
            return None
        
        if agg_column not in df.columns:
            print(f"Column {agg_column} not found in {dataset_name}")
            return None
        
        # Validate aggregation function
        valid_functions = ['mean', 'sum', 'count', 'min', 'max']
        if agg_function not in valid_functions:
            print(f"Invalid aggregation function. Must be one of: {', '.join(valid_functions)}")
            return None
        
        # Aggregate the data
        if agg_function == 'mean':
            result = df.groupby(group_by)[agg_column].mean()
        elif agg_function == 'sum':
            result = df.groupby(group_by)[agg_column].sum()
        elif agg_function == 'count':
            result = df.groupby(group_by)[agg_column].count()
        elif agg_function == 'min':
            result = df.groupby(group_by)[agg_column].min()
        elif agg_function == 'max':
            result = df.groupby(group_by)[agg_column].max()
        
        return result.reset_index()
    
    def plot_bar_chart(self, data: pd.DataFrame, x_column: str, y_column: str, 
                       title: str = None, save_path: str = None) -> None:
        """
        Create a bar chart from a DataFrame.
        
        Args:
            data: DataFrame containing the data to plot
            x_column: Column to use for x-axis
            y_column: Column to use for y-axis
            title: Chart title (optional)
            save_path: Path to save the chart image (optional)
        """
        # Check if data is valid
        if data is None or len(data) == 0:
            print("No data to plot")
            return
        
        # Check if columns exist
        if x_column not in data.columns:
            print(f"Column {x_column} not found in data")
            return
        
        if y_column not in data.columns:
            print(f"Column {y_column} not found in data")
            return
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.bar(data[x_column], data[y_column])
        
        # Add title if provided
        if title:
            plt.title(title)
        
        # Add labels
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        
        # Rotate x-axis labels if there are many categories
        if len(data) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Display the plot
        plt.show()
    
    def plot_line_chart(self, data: pd.DataFrame, x_column: str, y_column: str, 
                        title: str = None, save_path: str = None) -> None:
        """
        Create a line chart from a DataFrame.
        
        Args:
            data: DataFrame containing the data to plot
            x_column: Column to use for x-axis
            y_column: Column to use for y-axis
            title: Chart title (optional)
            save_path: Path to save the chart image (optional)
        """
        # Check if data is valid
        if data is None or len(data) == 0:
            print("No data to plot")
            return
        
        # Check if columns exist
        if x_column not in data.columns:
            print(f"Column {x_column} not found in data")
            return
        
        if y_column not in data.columns:
            print(f"Column {y_column} not found in data")
            return
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(data[x_column], data[y_column], marker='o')
        
        # Add title if provided
        if title:
            plt.title(title)
        
        # Add labels
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        
        # Rotate x-axis labels if there are many points
        if len(data) > 10:
            plt.xticks(rotation=45, ha='right')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Display the plot
        plt.show()
    
    def calculate_statistics(self, dataset_name: str, column: str) -> Dict:
        """
        Calculate basic statistics for a numeric column.
        
        Args:
            dataset_name: Name of the dataset
            column: Column to calculate statistics for
            
        Returns:
            Dictionary of statistics or None if error
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return None
        
        # Check if column exists
        if column not in df.columns:
            print(f"Column {column} not found in {dataset_name}")
            return None
        
        # Check if column is numeric
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column {column} is not numeric")
            return None
        
        # Calculate statistics
        stats = {
            'mean': df[column].mean(),
            'median': df[column].median(),
            'min': df[column].min(),
            'max': df[column].max(),
            'std': df[column].std(),
            'count': df[column].count(),
            'missing': df[column].isna().sum()
        }
        
        return stats
    
    def export_to_json(self, dataset_name: str, output_file: str) -> bool:
        """
        Export a dataset to JSON format.
        
        Args:
            dataset_name: Name of the dataset to export
            output_file: Path to the output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return False
        
        try:
            # Convert DataFrame to dict
            data_dict = df.to_dict(orient='records')
            
            # Write to JSON file
            with open(output_file, 'w') as f:
                json.dump(data_dict, f, indent=2)
            
            print(f"Exported {dataset_name} to {output_file}")
            return True
        
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
    
    def find_correlation(self, dataset_name: str, column1: str, column2: str) -> float:
        """
        Calculate the correlation between two numeric columns.
        
        Args:
            dataset_name: Name of the dataset
            column1: First column
            column2: Second column
            
        Returns:
            Correlation coefficient or None if error
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return None
        
        # Check if columns exist
        if column1 not in df.columns:
            print(f"Column {column1} not found in {dataset_name}")
            return None
        
        if column2 not in df.columns:
            print(f"Column {column2} not found in {dataset_name}")
            return None
        
        # Check if columns are numeric
        if not pd.api.types.is_numeric_dtype(df[column1]):
            print(f"Column {column1} is not numeric")
            return None
        
        if not pd.api.types.is_numeric_dtype(df[column2]):
            print(f"Column {column2} is not numeric")
            return None
        
        # Calculate correlation
        correlation = df[column1].corr(df[column2])
        return correlation
    
    def merge_datasets(self, dataset1: str, dataset2: str, on_column: str, 
                       merge_type: str = 'inner') -> str:
        """
        Merge two datasets based on a common column.
        
        Args:
            dataset1: Name of the first dataset
            dataset2: Name of the second dataset
            on_column: Column to merge on
            merge_type: Type of merge ('inner', 'left', 'right', 'outer')
            
        Returns:
            Name of the merged dataset or None if error
        """
        df1 = self.get_dataframe(dataset1)
        df2 = self.get_dataframe(dataset2)
        
        if df1 is None:
            print(f"Dataset {dataset1} not found")
            return None
        
        if df2 is None:
            print(f"Dataset {dataset2} not found")
            return None
        
        # Check if merge column exists in both datasets
        if on_column not in df1.columns:
            print(f"Column {on_column} not found in {dataset1}")
            return None
        
        if on_column not in df2.columns:
            print(f"Column {on_column} not found in {dataset2}")
            return None
        
        # Validate merge type
        valid_merge_types = ['inner', 'left', 'right', 'outer']
        if merge_type not in valid_merge_types:
            print(f"Invalid merge type. Must be one of: {', '.join(valid_merge_types)}")
            return None
        
        try:
            # Perform the merge
            merged_df = df1.merge(df2, on=on_column, how=merge_type)
            
            # Create a new dataset name
            merged_name = f"{dataset1}_{dataset2}_merged"
            
            # Store the merged dataset
            self.dataframes[merged_name] = merged_df
            
            print(f"Merged {dataset1} and {dataset2} into {merged_name}")
            print(f"  Resulting dataset has {len(merged_df)} rows and {len(merged_df.columns)} columns")
            
            return merged_name
        
        except Exception as e:
            print(f"Error merging datasets: {str(e)}")
            return None
    
    def sample_data(self, dataset_name: str, n: int = 5, random: bool = True) -> pd.DataFrame:
        """
        Get a sample of rows from a dataset.
        
        Args:
            dataset_name: Name of the dataset to sample
            n: Number of rows to sample
            random: If True, get a random sample; if False, get the first n rows
            
        Returns:
            Sampled DataFrame or None if error
        """
        df = self.get_dataframe(dataset_name)
        if df is None:
            print(f"Dataset {dataset_name} not found")
            return None
        
        if n <= 0:
            print("Sample size must be positive")
            return None
        
        if n > len(df):
            print(f"Sample size {n} is larger than dataset size {len(df)}")
            n = len(df)
            print(f"Using sample size {n} instead")
        
        if random:
            return df.sample(n)
        else:
            return df.head(n)


# Example usage
def demo_data_analyzer():
    """Run a demo of the DataAnalyzer class."""
    # Create a data folder if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create a sample CSV file for demonstration
    sample_data = pd.DataFrame({
        'ID': range(1, 101),
        'Category': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'Value': np.random.normal(100, 15, 100).round(2),
        'Date': pd.date_range(start='2023-01-01', periods=100).astype(str)
    })
    
    # Add some missing values and duplicates
    sample_data.loc[10:15, 'Value'] = np.nan
    sample_data = pd.concat([sample_data, sample_data.iloc[:5]])
    
    # Save to CSV
    sample_data.to_csv('data/sample_data.csv', index=False)
    
    # Create another sample dataset
    sample_data2 = pd.DataFrame({
        'ID': range(1, 51),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 50),
        'Sales': np.random.uniform(1000, 5000, 50).round(2),
    })
    
    # Save to CSV
    sample_data2.to_csv('data/sales_data.csv', index=False)
    
    # Initialize the analyzer
    analyzer = DataAnalyzer()
    
    # Load the data
    analyzer.load_data('sample_data.csv')
    analyzer.load_data('sales_data.csv')
    
    # Clean the data
    analyzer.clean_data('sample_data')
    
    # Get aggregate data
    agg_data = analyzer.aggregate_data('sample_data', 'Category', 'Value', 'mean')
    
    # Plot a bar chart
    if agg_data is not None:
        analyzer.plot_bar_chart(agg_data, 'Category', 'Value', 
                             'Average Value by Category')
    
    # Calculate statistics
    stats = analyzer.calculate_statistics('sample_data', 'Value')
    if stats:
        print("\nStatistics for Value column:")
        for stat, value in stats.items():
            print(f"  {stat}: {value}")
    
    # Merge datasets
    merged = analyzer.merge_datasets('sample_data', 'sales_data', 'ID')
    
    # Export to JSON
    if merged:
        analyzer.export_to_json(merged, 'data/merged_data.json')
    
    print("\nDemo completed!")


if __name__ == "__main__":
    demo_data_analyzer()


"""
PART 2: Sample Code Review Feedback

Below is sample feedback you might receive on the code above. 
Practice responding to this feedback in a constructive way:

Reviewer Comments:
-------------------

1. The DataAnalyzer class has too many responsibilities and should be split into 
   smaller classes following the Single Responsibility Principle. Consider separating 
   data loading, cleaning, analysis, and visualization into different classes.

2. There's no proper error handling in the class methods. Most just print an error 
   message and return None/False. Consider raising appropriate exceptions instead.

3. The plot_bar_chart and plot_line_chart methods are almost identical with a lot 
   of code duplication. This violates the DRY (Don't Repeat Yourself) principle.

4. The aggregate_data method uses a series of if-elif statements to choose the 
   aggregation function. This is not scalable and makes it hard to add new 
   aggregation functions. Consider using a more flexible approach.

5. There's no docstring for the class itself explaining its overall purpose and 
   how the different methods relate to each other.

6. The merge_datasets method creates a merged dataset name automatically, but this
   could lead to naming conflicts if called multiple times. Consider adding a 
   parameter to allow the user to specify the output dataset name.

7. The code doesn't have any unit tests. It would be better to include a test suite 
   to verify the functionality of the different methods.

8. The demo_data_analyzer function creates test data but doesn't clean up after 
   itself, potentially leaving unnecessary files in the filesystem.

Exercise: Write a response to each of these comments. Consider:
- Do you agree or disagree with the feedback? Why?
- How would you address each point?
- What clarification might you need from the reviewer?
- How would you prioritize these changes?
"""
