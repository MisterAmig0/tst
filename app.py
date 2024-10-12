from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Database configuration - using site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Model for Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)

# Check if the database exists and create it if not
def init_db():
    if not os.path.exists('site.db'):
        with app.app_context():
            db.create_all()
            print("Database created!")
    else:
        print("Database already exists.")

# Call the function to initialize the database
init_db()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Homepage route to display posts
@app.route('/')
def home():
    # Get all posts from the database
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

# Route to create a new listing
@app.route('/makelisting', methods=['GET', 'POST'])
def makelisting():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        image = request.files['image']

        if image and allowed_file(image.filename):
            # Save the image
            filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create new post and add to the database
            new_post = Post(title=title, price=price, image_filename=filename)
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template('makelisting.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
