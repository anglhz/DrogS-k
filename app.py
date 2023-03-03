from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
from fuzzywuzzy import fuzz
import smtplib

app = Flask(__name__)

# Load the excel file as a DataFrame
df = pd.read_excel('static/database/med_list.xlsx')

# Define a function to search for matches in the first and second columns
def search_med_list(df, word):
    # Search for exact matches in the first and second columns
    matches_col1 = df.loc[df.iloc[:, 0] == word]
    matches_col2 = df.loc[df.iloc[:, 1] == word]
    # Merge the results
    matches = pd.concat([matches_col1, matches_col2]).drop_duplicates()
    # Check if the content of the matched word matches with any other word in the columns
    for index, row in matches.iterrows():
        if word in row[0] or word in row[1]:
            matching_rows = df.loc[(df.iloc[:, 0].str.contains(word)) | (df.iloc[:, 1].str.contains(word))]
            matches = pd.concat([matches, matching_rows]).drop_duplicates()
    # Capitalize the values in the first column of the matched rows
    matches.iloc[:, 0] = matches.iloc[:, 0].str.capitalize()
    # If no exact match was found, try fuzzy matching
    if matches.empty:
        fuzzy_matches = []
        for index, row in df.iterrows():
            # Calculate the fuzzy match score for each word in the first and second columns
            score1 = fuzz.token_set_ratio(word, row[0])
            score2 = fuzz.token_set_ratio(word, row[1])
            # If the score is greater than or equal to 90, add the row to the list of fuzzy matches
            if score1 >= 90 or score2 >= 90:
                fuzzy_matches.append(row)
        # If there are any fuzzy matches, create a dataframe of the matches and return it
        if fuzzy_matches:
            matches = pd.DataFrame(fuzzy_matches, columns=df.columns).drop_duplicates()
            matches.iloc[:, 0] = matches.iloc[:, 0].str.capitalize()
    return matches

def send_email(subject, body):
    try:
        server = smtplib.SMTP('send.one.com', 587)
        server.starttls()
        server.login('kontakt@xn--drogsk-0xa.se', 'pw')
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format('kontakt@xn--drogsk-0xa.se', 'kontakt@xn--drogsk-0xa.se', subject, body)
        server.sendmail('kontakt@xn--drogsk-0xa.se', 'kontakt@xn--drogsk-0xa.se', message.encode('utf-8'))
        server.quit()
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search']
    result = search_med_list(df, search_term.lower())
    return render_template('result.html', result=result, search_term=search_term)

@app.route("/usage")
def usage():
    return render_template("usage.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/mediciner")
def mediciner():
    with open('static/database/med_list.xlsx', 'r') as file:
        content = file.read()
    return content

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/send_email', methods=['POST'])
def send_email_route():
    search_term = request.form['search_term']
    subject = 'Ny Träffrapport'
    body = f'Användaren sökte på: {search_term}'
    email_sent = send_email(subject, body)  # add parentheses to call the function
    if email_sent:
        message = "E-postmeddelandet skickades"
    else:
        message = "E-postmeddelandet kunde inte skickas"
    return message
    

if __name__ == '__main__':
    app.run(debug=True)
    