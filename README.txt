REAL-TIME STUDENT ATTENDANCE TREND PREDICTION SYSTEM
====================================================

Technologies matching the first PPT:
- Python: main programming language
- Pandas: cleaning and preparing attendance records
- Scikit-learn: Linear Regression prediction model
- MySQL: database storage (optional configuration)
- Streamlit: interactive web dashboard

QUICK START (Windows)
---------------------
1. Install Python 3.10 or newer.
2. Extract this ZIP folder.
3. Open Command Prompt inside the extracted folder.
4. Run:
       py -m pip install -r requirements.txt
5. Run:
       py -m streamlit run app.py
6. The dashboard opens in your browser. If it does not, open the local URL shown in Command Prompt.

The project includes attendance_data.csv, so you can try the demo without setting up MySQL.
In local CSV demo mode, records are saved in attendance_data.csv. For MySQL storage, follow the steps below.

ENABLE MYSQL
------------
1. Start MySQL Server.
2. Open MySQL Workbench and run schema.sql.
3. Set these environment variables in Command Prompt before launching Streamlit:
       set MYSQL_HOST=localhost
       set MYSQL_USER=your_mysql_username
       set MYSQL_PASSWORD=your_mysql_password
       set MYSQL_DATABASE=attendance_trend_prediction
       set MYSQL_PORT=3306
4. Start the app:
       py -m streamlit run app.py

PREDICTION METHOD
-----------------
- The app calculates attendance percentage as:
      (classes attended / total classes) * 100
- It trains a Scikit-learn LinearRegression model using the student's week number and recorded weekly attendance percentages.
- It estimates attendance for the next week and caps the result between 0% and 100%.
- If only one weekly record exists, it uses the latest attendance as a simple estimate.
- Students predicted below the chosen required-attendance threshold are marked "At Risk".

IMPORTANT LIMITATIONS
---------------------
- The included dataset is synthetic/sample data, not real college records.
- Predictions are estimates, not guaranteed outcomes.
- The app is an academic demonstration. Validate with real historical records before using it for decisions.
- "Real-time" means the dashboard updates when records are saved or the page is refreshed; it is not a millisecond streaming system.
