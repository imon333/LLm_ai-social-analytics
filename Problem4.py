import os
import json

# NB : (Copied papers directory on my directory)
# because of only Read permission

""" a) Generate a dictionary corpus_raw that holds all 
concatenated paper summaries for every year in the
folder arxiv/papers. For a given year, load the jsonl
file and combine all summary fields of all papers
 to a single string. """

# Path to the papers directory
papers_dir = '/home/nnds-8b/papers'  

# Output file path
output_file_path = '/home/nnds-8b/papers/concatenated_summaries.json'  

# Initialize the dictionary to hold summaries as lists
corpus_raw = {}

# Loop through each file in the papers directory
for filename in os.listdir(papers_dir):
    if filename.endswith('.jsonl'):
        year = filename[:-5]  # Extract the year from the filename (remove .jsonl)
        summaries = []  # Initialize a list to hold summaries for this year

        # Read the jsonl file as a JSON array
        with open(os.path.join(papers_dir, filename), 'r') as file:
            data = json.load(file)  # Load the entire file as a JSON array
            for entry in data:
                summary = entry.get("summary", "")  # Get the summary, default to empty string if not present
                summaries.append(summary)  # Append the summary to the list

        # Store the list of summaries in the dictionary
        corpus_raw[year] = summaries  # Store the list of summaries
    # print(corpus_raw[year])
    
    #-------
    ## Question: after printing it crashed and ask for reopen.
    # why is that ?
   # --------
   
# Write the concatenated summaries to a JSON file
with open(output_file_path, 'w') as output_file:
    json.dump(corpus_raw, output_file, indent=2)


""" b) Generate a dictionary corpus_clean that 
stores the paper summaries in a cleaned form. Apply the
following steps: First, replace \n by 
a single whitespace. Then, remove non-word chars. Finally,
compress multiple whitespaces into a single one."""

# Part B --------------------------------------------------------------

import re # for replace pattern mathches

# Path to the concatenated JSON file
Concatenated_json_file_path = '/home/nnds-8b/papers/concatenated_summaries.json'

# Read the JSON file
with open(Concatenated_json_file_path, 'r') as file:
    data = json.load(file)

# Initialize an empty dictionary to store cleaned summaries
corpus_clean = {}

# Iterate through the data to clean the summaries
for year, summaries in data.items():
    cleaned_summaries = []
    for summary in summaries:
        summary = summary.replace('\n', ' ')  # Replace newlines with whitespace
        summary = re.sub(r'[^\w\s]', '', summary)  # Remove non-word characters
        summary = re.sub(r'\s+', ' ', summary)  # Compress multiple whitespaces
        cleaned_summaries.append(summary.strip())  # Strip leading/trailing whitespace

    corpus_clean[year] = cleaned_summaries

# Print the cleaned summaries
print(json.dumps(corpus_clean, indent=2))



##-- part c ----------------------------------------------
""" c) Plot the relative number of occurence 
of all ChatGPT words listed above as a function of the year.
Normalize the count to the number of papers 
published in a given year."""


import pandas as pd
import matplotlib.pyplot as plt
# List of target words to count
chatgpt_words = ['delve', 'intricate', 'meticulous', 'versatile', 'pivotal']

# Initialize a dictionary to hold counts and paper counts
word_counts = {word: {} for word in chatgpt_words}
paper_counts = {}

# Iterate through the data to count words and total papers
for year, summaries in data.items():
    total_papers = len(summaries)
    paper_counts[year] = total_papers  # Store total number of papers for the year

    for summary in summaries:
        for word in chatgpt_words:
            count = len(re.findall(r'\b' + re.escape(word) + r'\b', summary.lower()))
            if year not in word_counts[word]:
                word_counts[word][year] = 0
            word_counts[word][year] += count

# Prepare data for plotting
relative_counts = {word: [] for word in chatgpt_words}
years = sorted(paper_counts.keys())

for year in years:
    for word in chatgpt_words:
        if paper_counts[year] > 0:
            relative_count = word_counts[word].get(year, 0) / paper_counts[year]
        else:
            relative_count = 0
        relative_counts[word].append(relative_count)

# Convert to DataFrame for easier plotting
df = pd.DataFrame(relative_counts, index=years)

#print(df) -- chekin the data frame

# Plot the data
plt.figure(figsize=(14, 8))  # Larger figure for better readability

# Plot each word without scaling
for word in chatgpt_words:
    plt.plot(df.index, df[word], marker='o', linestyle='-', linewidth=2, markersize=6, label=word)

# Enhancing labels and title
plt.title('Trends in Relative Occurrence of Target Words by Year', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=14)
plt.ylabel('Relative Occurrence', fontsize=14)  # Updated ylabel for clarity

# Adding a legend with a background box for clarity
plt.legend(title='Words', title_fontsize=12, fontsize=10, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0)

# Displaying grid lines and improving layout
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout for better spacing
plt.show()



## part D ------------------------------------------------

""" d) Combine all (cleaned) text from all years into a single string. Calculate the distribution of letters (a
to z) and create a plot. Include standard English letter frequencies as given by eng_let_std.csv."""

#count occurrences of each letter efficiently
from collections import Counter

# S Combine all cleaned text into a single string
combined_text_parts = []  # Use a list for efficient concatenation
for year, summaries in data.items():
    combined_text_parts.extend(summaries)  # Add summaries to the list

# Combine all summaries into a single string
combined_text = " ".join(combined_text_parts)

# Step 2: Calculate the distribution of letters (a to z)
letter_counts = Counter()  # Initialize a Counter to count letters
combined_text = combined_text.lower()  # Convert to lowercase for uniformity

for char in combined_text:
    if 'a' <= char <= 'z':  # Count only letters a-z
        letter_counts[char] += 1

# Convert letter_counts to a dictionary for DataFrame creation
letter_counts_dict = dict(letter_counts)

#  Load standard English letter frequencies from CSV (assumes no headers in the file)
standard_frequencies = pd.read_csv('eng_let_std.csv', names=['letter', 'frequency'], header=None)

#  Prepare DataFrames for plotting
df_counts = pd.DataFrame(list(letter_counts_dict.items()), columns=['letter', 'count'])

#print(df_counts)

df_counts['relative_frequency'] = df_counts['count']*100 / df_counts['count'].sum()  # Relative frequency

# Merge with standard frequencies DataFrame
df_merged = pd.merge(df_counts, standard_frequencies, on='letter', suffixes=('_calculated', '_standard'))



# Plot the letter frequencies
plt.figure(figsize=(14, 8))
plt.bar(df_merged['letter'], df_merged['relative_frequency'], alpha=0.6, label='Calculated Frequency')
plt.plot(df_merged['letter'], df_merged['frequency'], marker='o', linestyle='-', color='red', label='Standard Frequency')
plt.title('Letter Frequency Distribution Comparison', fontsize=16)
plt.xlabel('Letters', fontsize=14)
plt.ylabel('Relative Frequency', fontsize=14)
plt.legend()
plt.grid(axis='y')
plt.tight_layout()
plt.show()