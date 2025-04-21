"""Generate new conversation from low rated conversations."""
import os
import csv
from openai import OpenAI
from analysis.utility import (
    get_low_criteria_rating_ids,
    get_low_overall_rating_ids,
    get_low_per_turn_rating_ids
)


low_rated_overall_convs = get_low_overall_rating_ids() # list of conv ids
low_rated_criteria_convs = get_low_criteria_rating_ids() # dict of dicts
low_rated_per_turn_convs = get_low_per_turn_rating_ids() # list of dictionaries


def gpt_analyzer():
    pass

def llama_analyzer():
    pass

def generate_new_convs():
    pass

def generate_new_overall_ratings():
    pass

def generate_observer_criteria_ratings():
    pass

def generate_user_criteria_ratings():
    pass

def generate_self_criteria_ratings():
    pass

