from flask import Flask, render_template, request, redirect, url_for, session, send_file
from weasyprint import HTML
import io

app = Flask(__name__)
app.secret_key = '6b70d08cbdf02f0a79324c6d61a0e356'  

CREDENTIALS = {
    'vaidehi': 'vaidehi@mount',
    'aman.thakur': 'aman@mount',
    'kiran.bhandari': 'kiran@mount',
    'rahul.mali': 'rahul@mount',
    'kishan.pandey': 'kishan@mount'
}

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the credentials are valid
        if CREDENTIALS.get(username) == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid username or password", 403

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    payment_method_type = None  # Initialize payment_method_type

    if request.method == 'POST':
        # Get form data
        invoice_date = request.form.get('invoice_date')
        invoice_number = request.form.get('invoice_number')
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'Online':
            payment_method_type = request.form.get('payment_method_method')
            if payment_method_type == 'UPI':
                upi_reference = request.form.get('upi_reference')
                transaction_id = None
            else:
                upi_reference = None
                transaction_id = request.form.get('transaction_id')
        else:
            upi_reference = None
            transaction_id = None

        items = request.form.getlist('item_name')
        quantities = request.form.getlist('quantity')
        prices = request.form.getlist('price')
        taxes = request.form.getlist('tax')

        # Calculate subtotals
        subtotals = [float(price) * int(quantity) for price, quantity in zip(prices, quantities)]
        subtotal = sum(subtotals)
        total_tax = sum(float(tax) for tax in taxes)
        total = subtotal + total_tax

        # Format all monetary values to 2 decimal places
        subtotals = [f"{subtotal:.2f}" for subtotal in subtotals]
        subtotal = f"{subtotal:.2f}"
        total_tax = f"{total_tax:.2f}"
        total = f"{total:.2f}"
        prices = [f"{float(price):.2f}" for price in prices]
        taxes = [f"{float(tax):.2f}" for tax in taxes]

        # Generate HTML
        html = render_template('invoice_template.html',
                               invoice_date=invoice_date,
                               invoice_number=invoice_number,
                               customer_name=customer_name,
                               customer_address=customer_address,
                               payment_method=payment_method,
                               payment_method_type=payment_method_type,
                               upi_reference=upi_reference,
                               transaction_id=transaction_id,
                               items=zip(items, quantities, prices, taxes, subtotals),
                               subtotal=subtotal,
                               taxes=total_tax,
                               total=total)

        # Convert HTML to PDF
        pdf = HTML(string=html, base_url=request.host_url).write_pdf()

        return send_file(io.BytesIO(pdf),
                         download_name='invoice.pdf',
                         as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
