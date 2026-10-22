import numpy as np
import matplotlib.pyplot as plt


L=512 #2^9, nombre de points du codeur incrémental
p=9 #nombre de bits du codeur incrémental
delta =100e-3#période du créneau de la tension d'alimentation
Acc=0.1#tension crête à crête du signal d'alimentation
Te=1e-3 #période d'échantillonnage du créneau
G=50 #gain du moteur
T=20e-3 #constante de temps du moteur
D = 500e-3          # durée totale de la simulation en secondes

theta=0
omega=0

x1=[theta,omega] #l'initialisation du vecteur d'état
#yn #mesure fournie par le codeur quantifiant la position angulaire réelle thetan

#on remplit u comme créneau de période delta et d'amplitude Acc avec la fonction entrée

def entree(D, Acc, Delta, Te):
    t = np.arange(0, D, Te)
    # Créneau centré d'amplitude crête à crête Acc
    # On utilise np.sin pour faire un signal carré alternant entre -Acc/2 et Acc/2
    u = (Acc / 2) * np.sign(np.sin(2 * np.pi * t / Delta))
    return u


#y#matrice colonne de même dimension que u contenant l'évolution de la mesure yn
#x#matrice à deux colonnes contenant l'évolution du vecteur d'état x=[theta,omega] au cours du temps


def simule(u, G, T, Te, L, x1):
    N = len(u)
    x = np.zeros((2, N))
    y = np.zeros((1, N))
    
    x[:, 0] = x1
    
    # Condition initiale de la mesure (quantification de theta_1)
    y[0, 0] = np.round(x[0, 0] * L / (2 * np.pi)) * (2 * np.pi) / L
    
    # Matrices continues du système
    A = np.array([[0, 1], [0, -1 / T]])
    B = np.array([[0], [G / T]])
    
    # Discrétisation par la méthode d'Euler (Ad = I + Te*A, Bd = Te*B)
    Ad = np.eye(2) + Te * A
    Bd = np.array([0, G / T])    

    for k in range(N - 1):
        # Évolution de l'état discret
        x[:, k + 1] = Ad @ x[:, k] + Bd * u[k]
        
        # Mesure fournie par le codeur 9 bits (quantification de la position)
        theta_reelle = x[0, k + 1]
        # Le codeur découpe un tour (2*pi radians) en L = 512 parts
        y[0, k + 1] = np.round(theta_reelle * L / (2 * np.pi)) * (2 * np.pi) / L
        
    return x, y


u = entree(D, Acc, delta, Te)
x, y = simule(u, G, T, Te, L, x1)

# --- 5. Affichage des résultats ---
t_vect = np.arange(0, D, Te)

plt.figure(figsize=(10, 8))

plt.subplot(3, 1, 1)
plt.plot(t_vect, u, color='orange')
plt.title("Tension d'alimentation u(t) (Créneau)")
plt.ylabel("U (V)")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t_vect, x[0, :], label="Theta réel", color='blue')
plt.plot(t_vect, y[0, :], label="Mesure codeur (y)", color='red', linestyle='--', alpha=0.7)
plt.title("Position angulaire du moteur et de la mesure")
plt.ylabel("Theta (rad)")
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(t_vect, x[1, :], color='green')
plt.title("Vitesse angulaire du moteur (Omega)")
plt.ylabel("Omega (rad/s)")
plt.xlabel("Temps (s)")
plt.grid(True)

plt.tight_layout()
plt.show()