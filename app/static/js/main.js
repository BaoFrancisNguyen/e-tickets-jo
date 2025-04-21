/**
 * Script principal pour l'application JO E-Tickets
 */

document.addEventListener('DOMContentLoaded', function() {
    // Activation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Activation des popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-disparition des alertes après 5 secondes
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Validation côté client des formulaires
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Formatter les numéros de carte de crédit (espacer tous les 4 chiffres)
    var cardNumberInput = document.getElementById('card_number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            var target = e.target;
            var value = target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            var formattedValue = '';
            
            for (var i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
            }
        });
    }
});
                formattedValue += value[i];
            }
            
            target.value = formattedValue;
        });
    }
    
    // Fonction pour mettre à jour la quantité dans le panier
    var quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            var form = this.closest('form');
            form.submit();
        });
    });
    
    // Boutons d'incrémentation et de décrémentation de quantité
    var incrementButtons = document.querySelectorAll('.btn-increment');
    var decrementButtons = document.querySelectorAll('.btn-decrement');
    
    incrementButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var input = this.closest('.input-group').querySelector('.quantity-input');
            var currentValue = parseInt(input.value);
            var maxValue = parseInt(input.getAttribute('max'));
            
            if (currentValue < maxValue) {
                input.value = currentValue + 1;
                // Déclencher l'événement change pour soumettre le formulaire
                var event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    });
    
    decrementButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var input = this.closest('.input-group').querySelector('.quantity-input');
            var currentValue = parseInt(input.value);
            var minValue = parseInt(input.getAttribute('min'));
            
            if (currentValue > minValue) {
                input.value = currentValue - 1;
                // Déclencher l'événement change pour soumettre le formulaire
                var event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    });
    
    // Filtre des offres
    var offerTypeSelect = document.getElementById('offer-type-filter');
    if (offerTypeSelect) {
        offerTypeSelect.addEventListener('change', function() {
            var selectedType = this.value;
            var url = new URL(window.location.href);
            
            if (selectedType) {
                url.searchParams.set('type', selectedType);
            } else {
                url.searchParams.delete('type');
            }
            
            window.location.href = url.toString();
        });
    }
    
    // Scanner de QR code (pour la page de vérification des billets)
    var scanButton = document.getElementById('scan-button');
    if (scanButton) {
        scanButton.addEventListener('click', function() {
            // Cette fonction simule un scan de QR code
            // Dans une application réelle, on utiliserait l'API WebRTC pour accéder à la caméra
            alert('Cette fonctionnalité nécessite l\'accès à la caméra. Dans une application réelle, vous pourriez scanner un QR code ici.');
        });
    }
    
    // Charts pour les statistiques admin (utilise Chart.js)
    var offersChartCanvas = document.getElementById('offers-chart');
    if (offersChartCanvas && typeof Chart !== 'undefined') {
        var offersData = JSON.parse(offersChartCanvas.getAttribute('data-offers'));
        
        new Chart(offersChartCanvas, {
            type: 'pie',
            data: {
                labels: offersData.labels,
                datasets: [{
                    data: offersData.data,
                    backgroundColor: [
                        '#0d6efd',
                        '#20c997',
                        '#fd7e14'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                stacked: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Nombre de commandes'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        title: {
                            display: true,
                            text: 'Ventes (€)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Évolution des ventes'
                    }
                }
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Répartition des billets par type d\'offre'
                    }
                }
            }
        });
    }
    
    var salesChartCanvas = document.getElementById('sales-chart');
    if (salesChartCanvas && typeof Chart !== 'undefined') {
        var salesData = JSON.parse(salesChartCanvas.getAttribute('data-sales'));
        
        new Chart(salesChartCanvas, {
            type: 'line',
            data: {
                labels: salesData.labels,
                datasets: [
                    {
                        label: 'Nombre de commandes',
                        data: salesData.orders,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Ventes (€)',
                        data: salesData.sales,
                        borderColor: '#20c997',
                        backgroundColor: 'rgba(32, 201, 151, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                