#2.3 d.2 : ici on cherche un gain constant de correction
#on calcule une seule fois la covariance permanente avec Riccati, puis K_inf
#on corrige ensuite xs avec le même gain à chaque mesure
#attention au gain de dlqe : selon la convention il correspond à F*K_inf
#ici K_inf corrige l'état courant, pas directement la prédiction suivante
#P0 reste dans les arguments pour garder la même interface mais ne règle pas le gain permanent
#dans notre moteur, si q=0 alors K_inf=0 : l'erreur initiale de position reste

import numpy as np
from scipy.linalg import solve_discrete_are


def estimer(y, u, F, B, H, Q, R, x0, P0):
    y, u = np.asarray(y).ravel(), np.asarray(u).ravel()
    
    if np.count_nonzero(Q) == 0:
        K = np.zeros((2, 1))
    else:
        
        #problème dual de Riccati pour trouver la covariance de prédiction permanente
        P = solve_discrete_are(F.T, H.T, Q, R)
        K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
    xs = np.asarray(x0).reshape(2, 1).copy()
    xe = np.zeros((2, len(y)))
    for k, z in enumerate(y):
        if k:
            xs = F @ xs + B * u[k - 1]
        
        #correction de la prédiction avec le gain constant
        xs += K @ (np.array([[z]]) - H @ xs)
        xe[:, k] = xs.ravel()
    return xe
