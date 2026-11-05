%TP MSTAT Hugo AGOSTINI et Florian BARBE
clear all
% Initialisation des paramètres et définition de l'état initial 
% x1_0 et de la matrice de covariance de l'erreur initiale P1_0
params.D = 500e-3;
params.A = 0.1;
params.Delta = 100e-3; 
params.Te = 1e-3;
params.G = 50;
params.T = 20e-3;
params.L = 512;
params.x1 = [0; 0];
params.x1_0 = [0; 0];
params.P1_0 = [1E6 0; 0 0];
params.q = 0.5;

% Question a) 
% En tenant compte des bruits stochastiques :
% v_n : bruit blanc de processus de variance q (erreurs d'entrée u_n + v_n)
% w_n : bruit blanc de mesure de variance r (erreur de quantification y_n = \theta_n + w_n)
% Le modèle d'état discret stochastique s'écrit:
%   x_{n+1} = \bar{A} x_n + \bar{B} (u_n + v_n) = \bar{A} x_n + \bar{B} u_n + \bar{B} v_n
%   y_n     = C x_n + w_n
% où \bar{A} et \bar{B} sont obtenues par discrétisation (invariance indicielle, c2dm).


%  Question b) 
% Le codeur possède L = 512 valeurs par tour, soit une précision de 2*pi/L rad.
% L'erreur de quantification w_n est modélisée par une loi uniforme sur l'intervalle 
% [-pi/L, pi/L]. La variance r d'une loi uniforme de largeur \Delta\theta = 2*pi/L vaut :
%   r = (\Delta\theta)^2 / 12 = ((2*pi / L)^2) / 12


% Question c) 
% D'après l'énoncé, le moteur est à l'arrêt au départ (vitesse nulle), mais 
% il n'y a aucune information a priori sur la position angulaire initiale.
% 
% Vecteur d'état initial estimé  :
%   X_1/0 = [0; 0] 
%   (position initiale fixée à 0 par défaut, vitesse initiale nulle)
% 
% 2. Matrice de covariance de l'erreur initiale P_{1/0} :
%   P_1/0 = [1E6 0; 0 0] 
%  variance extrêmement grande sur la position pour traduire l'incertitude 
%   totale, et variance nulle sur la vitesse puisque la vitesse du moteur est nulle à l'arrêt


% Synthèse du signal de commande u(t) sous forme d'un créneau 
% centré, échantillonné à la période Te sur une durée totale D.

u = entree(params);
figure(1)
hold off
plot(u)

%Simulation de la dynamique du moteur à courant continu.
% Discrétisation par la méthode de l'invariance indicielle (bloqueur d'ordre 0)
% à l'aide de la fonction c2dm.
% Modélisation de la mesure y_n fournie par un codeur absolu ou incrémental
[x ,y] = simule(u,params);
figure(2)
hold off
plot(y)
hold on
plot(x(:,1))
figure(3)
hold off
plot(x(:,2))

% Implémentation du filtre de Kalman optimal récursif et stationnaire   
%( pour l'estimation en ligne de la position et de 
% la vitesse du rotor. 


Xest_optimal = Kal(y, u, params);
Xest_stationnaire = Kal_stationnaire(y, u, params);

figure(4)
hold off
plot(Xest_optimal(:,1));
title('estimation de la position avec le filtre optimal')

figure(5)
hold off
plot(Xest_stationnaire(:,1));
title('estimation de la position avec le filtre stationnaire')

figure(6)
hold off
plot(Xest_optimal(:, 2));
title('estimation de la vitesse avec le filtre optimal')

figure(7)
hold off
plot(Xest_stationnaire(:, 2));
title('estimation de la vitesse avec le filtre stationnaire')

figure('Name', 'Estimation de la Position');
hold off
plot(x(:, 1), 'k-', 'LineWidth', 1.5); 
hold on;
plot(Xest_optimal(:, 1), 'b--', 'LineWidth', 1.2);
plot(Xest_stationnaire(:, 1), 'r:', 'LineWidth', 1.2);
legend('Réel \theta', 'Optimal (Kal)', 'Stationnaire (dlqe)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Position (rad)');
title('Comparaison de la position estimée');
grid on;


figure('Name', 'Estimation de la Vitesse');
hold off
plot(x(:, 2), 'k-', 'LineWidth', 1.5); 
hold on;
plot(Xest_optimal(:, 2), 'b--', 'LineWidth', 1.2); 
plot(Xest_stationnaire(:, 2), 'r:', 'LineWidth', 1.2); 
legend('Réel \Omega', 'Optimal (Kal)', 'Stationnaire (dlqe)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Vitesse (rad/s)');
title('Comparaison de la vitesse estimée');
grid on;


figure('Name', 'Comparaison  Position');
hold off
subplot(2,1,1);
plot(x(:,1), 'k', 'LineWidth', 1.5); hold on;
plot(Xest_optimal(:,1), 'b--', 'LineWidth', 1.2);
plot(Xest_stationnaire(:,1), 'r:', 'LineWidth', 1.2);
legend('Réel (\theta)', 'Optimal (Kal)', 'Stationnaire (dlqe)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Position (rad)');
title('Comparaison de l''estimation de la Position');
grid on;


subplot(2,1,2);
plot(x(:,1) - Xest_optimal(:,1), 'b', 'LineWidth', 1); hold on;
plot(x(:,1) - Xest_stationnaire(:,1), 'r', 'LineWidth', 1);
legend('Erreur Optimal', 'Erreur Stationnaire', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Erreur de Position');
grid on;


figure('Name', 'Comparaison Vitesse');
hold off
subplot(2,1,1);
plot(x(:,2), 'k', 'LineWidth', 1.5); hold on;
plot(Xest_optimal(:,2), 'b--', 'LineWidth', 1.2);
plot(Xest_stationnaire(:,2), 'r:', 'LineWidth', 1.2);
legend('Réel (\Omega)', 'Optimal (Kal)', 'Stationnaire (dlqe)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Vitesse (rad/s)');
title('Comparaison de l''estimation de la Vitesse');
grid on;

subplot(2,1,2);
plot(x(:,2) - Xest_optimal(:,2), 'b', 'LineWidth', 1); hold on;
plot(x(:,2) - Xest_stationnaire(:,2), 'r', 'LineWidth', 1);
legend('Erreur Optimal', 'Erreur Stationnaire', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Erreur de Vitesse');
grid on;
 

params_erronne = params;
params_erronne.T = 25e-3; 


Xest_opt_err = Kal(y, u, params_erronne);
Xest_stat_err = Kal_stationnaire(y, u, params_erronne);

figure('Name', 'Modèle Imprécis position');
hold off
plot(x(:,1), 'k', 'LineWidth', 1.5); hold on;
plot(Xest_opt_err(:,1), 'b--', 'LineWidth', 1.2);
plot(Xest_stat_err(:,1), 'r:', 'LineWidth', 1.2);
legend('Réel (\Omega)', 'Optimal (modèle erroné)', 'Stationnaire (modèle erroné)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Vitesse (rad)');
title('Effet d''une mauvaise modélisation (T = 25ms au lieu de 20ms)');
grid on;

figure('Name', 'Modèle Imprécis Vitesse');
hold off
plot(x(:,2), 'k', 'LineWidth', 1.5); hold on;
plot(Xest_opt_err(:,2), 'b--', 'LineWidth', 1.2);
plot(Xest_stat_err(:,2), 'r:', 'LineWidth', 1.2);
legend('Réel (\Omega)', 'Optimal (modèle erroné)', 'Stationnaire (modèle erroné)', 'Location', 'Best');
xlabel('Échantillons (n)');
ylabel('Vitesse (rad/s)');
title('Effet d''une mauvaise modélisation (T = 25ms au lieu de 20ms)');
grid on;

% test de plusieur valeur de q avec tracé de
% l'erreur en fonction de q 

qs = linspace(0, 0.1, 100); 
erreuropt = zeros(length(qs), 2); 


for i = 1:length(qs)
    params.q = qs(i);
    
    
    Xe = Kal(y, u, params);
    
    
    % Calcul de la norme de l'erreur pour la position et la vitesse
    erreuropt(i, 1) = norm(x(:, 1) - Xe(:, 1)); 
    erreuropt(i, 2) = norm(x(:, 2) - Xe(:, 2)); 
    
end



figure('Name', 'Erreur  Position' );
hold off
plot(qs, erreuropt(:, 1), 'b-', 'LineWidth', 1.5); 
legend('Optimal (Kal)',  'Location', 'Best');
xlabel('Valeur de q');
ylabel('Norme de l''erreur de position');
title('Influence de q sur l''erreur de Position');
grid on;


figure('Name', 'Erreur  Vitesse');
hold off
plot(qs, erreuropt(:, 2), 'b-', 'LineWidth', 1.5); 
legend('Optimal (Kal)',  'Location', 'Best');
xlabel('Valeur de q ');
ylabel('Norme de l''erreur de vitesse');
title('Influence de q sur l''erreur de Vitesse'); 
grid on;

