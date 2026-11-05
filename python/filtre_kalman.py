#2.3 d.1 : filtre de Kalman optimal, le gain dépend du temps
#on utilise FilterPy pour faire les prédictions et corrections successives
#doc : https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
#x : estimation de theta et omega (2,1), z : mesure du codeur (1,1)
#P : covariance de l'erreur d'estimation (2,2), pas celle de l'état réel
#F : transition (2,2), B : commande discrète Bd (2,1), H : mesure (1,2)
#Q : bruit de processus (2,2), R : variance de mesure sous forme (1,1)
#K : gain recalculé par update() à partir de l'incertitude du moment
#x0 et P0 sont la prédiction initiale X_hat_1/0 et sa covariance P_1/0

import numpy as np
from filterpy.kalman import KalmanFilter


def estimer(y, u, F, B, H, Q, R, x0, P0):
    y, u = np.asarray(y).ravel(), np.asarray(u).ravel()
    
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.F, kf.B, kf.H = F.copy(), B.copy(), H.copy()
    kf.Q, kf.R = Q.copy(), R.copy()
    kf.x, kf.P = np.asarray(x0).reshape(2, 1).copy(), P0.copy()
    xe = np.zeros((2, len(y)))
    
    #on utilise directement la première mesure car x0 correspond déjà au premier instant
    for k, z in enumerate(y):
        if k:
            
            #1) prédiction avec la commande de l’intervalle précédent
            kf.predict(u=np.array([[u[k - 1]]]))
        
        #2) correction avec la mesure courante, mise à jour de P et du gain
        kf.update(np.array([[z]]))
        
        #3) on conserve les deux composantes estimées
        xe[:, k] = kf.x.ravel()
    return xe
