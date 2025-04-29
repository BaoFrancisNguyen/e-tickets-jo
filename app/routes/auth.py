from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models.user import User
from app.services.auth_service import (
    register_user, verify_account, login_user as auth_login_user,
    setup_2fa, verify_2fa_code, change_password,
    reset_password_request, reset_password
)
from app.forms.auth_forms import (
    RegistrationForm, LoginForm, TwoFactorForm,
    ChangePasswordForm, RequestResetForm, ResetPasswordForm
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        current_app.logger.info(f"Tentative d'inscription avec les données: {request.form}")
    
    if form.validate_on_submit():
        try:
            success, result = register_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                nom=form.nom.data,
                prenom=form.prenom.data
            )
            
            if success:
                flash('Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(f"Erreur lors de l'inscription: {result}", 'danger')
        except Exception as e:
            current_app.logger.error(f"Exception lors de l'inscription: {str(e)}")
            flash(f"Une erreur s'est produite: {str(e)}", 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erreur dans le champ {getattr(form, field).label.text}: {error}", 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/debug-users')
def debug_users():
    """Route temporaire pour déboguer les utilisateurs."""
    from app.models.user import User
    
    # Vérifier si l'utilisateur est connecté et est admin
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        users_count = User.query.count()
        return f"Nombre d'utilisateurs dans la base de données: {users_count}. Connectez-vous en tant qu'administrateur pour plus de détails."
    
    # Obtenir tous les utilisateurs
    users = User.query.all()
    user_list = []
    
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'date_creation': user.date_creation.strftime('%Y-%m-%d %H:%M:%S') if user.date_creation else None
        })
    
    return jsonify(user_list)

@auth_bp.route('/remove-user/<email>')
def remove_user(email):
    """Route temporaire pour supprimer un utilisateur par email."""
    # Uniquement accessible à l'administrateur
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        flash('Accès refusé. Connectez-vous en tant qu\'administrateur.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'Utilisateur avec email {email} supprimé avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    else:
        flash(f'Aucun utilisateur trouvé avec l\'email {email}.', 'warning')
    
    return redirect(url_for('admin_custom.users') if current_user.role == 'administrateur' else url_for('main.index'))

@auth_bp.route('/create-test-user')
def create_test_user():
    """Route temporaire pour créer un utilisateur de test."""
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(email="testuser@example.com").first():
        flash('Utilisateur de test existe déjà.', 'info')
        return redirect(url_for('auth.login'))
        
    try:
        from app import bcrypt
        
        # Créer directement l'utilisateur sans passer par register_user
        hashed_password = bcrypt.generate_password_hash("TestUser123!").decode('utf-8')
        user = User(
            username="testuser",
            email="testuser@example.com",
            password=hashed_password,
            nom="Test",
            prenom="User",
            est_verifie=True
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Utilisateur de test créé avec succès. Vous pouvez maintenant vous connecter avec email: testuser@example.com et mot de passe: TestUser123!', 'success')
    except Exception as e:
        flash(f"Exception: {str(e)}", 'danger')
        
    return redirect(url_for('auth.login'))

@auth_bp.route('/quick-register', methods=['GET', 'POST'])
def quick_register():
    """Route simplifiée pour l'inscription."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        
        # Vérifications manuelles simples
        if not all([username, email, password, confirm_password, nom, prenom]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('auth/quick_register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('auth/quick_register.html')
        
        # Vérifier manuellement si l'email existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('auth/quick_register.html')
        
        # Créer l'utilisateur directement
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            nom=nom,
            prenom=prenom,
            est_verifie=True
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/quick_register.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Page de réinitialisation de mot de passe."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        success, message = reset_password(token, form.password.data)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            return redirect(url_for('auth.request_reset'))
    
    return render_template('auth/reset_token.html', form=form)


@auth_bp.route('/verify/<code>')
def verify_account_route(code):
    """Route de vérification de compte."""
    success, message = verify_account(code)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(message, 'danger')
        return redirect(url_for('main.index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        success, result = auth_login_user(
            email=form.email.data,
            password=form.password.data
        )
        
        if success:
            user = result
            
            # Vérifier si l'authentification à deux facteurs est activée
            if user.est_2fa_active:
                # Stocker l'ID utilisateur en session pour la vérification 2FA
                session['user_id_for_2fa'] = user.id
                return redirect(url_for('auth.two_factor'))
            
            remember = form.remember.data
            login_user(user, remember=remember)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash(result, 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """Page d'authentification à deux facteurs."""
    if current_user.is_authenticated or 'user_id_for_2fa' not in session:
        return redirect(url_for('main.index'))
    
    form = TwoFactorForm()
    
    if form.validate_on_submit():
        user_id = session['user_id_for_2fa']
        user = User.query.get(user_id)
        
        if not user:
            flash('Utilisateur non trouvé.', 'danger')
            return redirect(url_for('auth.login'))
        
        success, message = verify_2fa_code(user, form.code.data)
        
        if success:
            # Supprimer l'ID utilisateur de la session
            session.pop('user_id_for_2fa', None)
            
            # Connecter l'utilisateur
            login_user(user, remember=False)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/two_factor.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion."""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Page de profil."""
    return render_template('auth/profile.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password_route():
    """Page de changement de mot de passe."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        success, message = change_password(
            user=current_user,
            current_password=form.current_password.data,
            new_password=form.new_password.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa_route():
    """Page de configuration de l'authentification à deux facteurs."""
    if current_user.est_2fa_active:
        flash('L\'authentification à deux facteurs est déjà activée.', 'info')
        return redirect(url_for('auth.profile'))
    
    success, result = setup_2fa(current_user)
    
    if not success:
        flash(result, 'danger')
        return redirect(url_for('auth.profile'))
    
    # Stocker le secret en session pour la vérification
    session['setup_2fa_secret'] = result['secret']
    
    return render_template('auth/setup_2fa.html', uri=result['uri'])

@auth_bp.route('/verify-2fa', methods=['POST'])
@login_required
def verify_2fa_setup():
    """Vérification de la configuration de l'authentification à deux facteurs."""
    if 'setup_2fa_secret' not in session:
        flash('Session expirée. Veuillez recommencer la configuration.', 'danger')
        return redirect(url_for('auth.setup_2fa_route'))
    
    code = request.form.get('code')
    
    if not code:
        flash('Veuillez fournir un code.', 'danger')
        return redirect(url_for('auth.setup_2fa_route'))
    
    # Vérifier le code
    import pyotp
    totp = pyotp.TOTP(session['setup_2fa_secret'])
    
    if totp.verify(code):
        # Activer l'authentification à deux facteurs
        current_user.code_2fa_secret = session['setup_2fa_secret']
        current_user.enable_2fa()
        
        # Supprimer le secret de la session
        session.pop('setup_2fa_secret', None)
        
        flash('L\'authentification à deux facteurs a été activée avec succès.', 'success')
        return redirect(url_for('auth.profile'))
    else:
        flash('Code incorrect. Veuillez réessayer.', 'danger')
        return redirect(url_for('auth.setup_2fa_route'))

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Désactivation de l'authentification à deux facteurs."""
    if not current_user.est_2fa_active:
        flash('L\'authentification à deux facteurs n\'est pas activée.', 'info')
        return redirect(url_for('auth.profile'))
    
    current_user.disable_2fa()
    current_user.code_2fa_secret = None
    db.session.commit()
    
    flash('L\'authentification à deux facteurs a été désactivée avec succès.', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def request_reset():
    """Page de demande de réinitialisation de mot de passe."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestResetForm()
    
    if form.validate_on_submit():
        success, message = reset_password_request(form.email.data)
        flash(message, 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/request_reset.html', form=form)