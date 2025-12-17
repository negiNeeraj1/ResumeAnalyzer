"""
Extract Training Data from MySQL Database
Converts existing user_data into training dataset for ML model
"""

import pandas as pd
import pymysql
import os

def extract_training_data_from_db(
    host='localhost',
    user='root',
    password='NeerajNegi@123',
    database='cv',
    output_file='training_data.csv'
):
    """
    Extract resume data from MySQL database to create training dataset
    
    Parameters:
    - host: MySQL host
    - user: MySQL username
    - password: MySQL password
    - database: Database name
    - output_file: Output CSV filename
    """
    try:
        print("🔌 Connecting to MySQL database...")
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        print("📊 Querying user data...")
        # Query to extract resume text and predicted fields
        query = """
        SELECT 
            CONCAT(
                COALESCE(convert(Actual_skills using utf8), ''),
                ' ',
                COALESCE(convert(Recommended_skills using utf8), ''),
                ' ',
                COALESCE(Name, ''),
                ' ',
                COALESCE(Email_ID, '')
            ) as resume_text,
            convert(Predicted_Field using utf8) as job_field
        FROM user_data
        WHERE Predicted_Field IS NOT NULL 
        AND Predicted_Field != 'NA'
        AND convert(Predicted_Field using utf8) != ''
        """
        
        df = pd.read_sql(query, connection)
        connection.close()
        
        if len(df) == 0:
            print("⚠️ No data found in database. Make sure you have analyzed some resumes first.")
            return None
        
        print(f"✅ Extracted {len(df)} records")
        print(f"\n📋 Job Field Distribution:")
        print(df['job_field'].value_counts())
        
        # Clean data
        df = df.dropna(subset=['resume_text', 'job_field'])
        df = df[df['resume_text'].str.strip() != '']
        df = df[df['job_field'].str.strip() != '']
        
        # Save to CSV
        output_path = os.path.join('.', output_file)
        df.to_csv(output_path, index=False)
        print(f"\n💾 Training data saved to: {output_path}")
        print(f"📊 Total records: {len(df)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main function"""
    print("="*60)
    print("📥 Extract Training Data from Database")
    print("="*60)
    print("\nThis script extracts resume data from your MySQL database")
    print("to create a training dataset for the ML model.\n")
    
    # You can customize these values
    df = extract_training_data_from_db(
        host='localhost',
        user='root',
        password='NeerajNegi@123',  # Update with your password
        database='cv',
        output_file='training_data.csv'
    )
    
    if df is not None:
        print("\n✅ Success! You can now use this CSV file to train the model:")
        print("   python train_model.py")
        print("\n💡 Tip: Update train_model.py to use 'training_data.csv'")

if __name__ == "__main__":
    main()
