from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Regexp
from datetime import datetime

class CartItemForm(FlaskForm):
    """
    Formulaire pour ajouter un article au panier.
    """
    quantity = IntegerField('Quantité', validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='La quantité doit être comprise entre 1 et 10.')
    ])
    
    submit = SubmitField('Ajouter au panier')

class PaymentForm(FlaskForm):
    """
    Formulaire de paiement.
    """
    card_number = StringField('Numéro de carte', validators=[
        DataRequired(),
        Regexp(r'^\d{13,19}$', message='Le numéro de carte doit contenir entre 13 et 19 chiffres.')
    ])
    
    card_holder = StringField('Titulaire de la carte', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Le nom du titulaire doit contenir entre 2 et 100 caractères.')
    ])
    
    expiry_month = SelectField('Mois d\'expiration', choices=[
        ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12')
    ], validators=[DataRequired()])
    
    expiry_year = SelectField('Année d\'expiration', validators=[DataRequired()])
    
    cvv = StringField('CVV', validators=[
        DataRequired(),
        Regexp(r'^\d{3,4}$', message='Le CVV doit contenir 3 ou 4 chiffres.')
    ])
    
    submit = SubmitField('Payer')
    
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        
        # Générer les années d'expiration dynamiquement
        current_year = datetime.utcnow().year
        years = [(str(current_year + i)[-2:], str(current_year + i)) for i in range(21)]  # 20 ans à partir de l'année courante
        self.expiry_year.choices = years
    
    def validate_expiry_date(self, form, field):
        """
        Vérifie que la date d'expiration n'est pas passée.
        Cette méthode est appelée après la validation de chaque champ.
        """
        try:
            month = int(self.expiry_month.data)
            year = int('20' + self.expiry_year.data)  # Convertir en année à 4 chiffres
            
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            
            if year < current_year or (year == current_year and month < current_month):
                raise ValidationError('La date d\'expiration est dépassée.')
        except ValueError:
            pass  # Les autres validateurs s'occuperont de ce cas
