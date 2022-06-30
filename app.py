import pickle, bz2
from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from logger.app_logger import logger
from config.mongodb import mongodbconnection
import warnings
warnings.filterwarnings("ignore")


app = Flask(__name__)

# Import Classification and Regression model file
pickle_in = bz2.BZ2File('classification.pkl', 'rb')
R_pickle_in = bz2.BZ2File('regression.pkl', 'rb')
model_C = pickle.load(pickle_in)
model_R = pickle.load(R_pickle_in)

# Data retrieved from DB using mongoconnection module
dbcon = mongodbconnection(username='admin', password='admin')
list_cursor = dbcon.getdata(dbName='FireDataML', collectionName='ml_task')
logger.info('Connected to Mongodb and data retrieved')

# Data From MongoDB is used for Standardization
df = pd.DataFrame(list_cursor)
df.drop('_id', axis=1, inplace=True)
logger.info('DataFrame created')
scaler = StandardScaler()
X = df.drop(['FWI', 'Classes'], axis=1)
# Standardize
X_reg_scaled = scaler.fit_transform(X)
logger.info('Standardization done')
 


# Route for homepage
@app.route('/')
def home():
    logger.info('Home page loaded successfully')
    return render_template('index.html')


# Route for API Testing
@app.route('/predict_api', methods=['POST'])
def predict_api():
    try:
        data = request.json['data']
        print(data)
        logger.info('Input from Api testing', data)
        new_data = [list(data.values())]
        final_data = scaler.transform(new_data)
        output = int(model_C.predict(final_data)[0])
        if output == 1:
            text = 'The Forest in Danger'
        else:
            text = 'Forest is Safe'
        return jsonify(text, output)
    except Exception as e:
        output = 'Check the in input again!'
        logger.error('error in input from Postman', e)
        return jsonify(output)


# Route for Classification Model
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # convert string to float
        data = [float(x) for x in request.form.values()]
        print('Data -->', np.array(data))
        final_features = [np.array(data)]
        print
        final_features = scaler.transform(final_features)
        output = model_C.predict(final_features)[0]
        logger.info('Prediction done for Classification model')
        if output == 0:
            text = 'Forest is Safe!'
        else:
            text = 'Forest is in Danger!'
        return render_template('index.html', prediction_text1="{} --- Chance of Fire is {}".format(text, output))
    except Exception as e:
        logger.error('Input error, check input', e)
        return render_template('index.html', prediction_text1="Check the Input again!!!")


# Route for Regression Model
@app.route('/predictR', methods=['POST'])
def predictR():
    try:
        data = [float(x) for x in request.form.values()]
        data = [np.array(data)]
        data = scaler.transform(data)
        output = model_R.predict(data)[0]
        logger.info('Prediction done for Regression model')
        if output > 15:
            return render_template('index.html', prediction_text2="Fuel Moisture Code index is {:.4f} ---- Warning!!! High hazard rating".format(output))
        else:
            return render_template('index.html', prediction_text2="Fuel Moisture Code index is {:.4f} ---- Safe.. Low hazard rating".format(output))
    except Exception as e:
        logger.error('Input error, check input', e)
        return render_template('index.html', prediction_text2="Check the Input again!!!")


# Run APP in Debug mode
if __name__ == "__main__":
    app.run(debug=True)
