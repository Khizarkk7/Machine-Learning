import pandas as pd
from sklearn.linear_model import LinearRegression

# Sample data
data = {'Experience': [1,2,3,4,5], 'Salary': [40000,45000,50000,55000,60000]}
df = pd.DataFrame(data)

# Model 
model = LinearRegression()
model.fit(df[['Experience']], df['Salary'])

# Prediction
print("\nSalary Prediction System")
exp = float(input("Apna experience (years) enter karein: "))
predicted_salary = model.predict([[exp]])

print(f"\n{exp} saal ke experience ka predicted salary: Rs. {predicted_salary[0]:.2f}")