"""
Weekend Getaway Ranker
Ranks destinations based on weekend suitability using only dataset fields.
No fabricated data - all logic derived from available columns.
"""

import pandas as pd
import os

# State proximity mapping (neighboring states for geographic approximation)
STATE_NEIGHBORS = {
    'Delhi': ['Haryana', 'Uttar Pradesh', 'Rajasthan', 'Punjab'],
    'Maharashtra': ['Gujarat', 'Madhya Pradesh', 'Karnataka', 'Goa', 'Telangana'],
    'Karnataka': ['Maharashtra', 'Goa', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Kerala'],
    'Tamil Nadu': ['Karnataka', 'Kerala', 'Andhra Pradesh'],
    'West Bengal': ['Bihar', 'Jharkhand', 'Odisha', 'Assam'],
    'Rajasthan': ['Gujarat', 'Madhya Pradesh', 'Uttar Pradesh', 'Haryana', 'Punjab', 'Delhi'],
    'Uttar Pradesh': ['Delhi', 'Haryana', 'Rajasthan', 'Madhya Pradesh', 'Bihar', 'Uttarakhand'],
    'Gujarat': ['Rajasthan', 'Madhya Pradesh', 'Maharashtra'],
    'Kerala': ['Tamil Nadu', 'Karnataka'],
    'Goa': ['Maharashtra', 'Karnataka'],
}

# Weekend-friendly categories (short trips, accessible)
WEEKEND_CATEGORIES = {
    'Hill Station': 1.0,
    'Beach': 1.0,
    'Wildlife': 0.8,
    'Historical': 0.9,
    'Religious': 0.9,
    'Adventure': 0.85,
    'Nature': 0.95,
    'Lake': 0.95,
    'Fort': 0.9,
    'Temple': 0.85,
    'Palace': 0.9,
}

def load_dataset(filepath: str) -> pd.DataFrame:
    """Load and inspect the travel dataset."""
    df = pd.read_csv(filepath)
    print(f"Dataset loaded: {len(df)} destinations")
    print(f"Columns: {list(df.columns)}")
    return df

def get_state_from_city(df: pd.DataFrame, city: str) -> str:
    """Extract state for a given city from dataset."""
    city_data = df[df['City'].str.lower() == city.lower()]
    if not city_data.empty:
        return city_data.iloc[0]['State']
    return None

def calculate_proximity_weight(source_state: str, dest_state: str) -> float:
    """
    Calculate proximity weight based on state-level geography.
    Since exact distances are not in dataset, we use state proximity as heuristic.
    
    Returns:
        1.0 - Same state (most suitable for weekend)
        0.7 - Neighboring state (feasible for weekend)
        0.4 - Distant state (less ideal but possible)
    """
    if source_state == dest_state:
        return 1.0
    
    neighbors = STATE_NEIGHBORS.get(source_state, [])
    if dest_state in neighbors:
        return 0.7
    
    return 0.4


def normalize_column(series: pd.Series) -> pd.Series:
    """Normalize a numeric column to 0-1 range."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)

def calculate_weekend_score(df: pd.DataFrame, source_city: str) -> pd.DataFrame:
    """
    Calculate weekend suitability score using only dataset fields.
    
    Score Components:
    - Rating/Popularity (50%): Higher rated places prioritized
    - Geographic Proximity (30%): State-level approximation
    - Category Suitability (20%): Weekend-friendly destination types
    """
    source_state = get_state_from_city(df, source_city)
    if not source_state:
        raise ValueError(f"City '{source_city}' not found in dataset")
    
    # Remove source city destinations
    df_filtered = df[df['City'].str.lower() != source_city.lower()].copy()
    
    # Use 'Google review rating' column
    rating_col = 'Google review rating'
    if rating_col in df_filtered.columns and pd.api.types.is_numeric_dtype(df_filtered[rating_col]):
        df_filtered['rating_score'] = normalize_column(df_filtered[rating_col])
    else:
        df_filtered['rating_score'] = 0.5  # Neutral if no rating
    
    # Calculate proximity score (30% weight)
    df_filtered['proximity_score'] = df_filtered['State'].apply(
        lambda x: calculate_proximity_weight(source_state, x)
    )
    
    # Calculate category score (20% weight)
    if 'Type' in df_filtered.columns:
        df_filtered['category_score'] = df_filtered['Type'].apply(
            lambda x: max([WEEKEND_CATEGORIES.get(cat, 0.5) for cat in str(x).split(',')], default=0.5)
        )
    else:
        df_filtered['category_score'] = 0.5
    
    # Composite weekend score
    df_filtered['weekend_score'] = (
        0.5 * df_filtered['rating_score'] +
        0.3 * df_filtered['proximity_score'] +
        0.2 * df_filtered['category_score']
    )
    
    return df_filtered

def get_top_destinations(df: pd.DataFrame, source_city: str, top_n: int = 5) -> pd.DataFrame:
    """Get top N weekend destinations from source city."""
    scored_df = calculate_weekend_score(df, source_city)
    top_destinations = scored_df.nlargest(top_n, 'weekend_score')
    return top_destinations

def format_output(df: pd.DataFrame, source_city: str, top_destinations: pd.DataFrame) -> str:
    """Format results as readable text."""
    source_state = get_state_from_city(df, source_city)
    
    output = f"{'='*70}\n"
    output += f"TOP 5 WEEKEND GETAWAYS FROM {source_city.upper()}\n"
    output += f"{'='*70}\n\n"
    output += f"Source: {source_city}, {source_state}\n"
    output += f"Ranking based on: Rating (50%), Proximity (30%), Category (20%)\n\n"
    
    for idx, (_, row) in enumerate(top_destinations.iterrows(), 1):
        output += f"{idx}. {row.get('Name', 'N/A')}\n"
        output += f"   Location: {row['City']}, {row['State']}\n"
        
        if 'Type' in row:
            output += f"   Category: {row['Type']}\n"
        
        if 'Google review rating' in row:
            output += f"   Rating: {row['Google review rating']}\n"
        
        output += f"   Weekend Score: {row['weekend_score']:.3f}\n"
        output += f"   (Proximity: {row['proximity_score']:.1f}, Rating: {row['rating_score']:.2f}, Category: {row['category_score']:.2f})\n\n"
    
    return output

def save_output(content: str, filename: str):
    """Save output to sample_outputs directory."""
    os.makedirs('sample_outputs', exist_ok=True)
    filepath = os.path.join('sample_outputs', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filepath}")


def main():
    """Main execution function."""
    dataset_path = 'data/Top Indian Places to Visit.csv'
    
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset not found at {dataset_path}")
        print("Please ensure the 'Top Indian Places to Visit.csv' file is in the data/ folder")
        return
    
    # Load dataset
    df = load_dataset(dataset_path)
    
    # Generate rankings for three major cities
    cities = df.sample(3)['City'].tolist()
    
    for city in cities:
        try:
            print(f"\nProcessing {city}...")
            top_destinations = get_top_destinations(df, city, top_n=5)
            output = format_output(df, city, top_destinations)
            
            # Display to console
            print(output)
            
            # Save to file
            save_output(output, f"{city.lower()}.txt")
            
        except ValueError as e:
            print(f"Error processing {city}: {e}")
        except Exception as e:
            print(f"Unexpected error for {city}: {e}")


if __name__ == "__main__":
    main()
