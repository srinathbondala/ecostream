from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
import pandas as pd
import numpy as np

def function1(new_product_features,new_product_type,new_product_weight):
    file_path = 'D:/eco/supply-chain-sustainability-main/stream/padding.csv'
    # Read the CSV file
    df = pd.read_csv(file_path)
    # Label encoding
    le_product = LabelEncoder()
    le_padding = LabelEncoder()
    df['product_type'] = le_product.fit_transform(df['product_type'])
    df['padding_type'] = le_padding.fit_transform(df['padding_type'])

    # Splitting data
    # Include 'weight' in your features
    X = df[['product_type', 'weight']]
    y = df['padding_type']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Define the parameter grid for GridSearchCV
    param_grid = {
        'max_depth': [2, 4, 8],
        'min_samples_split': [2, 5, 10],
        'criterion': ['gini', 'entropy']
    }

    # Create a DecisionTreeClassifier object
    clf = DecisionTreeClassifier()

    # Use GridSearchCV to find the best hyperparameters
    grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, cv=2)
    grid_search.fit(X_train, y_train)

    # Get the best model and its parameters
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_

    # Print the best parameters found
    print("Best Hyperparameters:", best_params)

    # Make predictions using the best model
    padding_prediction = best_model.predict(X_test)

    # further evaluate the model performance here using metrics like accuracy score
    # from sklearn.metrics import accuracy_score
    # accuracy = accuracy_score(y_test, padding_prediction)
    # print("Accuracy:", accuracy)

    new_product_type_transformed = le_product.transform([new_product_type]).reshape(-1, 1)
    new_product_features = np.hstack([new_product_type_transformed, [[new_product_weight]]])  # include weight in features
    predicted_padding = best_model.predict(new_product_features)
    predicted_padding_name = le_padding.inverse_transform(predicted_padding)[0]

    print(f"Predicted padding type for '{new_product_type}' with weight {new_product_weight}: {predicted_padding_name}")
    return predicted_padding_name


def function2(new_product,predicted_padding_name):
    file_path = 'D:/eco/supply-chain-sustainability-main/stream/padding.csv'
    # Read the CSV file
    df = pd.read_csv(file_path)
    # Label encoding
    le_product = LabelEncoder()
    df['product_type'] = le_product.fit_transform(df['product_type'])

    # Add this line to encode 'padding_type'
    le_padding = LabelEncoder()
    df['padding_type'] = le_padding.fit_transform(df['padding_type'])

    # Splitting data
    # Include all relevant features
    features = ['product_type', 'weight', 'padding_type', 'length', 'width', 'height', 'surface_area', 'volume', 'padding_thickness']
    X = df[features]

    # Create two models, one for each target variable
    targets = ['diff_volume', 'new_surface_area']
    models = {}

    for target in targets:
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        # Define the parameter grid for GridSearchCV
        param_grid = {
            'max_depth': [2, 4, 8],
            'min_samples_split': [2, 5, 10]
        }

        # Create a DecisionTreeRegressor object
        reg = DecisionTreeRegressor()

        # Use GridSearchCV to find the best hyperparameters
        grid_search = GridSearchCV(estimator=reg, param_grid=param_grid, cv=2)
        grid_search.fit(X_train, y_train)

        # Get the best model and its parameters
        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_

        # Print the best parameters found
        print(f"Best Hyperparameters for {target}:", best_params)

        # Store the model for later use
        models[target] = best_model

    # Now you can use models['diff_volume'] and models['new_surface_area'] to make predictions
    # new_product = {
    #     'product_type': 'electronics',  # example product type
    #     'weight': 25.63,  # example weight
    #     'padding_type': predicted_padding_name,  # example padding type
    #     'length': 0.51,  # example length
    #     'width': 0.05,  # example width
    #     'height': 0.05,  # example height
    #     'surface_area': 0.107,  # example surface area
    #     'volume': 0.001275,  # example volume
    #     'padding_thickness': 0.12815  # example padding thickness
    # }
    new_product.update({'padding_type': predicted_padding_name})
    # Transform the product type and padding type to their encoded forms
    new_product['product_type'] = le_product.transform([new_product['product_type']])[0]
    new_product['padding_type'] = le_padding.transform([new_product['padding_type']])[0]

    # Extract the features in the same order as was used for training
    new_product_features = [new_product[feature] for feature in features]


    # Make predictions
    for target, model in models.items():
        prediction = model.predict([new_product_features])[0]
        return f"Predicted padding volume for new product: {prediction}"
