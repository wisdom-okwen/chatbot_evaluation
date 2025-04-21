import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


OVERALL_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/overall_ratings.csv"
USER_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/criteria_ratings/user.csv"
SELF_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/criteria_ratings/self.csv"
OBSERVER_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/criteria_ratings/observer.csv"
PER_TURN_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/per_turn_ratings.csv"

def visualize_overall_ratings_summary(df):
    """Display basic statistics for overall ratings (excluding language)."""
    df_no_lang = df.drop(columns=["Language"])
    print(df_no_lang.describe())

def plot_overall_rating_correlation(df):
    """Plot heatmap of correlations among overall ratings (excluding IDs and language)."""
    corr_matrix = df.drop(columns=["Language", "Convsation_Id"]).corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
    plt.title('Correlation Heatmap - Overall Ratings')
    plt.show()

def plot_observer_vs_self_scatter(df):
    """Plot Observer vs Self ratings with color scale showing differences."""
    df['Observer_Self_Diff'] = df['Observer_Rating'] - df['Self_Rating']
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(df['Observer_Rating'], df['Self_Rating'], c=df['Observer_Self_Diff'], cmap='coolwarm')
    plt.colorbar(sc, label='Observer - Self Rating Difference')
    plt.title("Scatterplot: Observer Rating vs Self Rating")
    plt.xlabel("Observer Rating")
    plt.ylabel("Self Rating")
    plt.show()

def plot_observer_vs_user_scatter(df):
    """Plot Observer vs User ratings with difference as color."""
    df['User_Observer_Diff'] = df['User_Rating'] - df['Observer_Rating']
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(df['Observer_Rating'], df['User_Rating'], c=df['User_Observer_Diff'], cmap='coolwarm', alpha=0.6, s=30)
    plt.colorbar(sc, label='User - Observer Rating Difference')
    plt.title("Scatterplot: Observer Rating vs User Rating")
    plt.xlabel("Observer Rating")
    plt.ylabel("User Rating")
    plt.show()

def plot_user_vs_self_scatter(df):
    """Plot User vs Self ratings with difference as color."""
    df['User_Self_Diff'] = df['User_Rating'] - df['Self_Rating']
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(df['User_Rating'], df['Self_Rating'], c=df['User_Self_Diff'], cmap='coolwarm', alpha=0.6, s=30)
    plt.colorbar(sc, label='User - Self Rating Difference')
    plt.title("Scatterplot: User Rating vs Self Rating")
    plt.xlabel("User Rating")
    plt.ylabel("Self Rating")
    plt.show()


def plot_low_ratings_by_language(df):
    """Bar plot of number of low ratings per language."""
    user_thresh = df['User_Rating'].quantile(0.05)
    self_thresh = df['Self_Rating'].quantile(0.05)
    observer_thresh = df['Observer_Rating'].quantile(0.05)

    low_df = df[
        (df['User_Rating'] < user_thresh) |
        (df['Self_Rating'] < self_thresh) |
        (df['Observer_Rating'] < observer_thresh)
    ]

    lang_counts = low_df['Language'].value_counts()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=lang_counts.index, y=lang_counts.values)
    plt.title('Number of Low Ratings per Language')
    plt.xlabel('Language')
    plt.ylabel('Count of Low Ratings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_low_rating_type_breakdown(df):
    """Stacked bar plot of which rating(s) were low by language."""
    user_thresh = df['User_Rating'].quantile(0.05)
    self_thresh = df['Self_Rating'].quantile(0.05)
    observer_thresh = df['Observer_Rating'].quantile(0.05)

    def get_low_rating_type(row):
        types = []
        if row['User_Rating'] < user_thresh:
            types.append('User')
        if row['Self_Rating'] < self_thresh:
            types.append('Self')
        if row['Observer_Rating'] < observer_thresh:
            types.append('Observer')
        return ', '.join(types)

    low_df = df[
        (df['User_Rating'] < user_thresh) |
        (df['Self_Rating'] < self_thresh) |
        (df['Observer_Rating'] < observer_thresh)
    ].copy()




    low_df['Low_Rating_Type'] = low_df.apply(get_low_rating_type, axis=1)
    breakdown = low_df.groupby(['Language', 'Low_Rating_Type']).size().unstack(fill_value=0)

    breakdown.plot(kind='bar', stacked=True, figsize=(12, 6))
    plt.title('Types of Low Ratings by Language')
    plt.ylabel('Number of Conversations')
    plt.xlabel('Language')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_user_criteria_correlation(df_CR_User):
    """Heatmap of correlations between different user rating criteria."""
    df_clean = df_CR_User.drop(columns=["Language"])
    corr_matrix = df_clean.corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
    plt.title('Correlation Heatmap - User Criteria')
    plt.show()

def plot_user_criteria_distributions(df_CR_User):
    """Histogram + KDE for each user rating criterion."""
    for column in df_CR_User.columns[1:]:
        sns.histplot(df_CR_User[column], kde=True)
        plt.title(f'Distribution of {column} Ratings - User')
        plt.xlabel('Rating')
        plt.ylabel('Frequency')
        plt.show()

import pandas as pd

def get_low_criteria_rating_ids(percentile=0.04):
    """
    Returns a dictionary of dictionaries: {persona: {criterion: [conversation_ids]}}.
    """

    df_user = pd.read_csv(USER_RATINGS)
    df_observer = pd.read_csv(OBSERVER_RATINGS)
    df_self = pd.read_csv(SELF_RATINGS)
    persona_dfs = {
        "User": df_user,
        "Self": df_self,
        "Observer": df_observer
    }

    criteria = [
        'Clarity_and_Simplicity',
        'Relevance_and_Accuracy',
        'Tone_and_Supportiveness',
        'Adaptability',
        'Consistency_and_Flow'
    ]

    result = {}

    for persona, df in persona_dfs.items():
        result[persona] = {}
        for crit in criteria:
            threshold = df[crit].quantile(percentile)
            low_ids = df[df[crit] < threshold]['Conversation_Id'].tolist()
            result[persona][crit] = low_ids

    return result


def get_low_overall_rating_ids():
    df = pd.read_csv(OVERALL_RATINGS)
    """Return list of conversation IDs where any rating is below the 5th percentile."""
    user_thresh = df['User_Rating'].quantile(0.05)
    self_thresh = df['Self_Rating'].quantile(0.05)
    observer_thresh = df['Observer_Rating'].quantile(0.05)

    res = df[
        (df['User_Rating'] < user_thresh) |
        (df['Self_Rating'] < self_thresh) |
        (df['Observer_Rating'] < observer_thresh)
    ]['Convsation_Id'].tolist()
    return res

import pandas as pd

def get_low_per_turn_rating_ids(percentile=0.05):
    """
    Returns a dictionary of {Conversation_ID: [Turn_x, Turn_y, ...]} 
    where one or more turns are below the global percentile threshold.
    """
    df = pd.read_csv(PER_TURN_RATINGS)

    # Get only the turn columns
    turn_cols = [col for col in df.columns if col.startswith("Turn_")]

    # Compute the global threshold across all turn values
    all_turn_values = df[turn_cols].values.flatten()
    threshold = pd.Series(all_turn_values).quantile(percentile)

    # Result dictionary
    result = {}

    for _, row in df.iterrows():
        low_turns = [col for col in turn_cols if row[col] < threshold]
        if low_turns:
            result[int(row['Conversation_ID'])] = low_turns

    return result
