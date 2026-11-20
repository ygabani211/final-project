import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set_theme(style="whitegrid")

class FitnessTracker:
    def __init__(self, filename="fitness_activities.csv"):
        self.filename = filename
        self.columns = ['Date', 'Activity Type', 'Duration (Minutes)', 'Calories Burned']
        self.df = self.load_data()

    def load_data(self):
        """Loads, cleans, and prepares the data."""
        if os.path.exists(self.filename):
            try:
                df = pd.read_csv(self.filename)
                
                df['Date'] = pd.to_datetime(df['Date'])
                
                df['Calories per Minute'] = df['Calories Burned'] / df['Duration (Minutes)']
                return df
            except Exception as e:
                print(f"Error loading file: {e}. Creating new dataset.")
                return pd.DataFrame(columns=self.columns)
        else:
            print("Dataset not found. Starting with an empty dataset.")
            return pd.DataFrame(columns=self.columns)

    def save_data(self):
        """Saves the current DataFrame to CSV."""
        
        save_df = self.df.drop(columns=['Calories per Minute'], errors='ignore')
        
        save_df['Date'] = pd.to_datetime(save_df['Date']).dt.strftime('%Y-%m-%d')
        save_df.to_csv(self.filename, index=False)

    def log_activity(self, activity_type, duration, calories):
        """Logs a new activity with data validation using control structures."""
        # Data Validation
        if not isinstance(duration, (int, float)) or duration <= 0:
            raise ValueError("Duration must be a positive number.")
        if not isinstance(calories, (int, float)) or calories <= 0:
            raise ValueError("Calories must be a positive number.")
        if not activity_type.strip():
            raise ValueError("Activity type cannot be empty.")

        new_data = {
            'Date': datetime.now(),
            'Activity Type': activity_type.capitalize(),
            'Duration (Minutes)': duration,
            'Calories Burned': calories
        }
        
        new_row = pd.DataFrame([new_data])
        new_row['Calories per Minute'] = new_row['Calories Burned'] / new_row['Duration (Minutes)']
        
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_data()
        print(f"\nSuccessfully logged: {activity_type} for {duration} minutes.")

    def calculate_metrics(self):
        """Calculates metrics using NumPy and Pandas."""
        if self.df.empty:
            print("\nNo data available to calculate metrics.")
            return

        total_calories = np.sum(self.df['Calories Burned'].values)
        avg_duration = np.mean(self.df['Duration (Minutes)'].values)
       
        activity_freq = self.df['Activity Type'].value_counts().to_dict()

        print("\n--- Fitness Metrics ---")
        print(f"Total Calories Burned: {total_calories:.2f} kcal")
        print(f"Average Duration per Session: {avg_duration:.2f} minutes")
        print("Activity Frequency:")
        for activity, count in activity_freq.items():
            print(f"  - {activity}: {count} times")
        print("-----------------------")

    def filter_activities(self, activity_type=None, start_date=None, end_date=None):
        """Filters activities based on type or date range."""
        filtered_df = self.df.copy()

        if activity_type:
            filtered_df = filtered_df[filtered_df['Activity Type'].str.lower() == activity_type.lower()]
        
        if start_date:
            filtered_df = filtered_df[filtered_df['Date'] >= pd.to_datetime(start_date)]
            
        if end_date:
            filtered_df = filtered_df[filtered_df['Date'] <= pd.to_datetime(end_date)]

        if filtered_df.empty:
            print("\nNo activities found matching the criteria.")
        else:
            print(f"\nFound {len(filtered_df)} matching activities:")
            print(filtered_df[['Date', 'Activity Type', 'Duration (Minutes)', 'Calories Burned']].to_string(index=False))
        
        return filtered_df

    def generate_report(self):
        """Summarizes fitness data for user review."""
        if self.df.empty:
            print("\nNo data for report.")
            return
        
        print("\n===== FITNESS PROGRESS REPORT =====")
        print(f"Tracking Period: {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
        print(f"Total Sessions Logged: {len(self.df)}")
        
        summary = self.df.groupby('Activity Type').agg(
            Total_Duration=('Duration (Minutes)', 'sum'),
            Total_Calories=('Calories Burned', 'sum'),
            Avg_Calories_Per_Min=('Calories per Minute', 'mean')
        ).round(2)
        
        print("\n--- Breakdown by Activity ---")
        print(summary)
        print("===================================")

    def visualize_progress(self):
        """Creates four visualizations using Matplotlib and Seaborn."""
        if self.df.empty:
            print("\nNo data available for visualization.")
            return

        # Prepare aggregated data
        df_grouped = self.df.groupby('Activity Type').agg({
            'Duration (Minutes)': 'sum',
            'Calories Burned': 'sum'
        }).reset_index()

        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Personal Fitness Tracker Dashboard', fontsize=18, fontweight='bold')

        plt.subplot(2, 2, 1)
        sns.barplot(x='Activity Type', y='Duration (Minutes)', data=df_grouped, palette='viridis')
        plt.title('Total Time Spent per Activity')
        plt.xlabel('Activity Type')
        plt.ylabel('Duration (Minutes)')

        plt.subplot(2, 2, 2)
        
        df_sorted = self.df.sort_values('Date')
        sns.lineplot(x='Date', y='Calories Burned', data=df_sorted, marker='o', color='b')
        plt.title('Calories Burned Over Time')
        plt.xlabel('Date')
        plt.ylabel('Calories Burned')
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 3)
        plt.pie(df_grouped['Duration (Minutes)'], labels=df_grouped['Activity Type'], 
                autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        plt.title('Distribution of Activities (by Duration)')
        plt.subplot(2, 2, 4)
        corr_matrix = self.df[['Duration (Minutes)', 'Calories Burned', 'Calories per Minute']].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        plt.title('Correlation Heatmap')

        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.show()

def main():
    tracker = FitnessTracker()

    while True:
        print("\n" + "="*35)
        print("  PERSONAL FITNESS TRACKER MENU")
        print("="*35)
        print("1. Log New Activity")
        print("2. View Metrics (NumPy/Pandas)")
        print("3. Filter Activities")
        print("4. Generate Summary Report")
        print("5. Visualize Progress (Charts)")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            try:
                act_type = input("Enter Activity Type (e.g., Running, Yoga): ")
                duration = float(input("Enter Duration (Minutes): "))
                calories = float(input("Enter Calories Burned: "))
                tracker.log_activity(act_type, duration, calories)
            except ValueError as e:
                print(f"Input Error: {e}")
                
        elif choice == '2':
            tracker.calculate_metrics()
            
        elif choice == '3':
            print("\nLeave blank to skip a filter.")
            act_type = input("Filter by Activity Type: ").strip()
            start_date = input("Filter by Start Date (YYYY-MM-DD): ").strip()
            end_date = input("Filter by End Date (YYYY-MM-DD): ").strip()
            
            act_type = act_type if act_type else None
            start_date = start_date if start_date else None
            end_date = end_date if end_date else None
            
            try:
                tracker.filter_activities(act_type, start_date, end_date)
            except Exception as e:
                print(f"Error filtering: {e}")
                
        elif choice == '4':
            tracker.generate_report()
            
        elif choice == '5':
            print("Generating charts. (Close the chart window to return to the menu).")
            tracker.visualize_progress()
            
        elif choice == '6':
            print("Thank you for using the Fitness Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()