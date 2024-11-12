import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

# Load and preprocess the traffic log data
def load_data(file_path):
    # Load datav vrvg
    data = pd.read_csv(file_path)

    # Ensure the 'Timestamp' column is in datetime format
    if 'Timestamp' not in data.columns:
        raise ValueError("Missing 'Timestamp' column in the dataset.")
    
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')

    # Calculate the time difference between consecutive requests
    data['inter_request_time'] = data['Timestamp'].diff().dt.total_seconds().fillna(0)
    
    # Check if 'request_rate' exists, if not, calculate it
    if 'request_rate' not in data.columns:
        print("Warning: 'request_rate' column not found. Calculating 'request_rate' as 1 / inter_request_time.")
        data['request_rate'] = 1 / data['inter_request_time']
    
    # Calculate the rolling mean for 'request_rate'
    data['rolling_mean_rate'] = data['request_rate'].rolling(window=10).mean()
    
    # Handle missing values (NaN) in 'rolling_mean_rate' and 'request_rate'
    data['rolling_mean_rate'].fillna(data['rolling_mean_rate'].mean(), inplace=True)
    data['request_rate'].fillna(data['request_rate'].mean(), inplace=True)
    
    return data

# Anomaly detection with Isolation Forest
def detect_anomalies(data):
    features = ['rolling_mean_rate']
    model = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
    
    # Ensure there are no NaN values before fitting the model
    data_clean = data.dropna(subset=features)
    
    data_clean['anomaly'] = model.fit_predict(data_clean[features])
    
    # Define attack type based on thresholds
    data_clean['attack_type'] = data_clean.apply(
        lambda x: 'High-Rate DDoS' if x['rolling_mean_rate'] > 750 else (
            'Low-Rate DDoS' if 100 < x['rolling_mean_rate'] <= 750 else 'No Attack'), axis=1
    )
    
    return data_clean
# Check high-rate attack instances and request_rate distribution
def visualize_results(data):
    
    # Count the instances of each attack type
    high_rate_attacks = data[(data['attack_type'] == 'High-Rate DDoS') & (data['request_rate'] > 750)]
    
    low_rate_attacks = data[(data['attack_type'] == 'Low-Rate DDoS') & (data['request_rate'] <= 750) & (data['request_rate'] > 100)]
    
    # If High-Rate DDoS has more than 20 instances, plot High-Rate graph only
    if len(high_rate_attacks) > 10:
        plt.figure(figsize=(10, 5))
        plt.plot(data['Timestamp'], data['request_rate'], color='blue', alpha=0.3, label='Request Rate')
        plt.scatter(high_rate_attacks['Timestamp'], high_rate_attacks['request_rate'], color='red', label='High-Rate DDoS Attack', s=50)
        plt.title('High-Rate DDoS Attacks with Request Rate > 750')
        plt.xlabel('Time')
        plt.ylabel('Request Rate')
        plt.legend()
        plt.show()
        
    
    # If Low-Rate DDoS has more instances, plot Low-Rate graph
    elif len(low_rate_attacks) > len(high_rate_attacks):
        plt.figure(figsize=(10, 5))
        plt.plot(data['Timestamp'], data['request_rate'], color='blue', alpha=0.3, label='Request Rate')
        plt.scatter(low_rate_attacks['Timestamp'], low_rate_attacks['request_rate'], color='orange', label='Low-Rate DDoS Attack', s=50)
        plt.title('Low-Rate DDoS Attacks with Request Rate Between 100 and 750')
        plt.xlabel('Time')
        plt.ylabel('Request Rate')
        plt.legend()
        plt.show()

    # If no attacks, only plot the Request Rate
    else:
        plt.figure(figsize=(14, 6))
        plt.plot(data['Timestamp'], data['request_rate'], label='Request Rate', color='blue')
        plt.title('Request Rate Over Time (No DDoS Attack Detected)')
        plt.xlabel('Time')
        plt.ylabel('Request Rate')
        plt.legend()
        plt.show()

# Main function to load data, detect anomalies, and visualize results
def main(file_path):
    data = load_data(file_path)
    data_clean = detect_anomalies(data)
    
    # Display High-Rate DDoS summary with sample instances
    high_rate_summary = data_clean[data_clean['attack_type'] == 'High-Rate DDoS']
    print("High-Rate DDoS Attack Summary:")
    print(f"Total High-Rate DDoS Instances: {len(high_rate_summary)}")
    print("Sample Instances of High-Rate DDoS Attacks:")
    print(high_rate_summary[['Timestamp', 'request_rate', 'rolling_mean_rate']].head())  # Show a few instances

    # If High-Rate DDoS instances are more than 20, skip low-rate DDoS summary
    if len(high_rate_summary) > 20:
        visualize_results(data_clean)
        return

    # Display Low-Rate DDoS summary with sample instances
    low_rate_summary = data_clean[data_clean['attack_type'] == 'Low-Rate DDoS']
    print("\nLow-Rate DDoS Attack Summary:")
    print(f"Total Low-Rate DDoS Instances: {len(low_rate_summary)}")
    print("Sample Instances of Low-Rate DDoS Attacks:")
    print(low_rate_summary[['Timestamp', 'request_rate', 'rolling_mean_rate']].head())  # Show a few instances

    # Visualize results
    visualize_results(data_clean)

# Run main function with the path to traffic log
if __name__ == '__main__':
    main('traffic_log.csv')

