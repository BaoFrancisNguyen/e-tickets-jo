from flask_admin import AdminIndexView
from flask_login import current_user
from flask import redirect, url_for, flash, request

class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'administrateur'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('auth.login', next=request.url))