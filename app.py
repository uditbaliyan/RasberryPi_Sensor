from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = "123"  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database URI
db = SQLAlchemy(app)  # Initialize SQLAlchemy


# Define the Customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    mail = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<Customer {self.name}>"


# Define the SensorData model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    temperature = db.Column(db.Float, nullable=False)
    pulse = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<SensorData {self.timestamp}: Temperature={self.temperature}, Pulse={self.pulse}>"


# Create tables before the first request
@app.before_first_request
def create_tables():
    db.create_all()




def maintain_data_limit():
    try:
        # Check if the number of entries exceeds the limit
        num_entries = db.session.query(SensorData).count()
        if num_entries > 100:
            # Find the oldest data entry
            oldest_data = SensorData.query.order_by(SensorData.id.asc()).first()
            # Delete the oldest data entry
            db.session.delete(oldest_data)
            db.session.commit()
    except Exception as e:
        print("Error deleting older data:", e)




# Route to handle login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = Customer.query.filter_by(name=name, mail=password).first()
        if user:
            session["name"] = user.name
            session["mail"] = user.mail
            flash("Login successful", "success")
            return redirect(url_for("customer"))
        else:
            flash("Username and Password Mismatch", "danger")
    return redirect(url_for("index"))


# Route to handle customer dashboard
@app.route('/customer')
def customer():
    if "name" in session:
        return render_template("heart_chart.html")
    else:
        flash("You need to login first", "warning")
        return redirect(url_for("index"))


# Route to handle registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact = request.form['contact']
        mail = request.form['mail']
        try:
            new_customer = Customer(name=name, address=address, contact=contact, mail=mail)
            db.session.add(new_customer)
            db.session.commit()
            flash("Registration Successful", "success")
        except Exception as e:
            flash(f"Error in Registration: {str(e)}", "danger")
        return redirect(url_for("index"))
    return render_template('register.html')


# Route to handle logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))


# Route to update sensor data
sensor_data = {"temperature": 0, "pulse": 0}
# Example route to add sensor data and maintain limit
@app.route('/update_data', methods=['POST',"GET"])
def update_data():
    global sensor_data
    new_data = SensorData(temperature=1,pulse=1)
    db.session.add(new_data)
    db.session.commit()
    if request.method == 'POST':
        data = request.json
        temperature = data.get('temperature', 0)
        pulse = data.get('pulse', 0)
        sensor_data = {"temperature": temperature, "pulse": pulse}

        try:
            # Create new data point
            new_data = SensorData(temperature, pulse)
            db.session.add(new_data)
            db.session.commit()
            # Automatically handle data limit
            maintain_data_limit()
            return 'Data received and stored successfully', 200
        except Exception as e:
            print("Error updating data:", e)
            return 'Error storing data', 500

    elif request.method == 'GET':
        return jsonify(sensor_data)



# Route to render customer dashboard
@app.route('/data')
def data():
    return render_template('databases_view.html')


# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invoke_function', methods=['POST'])
def invoke_function():
    # Your Python function logic goes here
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart



    # Email configuration
    sender_email = "healthmonitoring00@gmail.com"
    receiver_email = "baliyanvdit@gmail.com"
    password = "yrhb uzsq souh dsvw"
    subject = "health monitoring system alert"

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add the email body
    body = "Please check the patient immediately."
    message.attach(MIMEText(body, "plain"))

    # Connect to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()  # identify ourselves to smtp.gmail.com
        server.starttls()  # secure the connection
        server.ehlo()  # re-identify ourselves after TLS
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)


    print("Email sent successfully!")
    print("Python function invoked!")
    return "Function invoked successfully"

# Route to retrieve all sensor data
@app.route('/get_all_data', methods=["GET"])
def get_all_data():
    try:
        # Fetch all data
        all_data = SensorData.query.all()

        # Convert data to a list of dictionaries
        data_list = [{'timestamp': data.timestamp, 'temperature': data.temperature, 'pulse': data.pulse} for data in all_data]

        # Return JSON response
        return jsonify(data_list)
    except Exception as e:
        print("Error retrieving all data:", e)
        # Return an empty list on error
        return jsonify([])





if __name__ == '__main__':
    app.run(debug=True)















