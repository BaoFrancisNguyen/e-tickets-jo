from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.ticket import Ticket
from app.models.order import Order
from app.services.qrcode_service import generate_ticket_qrcode, verify_qrcode, scan_ticket
import io
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/')
@login_required
def index():
    """
    Affiche les billets de l'utilisateur.
    """
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('tickets/index.html', tickets=tickets)

@tickets_bp.route('/<int:ticket_id>')
@login_required
def detail(ticket_id):
    """
    Affiche les détails d'un billet spécifique.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire du billet
    if ticket.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à ce billet.', 'danger')
        return redirect(url_for('tickets.index'))
    
    # Générer le QR code si nécessaire
    if not ticket.qr_code:
        ticket.qr_code = generate_ticket_qrcode(ticket.id)
        db.session.commit()
    
    return render_template('tickets/detail.html', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/download')
@login_required
def download(ticket_id):
    """
    Télécharge un billet au format PDF avec un design amélioré.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire du billet
    if ticket.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à accéder à ce billet.', 'danger')
        return redirect(url_for('tickets.index'))
    
    try:
        # Importation des modules nécessaires
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        import tempfile
        import os
        
        # Création du buffer pour le PDF
        buffer = io.BytesIO()
        
        # Dimensions de la page
        width, height = A4
        
        # Création du PDF
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Chemin vers l'image de bannière
        banner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images', 'olympic-banner.jpg')
        
        # Ajout de l'image du bandeau en haut (pleine largeur)
        if os.path.exists(banner_path):
            # Hauteur du bandeau (60mm)
            banner_height = 60*mm
            # Dessiner l'image en haut de la page sur toute la largeur
            pdf.drawImage(banner_path, 0, height - banner_height, width=width, height=banner_height, preserveAspectRatio=False)
        else:
            # Fallback si l'image n'existe pas: simple rectangle coloré
            pdf.setFillColorRGB(0, 0.32, 0.6)  # Bleu olympique
            pdf.rect(0, height - 60*mm, width, 60*mm, fill=1)
        
        # Information sur l'événement
        pdf.setFillColorRGB(0, 0, 0)  # Texte noir
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(20*mm, height - 80*mm, ticket.offer.titre)
        
        # Rectangle d'information (sans opacité)
        pdf.setFillColorRGB(0.95, 0.95, 1)  # Fond bleu très clair
        pdf.rect(20*mm, height - 160*mm, width - 40*mm, 70*mm, fill=1, stroke=1)
        
        # Détails de l'événement
        pdf.setFillColorRGB(0, 0, 0)  # Texte noir
        pdf.setFont("Helvetica-Bold", 12)
        
        # Icônes et informations
        y_position = height - 95*mm
        line_height = 10*mm
        
        # Date et heure
        pdf.drawString(25*mm, y_position, "Date et heure:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(70*mm, y_position, ticket.offer.date_evenement.strftime('%d/%m/%Y à %H:%M'))
        y_position -= line_height
        
        # Type de billet
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25*mm, y_position, "Type de billet:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(70*mm, y_position, f"{ticket.offer.type.capitalize()} ({ticket.offer.nombre_personnes} {'personne' if ticket.offer.nombre_personnes == 1 else 'personnes'})")
        y_position -= line_height
        
        # Numéro de billet
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25*mm, y_position, "Numéro du billet:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(70*mm, y_position, f"#{ticket.id}")
        y_position -= line_height
        
        # Titulaire
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25*mm, y_position, "Titulaire:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(70*mm, y_position, f"{current_user.prenom} {current_user.nom}")
        y_position -= line_height
        
        # Référence
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25*mm, y_position, "Référence:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(70*mm, y_position, ticket.order.reference)
        y_position -= line_height
        
        # QR Code
        if ticket.qr_code and 'base64' in ticket.qr_code:
            try:
                # Extraire la partie base64
                qr_data = ticket.qr_code.split(',')[1]
                qr_image_data = base64.b64decode(qr_data)
                
                # Créer un fichier temporaire pour l'image
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_file.write(qr_image_data)
                temp_file.close()
                
                # Ajouter le QR code
                pdf.drawImage(temp_file.name, width - 70*mm, height - 150*mm, width=50*mm, height=50*mm)
                
                # Légende du QR code
                pdf.setFont("Helvetica", 10)
                pdf.drawString(width - 65*mm, height - 155*mm, "Scannez ce code à l'entrée")
                
                # Supprimer le fichier temporaire
                os.unlink(temp_file.name)
                
            except Exception as e:
                print(f"Erreur lors de l'ajout du QR code: {str(e)}")

        # Information importante encadrée (sans opacité)
        pdf.setFillColorRGB(1, 1, 1)  # Fond blanc
        pdf.rect(20*mm, height - 220*mm, width - 40*mm, 50*mm, fill=1, stroke=1)
        
        # Titre de la section
        pdf.setFillColorRGB(0, 0, 0)  # Texte noir
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(25*mm, height - 175*mm, "Informations importantes")
        
        # Points d'information
        pdf.setFont("Helvetica", 11)
        y_position = height - 190*mm
        
        pdf.drawString(30*mm, y_position, "• Présentez ce billet (imprimé ou sur smartphone) à l'entrée du site.")
        y_position -= 8*mm
        
        pdf.drawString(30*mm, y_position, "• Une pièce d'identité vous sera demandée pour vérification.")
        y_position -= 8*mm
        
        pdf.drawString(30*mm, y_position, "• Prévoyez d'arriver au moins 1 heure avant le début de l'événement.")
        y_position -= 8*mm
        
        pdf.drawString(30*mm, y_position, "• Ce billet est personnel et ne peut être revendu.")
        
        # Pied de page
        pdf.setFillColorRGB(0, 0.32, 0.6)  # Bleu olympique
        pdf.rect(0, 0, width, 15*mm, fill=1)
        
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(1, 1, 1)  # Texte blanc
        pdf.drawCentredString(width/2, 5*mm, "Paris 2024 - Tous droits réservés - Document officiel")
        
        # Finaliser le PDF
        pdf.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"billet-jo-{ticket.id}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'danger')
        return redirect(url_for('tickets.detail', ticket_id=ticket.id))

@tickets_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    """
    Vérifie l'authenticité d'un billet à partir d'un QR code.
    Cette route est utilisée par les employés le jour de l'événement.
    """
    # Vérifier que l'utilisateur a le rôle employé ou administrateur
    if current_user.role not in ['employe', 'administrateur']:
        flash('Vous n\'êtes pas autorisé à accéder à cette page.', 'danger')
        return redirect(url_for('main.index'))
    
    result = None
    
    if request.method == 'POST':
        # Récupérer les données du QR code
        qr_data = request.form.get('qr_data')
        
        if qr_data:
            # Vérifier l'authenticité du QR code
            success, verification_result = verify_qrcode(qr_data)
            
            if success:
                ticket = verification_result
                result = {
                    'valid': True,
                    'ticket_id': ticket.id,
                    'offer': ticket.offer.titre,
                    'type': ticket.offer.type,
                    'date': ticket.offer.date_evenement.strftime('%d/%m/%Y %H:%M'),
                    'user': f"{ticket.user.prenom} {ticket.user.nom}",
                    'status': 'Valide' if ticket.est_valide else 'Déjà utilisé'
                }
            else:
                result = {
                    'valid': False,
                    'message': verification_result
                }
    
    return render_template('tickets/verify.html', result=result)

@tickets_bp.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    """
    Scanne et valide un billet à partir d'un QR code.
    Cette route est utilisée par les employés le jour de l'événement.
    """
    # Vérifier que l'utilisateur a le rôle employé ou administrateur
    if current_user.role not in ['employe', 'administrateur']:
        flash('Vous n\'êtes pas autorisé à accéder à cette page.', 'danger')
        return redirect(url_for('main.index'))
    
    result = None
    
    if request.method == 'POST':
        # Récupérer les données du QR code
        qr_data = request.form.get('qr_data')
        
        if qr_data:
            # Scanner et valider le billet
            success, scan_result = scan_ticket(qr_data)
            
            if success:
                result = {
                    'valid': True,
                    'ticket_id': scan_result['ticket_id'],
                    'offer': scan_result['offer'],
                    'user': scan_result['user'],
                    'validated_at': scan_result['validated_at']
                }
            else:
                result = {
                    'valid': False,
                    'message': scan_result
                }
    
    return render_template('tickets/scan.html', result=result)

@tickets_bp.route('/api/validate/<int:ticket_id>', methods=['POST'])
@login_required
def api_validate(ticket_id):
    """
    API pour valider un billet.
    """
    # Vérifier que l'utilisateur a le rôle employé ou administrateur
    if current_user.role not in ['employe', 'administrateur']:
        return jsonify({'success': False, 'message': 'Non autorisé'}), 403
    
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.validate():
        return jsonify({
            'success': True,
            'message': 'Billet validé avec succès',
            'ticket': ticket.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': 'Échec de la validation du billet'}), 400