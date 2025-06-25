from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Model train karein
data = {'Experience': [1,2,3,4,5], 'Salary': [40000,45000,50000,55000,60000]}
df = pd.DataFrame(data)
model = LinearRegression()
model.fit(df[['Experience']], df['Salary'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Form se input lein
        experience = float(request.form['experience'])
        
        # Prediction karein
        prediction = model.predict([[experience]])[0]
        
        # Result ko HTML mein bhejein
        return render_template('result.html', 
                             experience=experience,
                             prediction=round(prediction,2))

if __name__ == '__main__':
    app.run(debug=True)