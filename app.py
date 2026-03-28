from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:765472@localhost/clinic_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS (Tables) ---
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100))
    fee = db.Column(db.Float) # Yahan column ka naam 'fee' hai
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROUTES ---

# 1. Dashboard Route
@app.route('/')
def index():
    # Database se latest data lana
    sales = Sale.query.order_by(Sale.date_sold.desc()).all()
    patients = Patient.query.order_by(Patient.visit_date.desc()).all()
    
    total_sales = sum(s.amount for s in sales)
    
    return render_template('index.html', 
                           total_sales=total_sales, 
                           total_patients=len(patients), 
                           sales_history=sales,
                           patients_list=patients)

# 2. Medicine Sale add karne ka route (Jo pehle missing tha)
@app.route('/add_sale', methods=['POST'])
def add_sale():
    m_name = request.form.get('m_name')
    amt = request.form.get('amt')
    pay_mode = request.form.get('pay_mode')
    
    if m_name and amt:
        new_sale = Sale(medicine_name=m_name, amount=float(amt), payment_method=pay_mode)
        db.session.add(new_sale)
        db.session.commit()
    return redirect('/')

# 3. Patient Entry add karne ka route
@app.route('/add_patient', methods=['POST'])
def add_patient():
    p_name = request.form.get('p_name')
    p_fee = request.form.get('p_fee')
    
    if p_name and p_fee:
        # Yahan 'fee' use kiya hai jo model mein define hai
        new_patient = Patient(patient_name=p_name, fee=float(p_fee))
        db.session.add(new_patient)
        db.session.commit()
    return redirect('/')
# Medicine Sale delete karne ka route
@app.route('/delete_sale/<int:id>')
def delete_sale(id):
    sale_to_delete = Sale.query.get_or_404(id)
    db.session.delete(sale_to_delete)
    db.session.commit()
    return redirect('/')

# Patient record delete karne ka route
@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    patient_to_delete = Patient.query.get_or_404(id)
    db.session.delete(patient_to_delete)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    print("Server start ho raha hai... http://127.0.0.1:5000 par jayein")
    app.run(debug=True)