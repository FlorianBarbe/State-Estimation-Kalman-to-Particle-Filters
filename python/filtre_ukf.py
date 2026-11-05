#on applique l'UKF au même moteur, avec les mêmes mesures et conditions initiales
#on propage des points sigma au lieu de calculer des dérivées
#comme notre modèle est linéaire on doit retrouver Kalman aux arrondis près
#la variance initiale de vitesse est nulle : on ajoute 1e-12 pour permettre Cholesky
#c'est une régularisation numérique, pas une nouvelle incertitude physique
#Te est déjà inclus dans F et B ; le dt d'interface n'intervient pas dans fx

import numpy as np
from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints


def estimer(y, u, F, B, H, Q, R, x0, P0):
    y, u = np.asarray(y).ravel(), np.asarray(u).ravel()
    points = MerweScaledSigmaPoints(2, alpha=1., beta=2., kappa=1.)
    kf = UnscentedKalmanFilter(
        dim_x=2, dim_z=1, dt=1., points=points,
        fx=lambda x, dt, commande: F @ x + B.ravel() * commande,
        hx=lambda x: H @ x,
    )
    kf.x = np.asarray(x0).reshape(2).copy()
    
    kf.P = P0.copy() + 1e-12 * np.eye(2)
    kf.Q, kf.R = Q.copy(), R.copy()
    xe = np.zeros((2, len(y)))
    for k, z in enumerate(y):
        if k:
            kf.predict(commande=u[k - 1])
        
        
        #on recalcule les points sigma avec toute la covariance prédite, Q inclus
        kf.compute_process_sigmas(dt=0., fx=lambda x, dt: x)
        kf.update(np.array([z]))
        xe[:, k] = kf.x
    return xe
