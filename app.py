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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filenames = db.Column(db.String(300), nullable=False)  # Changed from image_filename to image_filenames


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
        images = request.files.getlist('images')  # Get list of uploaded images

        image_filenames = []

        for image in images:
            if image and allowed_file(image.filename):
                # Save the image
                filename = image.filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filenames.append(filename)

        # Join image filenames into a single string to store in the database
        image_filenames_str = ','.join(image_filenames)

        # Create new post and add to the database
        new_post = Post(title=title, price=price, image_filenames=image_filenames_str)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('makelisting.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
