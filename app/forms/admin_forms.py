from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Email
from datetime import datetime

class OfferForm(FlaskForm):
    """
    Formulaire de création/modification d'une offre.
    """
    titre = StringField('Titre', validators=[
        DataRequired(),
        Length(min=5, max=100)
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    
    type = SelectField('Type', choices=[
        ('solo', 'Solo (1 personne)'),
        ('duo', 'Duo (2 personnes)'),
        ('familiale', 'Familiale (4 personnes)')
    ], validators=[DataRequired()])
    
    nombre_personnes = IntegerField('Nombre de personnes', validators=[
        DataRequired(),
        NumberRange(min=1, max=4)
    ])
    
    prix = FloatField('Prix (€)', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    date_evenement = DateTimeField('Date de l\'événement', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    
    disponibilite = IntegerField('Disponibilité', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images uniquement')
    ])
    
    est_publie = BooleanField('Publier l\'offre')
    
    submit = SubmitField('Enregistrer')
    
    def validate_date_evenement(self, date_evenement):
        """Vérifie que la date de l'événement est dans le futur."""
        if date_evenement.data < datetime.utcnow():
            raise ValidationError('La date de l\'événement doit être dans le futur.')
    
    def validate_nombre_personnes(self, nombre_personnes):
        """Vérifie que le nombre de personnes correspond au type d'offre sélectionné."""
        type_to_persons = {
            'solo': 1,
            'duo': 2,
            'familiale': 4
        }
        
        if nombre_personnes.data != type_to_persons.get(self.type.data):
            raise ValidationError(f'Le nombre de personnes pour une offre {self.type.data} doit être {type_to_persons.get(self.type.data)}.')

class UserForm(FlaskForm):
    """
    Formulaire de modification d'un utilisateur.
    """
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    
    email = StringField('Adresse email', validators=[
        DataRequired(),
        Email()
    ])
    
    nom = StringField('Nom', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    prenom = StringField('Prénom', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    role = SelectField('Rôle', choices=[
        ('utilisateur', 'Utilisateur'),
        ('employe', 'Employé'),
        ('administrateur', 'Administrateur')
    ])
    
    est_verifie = BooleanField('Compte vérifié')
    
    submit = SubmitField('Enregistrer')
