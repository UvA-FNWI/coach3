from sklearn.linear_model import BayesianRidge
from utils.dataset import create_training_set
from sklearn.externals import joblib


def generate_model_fit(train_values, train_targets, n_assessments):
    model = BayesianRidge()
    model.fit(train_values, train_targets)

    # Output a pickle file for the model
    joblib.dump(model, 'model_for_{}_assessments.pkl'.format(n_assessments))

def generate_all_model_fits():
    for n_assessments in range(1, 12):
        train_values, train_targets = create_training_set(n_assessments)
        generate_model_fit(train_values,train_targets, n_assessments)

