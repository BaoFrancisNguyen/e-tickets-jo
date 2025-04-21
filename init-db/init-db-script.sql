-- Création des extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Création d'un utilisateur admin initial
-- Note: Le mot de passe est 'Admin123!' (haché avec bcrypt)
-- Ce code sera exécuté uniquement lors de la première initialisation de la base de données
INSERT INTO users (username, email, nom, prenom, password, cle_securite, date_creation, role, est_verifie)
VALUES (
    'admin',
    'admin@jo-etickets.fr',
    'Admin',
    'JO',
    '$2b$12$rYTRn6DZvDY3JlTjoGQyyuXrSJVwObDUZVlEJFV5nG3m.FLnkGpVO',  -- bcrypt hash de 'Admin123!'
    uuid_generate_v4(),
    NOW(),
    'administrateur',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- Création de quelques offres initiales
INSERT INTO offers (titre, description, type, nombre_personnes, prix, disponibilite, date_evenement, est_publie, date_creation)
VALUES 
    ('Cérémonie d''ouverture', 'Assistez à la spectaculaire cérémonie d''ouverture des Jeux olympiques 2024 à Paris.', 'solo', 1, 150.00, 100, '2024-07-26 20:00:00', TRUE, NOW()),
    ('Cérémonie d''ouverture', 'Assistez à la spectaculaire cérémonie d''ouverture des Jeux olympiques 2024 à Paris.', 'duo', 2, 280.00, 50, '2024-07-26 20:00:00', TRUE, NOW()),
    ('Cérémonie d''ouverture', 'Assistez à la spectaculaire cérémonie d''ouverture des Jeux olympiques 2024 à Paris.', 'familiale', 4, 520.00, 25, '2024-07-26 20:00:00', TRUE, NOW()),
    ('Finale Natation 100m', 'Vivez l''intensité de la finale du 100m nage libre aux Jeux olympiques 2024.', 'solo', 1, 80.00, 200, '2024-08-02 19:30:00', TRUE, NOW()),
    ('Finale Natation 100m', 'Vivez l''intensité de la finale du 100m nage libre aux Jeux olympiques 2024.', 'duo', 2, 150.00, 100, '2024-08-02 19:30:00', TRUE, NOW()),
    ('Finale Natation 100m', 'Vivez l''intensité de la finale du 100m nage libre aux Jeux olympiques 2024.', 'familiale', 4, 280.00, 50, '2024-08-02 19:30:00', TRUE, NOW()),
    ('Finale Athlétisme 100m', 'Assistez à la finale du 100m, l''épreuve reine de l''athlétisme aux JO 2024.', 'solo', 1, 100.00, 150, '2024-08-10 21:00:00', TRUE, NOW()),
    ('Finale Athlétisme 100m', 'Assistez à la finale du 100m, l''épreuve reine de l''athlétisme aux JO 2024.', 'duo', 2, 180.00, 75, '2024-08-10 21:00:00', TRUE, NOW()),
    ('Finale Athlétisme 100m', 'Assistez à la finale du 100m, l''épreuve reine de l''athlétisme aux JO 2024.', 'familiale', 4, 320.00, 40, '2024-08-10 21:00:00', TRUE, NOW())
ON CONFLICT DO NOTHING;