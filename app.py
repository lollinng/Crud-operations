from dataclasses import dataclass
from decimal import Decimal
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app) 


"""
Completed tasks:

1) Create and deleted operations are performed
2) All Validation are working
"""
@dataclass
class InvoiceHeaders(db.Model):

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    date = db.Column(db.String())
    invoiceNumber = db.Column(db.Integer,unique=True)
    CustomerName = db.Column(db.String(30))
    BullingAddress = db.Column(db.String(100))
    ShoppingAddress = db.Column(db.String(100))
    GSTIN = db.Column(db.String(30),unique=True)
    TotalAmount = db.Column(db.Numeric(10,2))
    # InvoiceItems_ = db.relationship('InvoiceItems',backref='invoiceHeaders') 
    # InvoiceBillSundrys_ = db.relationship('InvoiceBillSundry',backref='header_')

@dataclass
class InvoiceItems(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    itemName = db.Column(db.String(30))
    Quantity = db.Column(db.Numeric(10,2))
    Price = db.Column(db.Numeric(10,2))
    Amount = db.Column(db.Numeric(10,2))
    # header_id = db.Column(db.Integer,db.ForeignKey('invoiceHeaders.id'))

@dataclass
class InvoiceBillSundry(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    itemName = db.Column(db.String(30))
    Amount = db.Column(db.Numeric(10,2))
    # header_id = db.Column(db.Integer,db.ForeignKey('InvoiceHeaders.id'))


@app.route('/create')
def create_entry():
    data = request.json
    if data:

        # header items
        header_dat = data.get('invoiceHeaders')
        h_Date = header_dat['Date'] 
        h_InvoiceNumber =  int(header_dat['InvoiceNumber'])
        h_CustomerName = header_dat['CustomerName'] 
        h_ShippingAddress =  header_dat['ShippingAddress'] 
        h_BillingAddress =  header_dat['BillingAddress'] 
        h_GSTIN =  header_dat['GSTIN'] 
        TotalAmount =  Decimal(header_dat['TotalAmount'])
        header_ = InvoiceHeaders(date=h_Date,invoiceNumber=h_InvoiceNumber,CustomerName=h_CustomerName,ShoppingAddress=h_ShippingAddress,BullingAddress=h_BillingAddress,GSTIN=h_GSTIN,TotalAmount=TotalAmount)
        db.session.add(header_)

        # items
        Items_data = data.get('invoiceItems')
        sum_of_invoice_amt = 0
        for i in Items_data:
            i['Amount'] = Decimal(i['Amount'])
            i['Quantity'] = Decimal(i['Quantity'])
            i['Price'] = Decimal(i['Price'])

            sum_of_invoice_amt +=  i['Amount']

            if  i['Amount']!= i['Quantity'] * i['Price'] or i['Amount']<0 or i['Quantity']<0 or i['Price']<0:
                return {"Error":"Failed Validation"}

            i_item_Name =  i['item_Name']
            i_Quantity =  i['Quantity']
            i_Price =  i['Price']
            i_Amount =  i['Amount']

            items_ = InvoiceItems(itemName=i_item_Name,Quantity=i_Quantity,Price=i_Price,Amount=i_Amount)
            db.session.add(items_)


        #sundry data
        bill_sundry_data = data.get('invoiceBillSundry')
        sum_of_bill = 0     
        for i in bill_sundry_data:
            i_Amount = Decimal(i['Amount'])
            sum_of_bill += i_Amount
            i_billSundryNamee =  i['billSundryName']
            bills_ = InvoiceBillSundry(itemName=i_billSundryNamee,Amount=i_Amount)
            db.session.add(bills_)

        if TotalAmount != sum_of_invoice_amt + sum_of_bill:
             return {"Error":"Failed Validation"}

        db.session.commit()
        return {'Code':201}        
    return {"Error":"No data"}


@app.route('/delete/<type_>/<id_>')
def delete_entry(type_,id_):

    if type_=='invoiceHeaders':
        InvoiceHeaders.query.filter_by(id=id_).delete()
    elif type_ == 'invoiceItems':
        InvoiceItems.query.filter_by(id=id_).delete()
    elif type_== 'invoiceBillSundry':
        InvoiceBillSundry.query.filter_by(id=id_).delete()
    else:
        return {"Error":"Wrong type"}
    db.session.commit()
    return {"Code":204 }


# INComplete function
@app.route('/query/<type_>/<id_>')
def query_data(type_,id_):

    if type_=='invoiceHeaders':
        data = InvoiceHeaders.query.filter_by(id=id_).first()
        print(data)
    elif type_ == 'invoiceItems':
        InvoiceItems.query.filter_by(id=id_).first()
    elif type_== 'invoiceBillSundry':
        InvoiceBillSundry.query.filter_by(id=id_).first()
    else:
        return {"Error":"Wrong type"}
    db.session.commit()
    return {"Code":200 }




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


    