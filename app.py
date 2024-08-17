from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from weasyprint import HTML
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import requests
from io import BytesIO
import threading
import os


app = Flask(__name__)
app.secret_key = '6b70d08cbdf02f0a79324c6d61a0e356'

CREDENTIALS = {
    'vaidehi': 'vaidehi@mount',
    'aman.thakur': 'aman@mount',
    'kiran.bhandari': 'kiran@mount',
    'rahul.mali': 'rahul@mount',
    'kishan.pandey': 'kishan@mount'
}

logo_path = os.path.join('static', 'logo.png')
image1_path = os.path.join('static', 'bg1.png')
image2_path = os.path.join('static', 'bg2.png')

def fetch_image(url):
    response = requests.get(url)
    return BytesIO(response.content)

def attach_image(msg, file_path, cid):
    with open(file_path, 'rb') as file:
        img = MIMEImage(file.read())
    img.add_header('Content-ID', f'<{cid}>')
    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(file_path))
    msg.attach(img)


def send_email(to_email, pdf_bytes, customer_name, invoice_number):
    # Email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background-color: #f4f4f4;
                font-family: Arial, sans-serif;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background: #f4f4f4;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }}
            .logo {{
                max-width: 200px;
                margin: 0 auto;
                display: block;
            }}
            .content {{
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 20px;
            }}
            .shop-more {{
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }}
            .shop-more h3 {{
                margin: 0;
                padding-bottom: 10px;
            }}
            .shop-more a {{
                color: #007BFF;
                text-decoration: none;
            }}
            .shop-more a:hover {{
                text-decoration: underline;
            }}
            .image-link {{
                margin: 10px;
            }}
            .image-link img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="cid:logo" alt="Mount Shilajit Logo" class="logo">
            <div class="content">
                <p>Hello {customer_name},</p>
                <p>Please find your invoice with order number #{invoice_number} attached below.</p>
                <h4>SHOP MORE:</h4>
                <a href="https://themountshilajit.com" class="image-link">
                    <img src="cid:image1" alt="Product 1">
                </a>
                <a href="https://themountshilajit.com/collections/all" class="image-link">
                    <img src="cid:image2" alt="Product 2">
                </a>
                <p><a href="https://www.themountshilajit.com/">Visit our website</a> for more details.</p>
                <br><br><br>
                <p>Enjoy the revitalizing benefits of this Himalayan treasure as part of your daily wellness routine.</p>
                <p>Thank you for choosing Mount Shilajit.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Mount Shilajit. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    print(f"Preparing to send email to the provided email id: {to_email}...")

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("themountshilajit@gmail.com", "jblu cmcw hsct qxvx")

    msg = MIMEMultipart()
    msg['From'] = "themountshilajit@gmail.com"
    msg['To'] = to_email
    msg['Subject'] = "Invoice from Mount Shilajit !!📃🗳️"

    msg.attach(MIMEText(html_content, 'html'))
    attach_image(msg, logo_path, 'logo')
    attach_image(msg, image1_path, 'image1')
    attach_image(msg, image2_path, 'image2')

    attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
    attachment.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
    msg.attach(attachment)
    
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    print(f"Email sent to {to_email}...")
    s.quit()

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

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

    if request.method == 'POST':
        # Get form data
        invoice_date = request.form.get('invoice_date')
        invoice_number = request.form.get('invoice_number')
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')
        payment_method = request.form.get('payment_method')
        email_to_send = request.form.get('email_id')

        payment_method_type = None
        upi_reference = None
        transaction_id = None

        if payment_method == 'Online':
            payment_method_type = request.form.get('payment_method_type')
            if payment_method_type == 'UPI':
                upi_reference = request.form.get('upi_reference')
            else:
                transaction_id = request.form.get('transaction_id')

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

        pdf = HTML(string=html, base_url=request.host_url).write_pdf()
        if email_to_send:
            email_thread = threading.Thread(target=send_email, args=(email_to_send, pdf, customer_name, invoice_number))
            email_thread.start()
            return send_file(io.BytesIO(pdf),
                            download_name='invoice.pdf',
                            as_attachment=True)
        else:
            return send_file(io.BytesIO(pdf),
                            download_name='invoice.pdf',
                            as_attachment=True)


    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
