import matplotlib.pyplot as plt
import numpy as np
import parametres as p
import main as m
#contexte posé par le sujet du problème :
#w_k : bruit gaussien de mesure supposé blanc du codeur
#r : variance du bruit de mesure supposé blanc du codeur (y_k=theta_k+w_k)
#u_k+v_k : entrée réelle du système, avec u_k bruit blanc de variance q, idpdt de w_k, u_k la tension d'alimentation du moteur à courant continu
#on impose u_0=0, mais on ne connait pas theta_0

## a) Représentation d'état stoechastique du modèle du système d'entrée u_k et de sortie y_k :
#x_k+1=F*x_k +B*(u_k+v_k), ou F=exp(A*Te), B=integrale(exp(A*t)*B dt de 0 à Te)
#y_k=H*x_k+w_k, ou H=[1 0]
#ces deux équations représentent respectivement le bruitage sur la tension et celui sur la mesure de x

## b) proposition de valeur de r : 
#w_k est le bruit issu du codeur incrémental à L fentes, de résolution delta=2*pi/L. On modélise en général l'erreur de quantification par un bruit uniforme sur l'intervalle [-delta/2, delta/2], de variance r=delta^2/12. On peut donc proposer r=delta^2/12
#on prendra donc r=delta^2/12 pour le bruit de mesure du codeur incrémental

r=p.pas**2/12 #variance du bruit de mesure du codeur incrémental

##c) Proposition d'une initialisation de la prédiction de l’état X̂1/0 et de la variance de l’erreur de prédiction P1/0 , d’après les connaissances a priori.
#on sait que la vitesse initiale est nule
#on metta arbitrairement la position initiale à 0, mais on ne connait pas la position initiale réelle theta_0 : on propose cette valeur avec bcp d'incertitude et on prendre donc P(11)1/0=M, avec M grande. 
# Les autres incertitudes sont nulles car on connaît la vitesse initiale nulle
#  On propose donc X̂1/0=[0,0] et P1/0=[[M,0],[0,0]] avec M grande. On prendra M=1000 rad^2 pour la position initiale

#X_hat_1_0=np.array([[0],[0]]) 
#P_1_0=np.array([[p.M,0],[0,0]]) 
#calculés dans parametres.py

##d) programons le filtre de Kalman
#d.1) Filtre de Kalman idéal

#implementation du filtre de Kalman à partir de la simulation du moteur à courant continu dans main.py
#on cherche à estimer les deux composantes x_k=(theta_k, omega_k)et y_k=theta_k+erreur de mesure
#on utilise la classe KalmanFilter détaillée ici https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html

#détails sur les variables de la classes dispos deans la documentation : 

    # x : ndarray (dim_x, 1), vecteur d'état contenant theta_k et omega_k de taille dim_x=2
    # z : ndarray (dim_z, 1), vecteur de mesure contenant theta_k
    # P: ndarray  (dim_x, dim_x) la matrice de covariance;
    # Q: ndarray (dim_x, dim_x), incertitude du procédé/bruit
    #R: ndarray (dim_z, dim_z), incertitude sur la mesure/bruit : ici la variance du bruit de mesure du codeur incrémental r=delta^2/12 choisi avec la loi uniforme
    #H : ndarray (dim_z, dim_x)fonction de mesure
    #F : ndarray (dim_x, dim_x) matrice de transition d'état
    #B : ndarray (dim_x, dim_u), par défaut 0, matrice de contrôle de transition


#création du filtre avant de boucler les prédictions et corrections successives
from filterpy.kalman import KalmanFilter
kf=KalmanFilter(dim_x=2 , dim_z=1) #on crée un objet kf de la classe KalmanFilter avec 2 dimensions d'état (angle et vitesse angulaire) et 1 dimension de mesure

#on ramène toutes les matrices du modèle discret exact à entrée constante dans le filtre de Kalman (évaluées dans parametres.py d'après les questions précédentes)
kf.F = p.F.copy()
kf.B = p.Bd.copy()
kf.H = p.H.copy()
kf.Q = p.Q.copy()
kf.R = p.R.copy()
kf.x = p.x0_estime.copy()
kf.P = p.P0.copy()+np.eye(2)*1000000

# Simulation
u = m.entree(p.D, p.Acc, p.delta, p.Te)

x, y, e = m.simule(u, p.G, p.T, p.Te, p.pas, p.x1)

N = y.shape[1]
x_estime = np.zeros((2, N))
P_estime = np.zeros((2, 2, N))

# L'initialisation de kf correspond déjà au premier instant :
# on utilise donc directement la première mesure
kf.update(y[:, 0])

x_estime[:, 0] = kf.x.ravel()
P_estime[:, :, 0] = kf.P

for k in range(N - 1):
    # 1. Prédire l'état suivant avec la commande u[k]
    kf.predict(u=np.array([[u[k]]]))

    # 2. Corriger avec la mesure à l'instant suivant
    kf.update(y[:, k + 1])

    # 3. Sauvegarder l'estimation et son incertitude
    x_estime[:, k + 1] = kf.x.ravel()
    P_estime[:, :, k + 1] = kf.P

t = np.arange(N) * p.Te

plt.figure()
plt.plot(t, x[0], label="Angle réel")
plt.plot(t, x_estime[0], "--", label="Angle estimé")
plt.xlabel("Temps (s)")
plt.ylabel("Angle (rad)")
plt.legend()
plt.grid()
plt.show()


plt.figure()
plt.plot(t, x[1], label="Vitesse réelle")
plt.plot(t, x_estime[1], "--", label="Vitesse estimée")
plt.xlabel("Temps (s)")
plt.ylabel("Vitesse (rad/s)")
plt.legend()
plt.grid()
plt.show()

#d.2) Filtre de Kalman stationnaire
