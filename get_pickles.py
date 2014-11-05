import os
import pickle

def get_pickles():
    print os.getcwd()
    if os.getcwd().split('/')[1] != 'Users':
        my_dir = os.path.dirname(__file__)
        model_path = os.path.join(my_dir, 'pickles/model.pkl')
        vec_path = os.path.join(my_dir, 'pickles/vectorizer.pkl')
        google_data_path = os.path.join(my_dir, 'pickles/google_data.pkl')
        last_update_path = os.path.join(my_dir, 'pickles/last_update.pkl')

        model = pickle.load( open( model_path, "rb" ) )
        vec  = pickle.load( open( vec_path, "rb" ) )
        google_data = pickle.load( open( google_data_path, "rb" ) )
        last_update  = pickle.load( open( last_update_path, "rb" ) )
    else:    
        model = pickle.load( open( "pickles/model.pkl", "rb" ) )
        vec  = pickle.load( open( "pickles/vectorizer.pkl", "rb" ) )
        google_data = pickle.load( open( "pickles/google_data.pkl", "rb" ) )
        last_update  = pickle.load( open( "pickles/last_update.pkl", "rb" ) )
    return model, vec, google_data, last_update   