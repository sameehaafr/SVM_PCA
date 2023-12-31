import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from sklearn.datasets import load_breast_cancer
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
from sklearn.metrics  import precision_score, recall_score
from sklearn.metrics import accuracy_score, classification_report


# Load the data

def load_data():
    tumor_df = load_breast_cancer()
    df = pd.DataFrame(tumor_df.data, columns=tumor_df.feature_names)
    df['target'] = tumor_df.target
    return df

# Split the data

def split_data(df):
    X = df.drop(['target'], axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=105)
    X_train_scaled = scale(X_train)
    X_test_scaled = scale(X_test)
    return X_train_scaled, X_test_scaled, y_train, y_test

def build_svm(C, gamma, kernel, X_train_scaled, y_train):
    svm = SVC(C=C, gamma=gamma, kernel=kernel, random_state=30)
    svm.fit(X_train_scaled,y_train)
    return svm

# Evaluate the basic SVM model
def show_confusion_matrix(clf_svm, X_test_scaled, y_test):
    class_labels = ['Malignant', 'Benign']
    cm = confusion_matrix(y_test, clf_svm.predict(X_test_scaled))
    fig, ax = plt.subplots(figsize=(6, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=class_labels, yticklabels=class_labels, ax=ax)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    st.pyplot(fig)

# Use GridSearchCV to find the best parameters
def find_best_params(X_train_scaled, y_train):
    param_grid = [
        {'C': [0.5, 1, 10, 100],
        'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.0001],
        'kernel': ['rbf']}
        ]

    optimal_params = GridSearchCV(
        SVC(),
        param_grid,
        cv=5,
        scoring='accuracy',
        verbose=0
    )

    optimal_params.fit(X_train_scaled, y_train)
    st.write('Optimal Parameters determined by GridSearchCV:')
    st.write(optimal_params.best_params_)
    c = optimal_params.best_params_['C']
    gamma = optimal_params.best_params_['gamma']
    kernel = optimal_params.best_params_['kernel']
    return c, gamma, kernel

def scree_plot(X_train_scaled):
    pca = PCA().fit(X_train_scaled)
    per_var = np.round(pca.explained_variance_ratio_ * 100, decimals=1)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.bar(x=range(1, len(per_var) + 1), height=per_var)
    ax.set_ylabel('Percentage of Explained Variance')
    ax.set_xlabel('Principal Component')
    ax.set_title('Scree Plot')

    return fig

# Build the model with the optimal parameters and the reduced number of features
def pca(X_train_scaled, X_test_scaled, y_train):
    pca = PCA(n_components=2).fit(X_train_scaled)

    X_train_pca = pca.fit_transform(X_train_scaled)
    X_test_pca = pca.transform(X_test_scaled)

    param_grid = [
        {'C': [0.5, 1, 10, 100],
            'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.0001],
            'kernel': ['rbf']}
    ]

    optimal_params = GridSearchCV(
        SVC(),
        param_grid,
        cv=5,
        scoring='accuracy',
        verbose=0
    )
    optimal_params.fit(X_train_pca, y_train)
    st.write('Optimal Parameters determined by GridSearchCV and PCA:')
    st.write(optimal_params.best_params_)
    c = optimal_params.best_params_['C']
    gamma = optimal_params.best_params_['gamma']
    kernel = optimal_params.best_params_['kernel']
    return c, gamma, kernel

# ---------------------------------------------DISPLAY------------------------------------------------------------- #
# Create a sidebar
st.sidebar.title("About Me")
st.sidebar.write("I'm Sameeha Afrulbasha! I'm an undergraduate student studying Data Science, Statistics, and Math at Purdue University. Feel free to checkout my website and other media accounts below!")

st.sidebar.markdown('Website: \n\n\n https://sameehaafr.github.io/sameehaafr/')
st.sidebar.markdown('GitHub: \n\n\n https://github.com/sameehaafr')
st.sidebar.markdown('LinkedIn: \n\n\n https://www.linkedin.com/in/sameeha-afrulbasha/')
st.sidebar.markdown('Medium: \n\n\n https://sameehaafr.medium.com/')


def main():   
    # ---------------------------------------------INTRO------------------------------------------------------------- #
    st.title('SVM for Classifying Tumors')
    st.markdown('In this article, we will be building a Support Vector Machine(SVM) for classifying tumors as either Malignant or Benign. The data used for this project is sourced from the [UC Irvine Machine Learning Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic), specifically the Breast Cancer Wisconsin Diagnostic dataset. The code and implementation details can be found in the corresponding [GitHub Repository](https://github.com/sameehaafr/SVM-PCA).')
    st.markdown("<b>Category</b>: Supervised Machine Learning", unsafe_allow_html=True)
    st.markdown("<b>Objective:</b> Build a supervised SVM model that can accurately predict the nature of tumors based on their characteristics.", unsafe_allow_html=True)

    # ---------------------------------------------DATA------------------------------------------------------------- #
    st.header('Data Loading and Preprocessing')
    st.markdown('The first step in the code involves loading the dataset and performing some initial data exploration. The breast cancer dataset is loaded using the scikit-learn librarys "load_breast_cancer" function, which provides a preprocessed and labeled dataset. The data is then organized into a pandas DataFrame for ease of manipulation and analysis. The DataFrame displays the tumor characteristics along with the corresponding target labels, which indicate whether the tumor is Malignant or Benign. This dataset seems to already be cleaned, so we will go ahead and use it as is.')
    df = load_data()
    st.dataframe(df)
    X_train_scaled, X_test_scaled, y_train, y_test = split_data(df)

    # ---------------------------------------------BASIC MODEL------------------------------------------------------------- #
    st.header('Basic SVM Model')
    st.markdown('The code proceeds to build a basic SVM model using default parameters. The SVM model is created using the scikit-learn librarys "SVC" class, with random_state set for reproducibility. The model is trained on the scaled training data. The accuracy, precision, and recall scores of the model are evaluated and displayed, along with a confusion matrix that illustrates the performance of the model in predicting tumor types.')
    st.markdown("Default SVM Parameters: C = 1.0, gamma = 'scale', kernel = 'rbf'")
    basic_svm = SVC(random_state=30)
    basic_svm.fit(X_train_scaled,y_train)
    st.write('Parameters used in the model:')
    st.write(basic_svm.get_params())

    # ---------------------------------------------METRICS------------------------------------------------------------- #
    accuracy = basic_svm.score(X_test_scaled, y_test)
    y_pred = basic_svm.predict(X_test_scaled)
    st.write("Accuracy: ", accuracy.round(2))
    st.write("Precision: ", precision_score(y_test, y_pred, labels=['Malignant', 'Benign']).round(2))
    st.write("Recall: ", recall_score(y_test, y_pred, labels=['Malignant', 'Benign']).round(2)) 

    st.write("[Understanding the Confusion Matrix](https://sameehaafr.notion.site/Understanding-Confusion-Matrix-94e06c56f84f4abfb4644a59fd3b2c3f?pvs=4)")
    show_confusion_matrix(basic_svm, X_test_scaled, y_test)


    # ---------------------------------------------GRIDSEARCHCV------------------------------------------------------------- #
    st.header('Parameter Tuning with GridSearchCV')
    st.markdown("To improve the performance of the SVM model, the code utilizes the GridSearchCV class from scikit-learn. GridSearchCV systematically searches through a specified parameter grid and performs cross-validation to identify the optimal combination of parameters. In this case, the parameters being tuned are C (regularization parameter), gamma (kernel coefficient), and kernel type. The best parameters determined by GridSearchCV are displayed, and the optimal SVM model is built using these parameters.")
    st.markdown("[Parameter Meanings](https://sameehaafr.notion.site/SVM-Parameter-Meanings-71b46acf73a047368eb27b8420d7663c?pvs=4)")
    st.code('''def find_best_params(X_train_scaled, y_train):
    param_grid = [
        {'C': [0.5, 1, 10, 100],
        'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.0001],
        'kernel': ['rbf']}
        ]

    optimal_params = GridSearchCV(
        SVC(),
        param_grid,
        cv=6,
        scoring='accuracy',
        verbose=0
    )

    optimal_params.fit(X_train_scaled, y_train)
    c = optimal_params.best_params_['C']
    gamma = optimal_params.best_params_['gamma']
    kernel = optimal_params.best_params_['kernel']

    return c, gamma, kernel''')

    c, gamma, kernel = find_best_params(X_train_scaled, y_train)
    st.markdown('This returns: C = {}, gamma = {}, kernel = {}'.format(c, gamma, kernel))

    # ---------------------------------------------OPTIMAL MODEL------------------------------------------------------------- #
    st.header("Evaluation of Optimal SVM Model")
    st.markdown("The code evaluates the performance of the optimal SVM model on the test dataset. The accuracy, precision, and recall scores are calculated and displayed. Additionally, a confusion matrix is generated to provide a visual representation of the model's performance.")
    opt_svm = build_svm(c, gamma, kernel, X_train_scaled, y_train)
    accuracy = opt_svm.score(X_test_scaled, y_test)
    y_pred = opt_svm.predict(X_test_scaled)
    st.write("Accuracy: ", accuracy.round(2))
    st.write("Precision: ", precision_score(y_test, y_pred, labels=['Malignant', 'Benign']).round(2))
    st.write("Recall: ", recall_score(y_test, y_pred, labels=['Malignant', 'Benign']).round(2)) 
    st.markdown("As can be seen, the optimized SVM model performs SLIGHTLY better than the basic model. In other cases, you may be able to see a better improvement in performance if a larger dataset is used. In this case, the dataset is relatively small and the relations between the variables are clear (when basic data analysis is done), so the improvement is not as significant.")

    show_confusion_matrix(opt_svm, X_test_scaled, y_test)

    # ---------------------------------------------SCREE PLOT AND PCA------------------------------------------------------------- #
    st.header("Principal Component Analysis (PCA)")
    st.markdown("Principal Component Analysis (PCA) is a dimensionality reduction technique used to transform a high-dimensional dataset into a lower-dimensional representation while preserving its essential information. PCA transforms the original features into a new set of uncorrelated variables, called principal components. The principal components are ordered in terms of their importance, where the first principal component captures the maximum variance in the data, and subsequent components capture decreasing amounts of variance. The code generates a scree plot, which illustrates the explained variance ratio for each principal component. This plot helps determine the number of components to retain.")
    fig = scree_plot(X_train_scaled)
    st.pyplot(fig)
    c, gamma, kernel = pca(X_train_scaled, X_test_scaled, y_train)

    # ---------------------------------------------OPTIMAL MODEL WITH PCA------------------------------------------------------------- #
    st.header("Optimal Model with PCA")
    st.markdown("Finally, the optimal SVM model is built using the PCA-transformed data. The same process of parameter tuning with GridSearchCV is applied, this time using the reduced number of features. Here's the performance of the optimized SVM model with PCA:")
    clf_svm_pca= build_svm(c, gamma, kernel, X_train_scaled, y_train)
    accuracy = clf_svm_pca.score(X_test_scaled, y_test)
    y_pred = clf_svm_pca.predict(X_test_scaled)
    class_names = ['Malignant', 'Benign']
    st.write("Accuracy:s ", accuracy.round(2))
    st.write("Precision: ", precision_score(y_test, y_pred, labels=class_names).round(2))
    st.write("Recall: ", recall_score(y_test, y_pred, labels=class_names).round(2))

    # ---------------------------------------------CONCLUSION------------------------------------------------------------- #
    st.header("Conclusion")
    st.markdown("By following this code and implementing the described steps, one can effectively utilize SVM and PCA for tumor classification, achieving accurate predictions and potentially aiding in medical diagnoses.")

    st.markdown("Thanks for reading! :)")


if __name__ == '__main__':
    main()