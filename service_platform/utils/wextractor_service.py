from ..models import OnlineReview

def save_data_to_model(user,platform,data):
    print(data['reviews'][0]['reviewer'])