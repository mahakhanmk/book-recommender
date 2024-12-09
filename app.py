from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

# popular_df = pickle.load(open('popular.pkl', 'rb'))
popular_df = pd.read_pickle("models/popular.pkl")
pt = pd.read_pickle("models/pt.pkl")
books = pd.read_pickle("models/books.pkl")
similarity_scores = pd.read_pickle("models/similarity_scores.pkl")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author = list(popular_df['Book-Author'].values),
                           image = list(popular_df['Image-URL-M'].values),
                           votes = list(popular_df['num_ratings'].values),
                           rating = list(popular_df['avg_ratings'].values),
                           )

@app.route('/recommend')
def recommed_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods = ['post'])
def recommed():
    user_input = request.form.get('user_input')

    book_name_lower = user_input.lower()
    
    matching_books = [book for book in pt.index if book_name_lower in book.lower()]
    
    if not matching_books:
        return render_template('notfound.html')
    
    book_name_matched = matching_books[0]
    
    index = np.where(pt.index == book_name_matched)[0][0]
    
    similar_items = sorted(
        list(enumerate(similarity_scores[index])), 
        key=lambda x: x[1], 
        reverse=True
    )[1:10]
    
    data = []
    recommended_books = set() 
    
    temp_df = books[books['Book-Title'] == book_name_matched]
    item = [
        list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0],
        list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values)[0],
        list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
    ]
    recommended_books.add(tuple(item))
    data.append(item)
    
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        recommended_books.add(tuple(item))
    
    data = list(recommended_books)
    
    return render_template('recommend.html', data=data)

@app.route('/contact')
def contact_ui():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)