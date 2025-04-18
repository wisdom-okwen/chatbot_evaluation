"""Generate new conversation from low rated conversations."""
import os
import csv
from openai import OpenAI
from analysis.utility import (
    get_low_overall_rating_conversation_ids,
    get_low_criteria_rating_ids,
)


low_rated_overall_convs = get_low_overall_rating_conversation_ids() # list of conv ids
low_rated_criteria_convs = get_low_criteria_rating_ids() # dict of persona: criteria: conv ids


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

