"""
Dataset Inspector
Quick utility to examine the Kaggle dataset structure and contents.
Run this first to verify your dataset before running the ranker.
"""

import pandas as pd

def inspect_dataset():
    """Inspect the travel dataset and display key information."""
    
    dataset_path = 'data/Top Indian Places to Visit.csv'
    
    print("[OK] Dataset found! Loading...\n")
    
    # Load dataset
    df = pd.read_csv(dataset_path)
    
    # Basic info
    print("="*70)
    print("DATASET OVERVIEW")
    print("="*70)
    print(f"Total destinations: {len(df)}")
    print(f"Total columns: {len(df.columns)}\n")
    
    # Column names and types
    print("="*70)
    print("COLUMNS")
    print("="*70)
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        print(f"  {col:25} | Type: {str(dtype):10} | Non-null: {non_null:4} | Null: {null_count:4}")
    
    # Sample data
    print("\n" + "="*70)
    print("SAMPLE DATA (First 3 rows)")
    print("="*70)
    print(df.head(3).to_string())
    
    # Unique values for key columns
    print("\n" + "="*70)
    print("UNIQUE VALUES")
    print("="*70)
    
    if 'State' in df.columns:
        print(f"\nUnique States ({df['State'].nunique()}):")
        print(df['State'].value_counts().head(10).to_string())
    
    if 'City' in df.columns:
        print(f"\n\nUnique Cities ({df['City'].nunique()}):")
        print(df['City'].value_counts().head(10).to_string())
    
    if 'Type' in df.columns:
        print(f"\n\nDestination Types ({df['Type'].nunique()}):")
        print(df['Type'].value_counts().head(10).to_string())
    
    # Check for rating columns
    print("\n" + "="*70)
    print("RATING INFORMATION")
    print("="*70)
    rating_cols = [col for col in df.columns if 'rating' in col.lower() or 'significance' in col.lower()]
    if rating_cols:
        for col in rating_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                print(f"\n{col}:")
                print(f"  Min: {df[col].min()}")
                print(f"  Max: {df[col].max()}")
                print(f"  Mean: {df[col].mean():.2f}")
                print(f"  Median: {df[col].median():.2f}")
    else:
        print("[WARNING] No obvious rating columns found")
    
    # Check for city coverage
    print("\n" + "="*70)
    print("CITY COVERAGE CHECK")
    print("="*70)
    
    if 'City' in df.columns:
        cities = sorted(df['City'].dropna().unique().tolist())
        print(f"Found {len(cities)} unique cities:")
        print("-" * 40)
        
        for city in cities:
            count = df[df['City'].str.contains(city, case=False, na=False)].shape[0]
            print(f"[OK] {city}: {count} destinations")
    else:
        print("[ERROR] 'City' column not found in dataset")
    
    print("\n" + "="*70)
    print("DATASET READY FOR RANKING!")
    print("="*70)
    print("\nNext step: Run 'python ranker.py' to generate weekend rankings\n")


if __name__ == "__main__":
    inspect_dataset()
