import numpy as np
import matplotlib.pyplot as plt

import parametres as p


x1=[p.theta0,p.omega0] #l'initialisation du vecteur d'état

#on remplit u comme créneau de période delta et d'amplitude Acc avec la fonction entrée

def entree(D, Acc, Delta, Te):
    t = np.arange(0, D, Te)
    # Créneau centré d'amplitude crête à crête Acc
    # On utilise np.sin pour faire un signal carré alternant entre -Acc/2 et Acc/2
    u = (Acc / 2) * np.sign(np.sin(2 * np.pi * t / Delta))
    return u


#y#matrice colonne de même dimension que u contenant l'évolution de la mesure yn
#x#matrice à deux colonnes contenant l'évolution du vecteur d'état x=[theta,omega] au cours du temps

def simule(u, G, T, Te, pas, x1):
    u=np.asarray(u).reshape(-1) # on s'assure que u est un vecteur ligne

    N = len(u)
    x = np.zeros((2, N))
    y = np.zeros((1, N))
    e = np.zeros((1, N))  # erreur de mesure du codeur incrémental
    
    x[:, 0] = x1
    
    # Condition initiale de la mesure (quantification de theta_1)
    y[0, 0] = np.round(x[0, 0]/pas)*pas

    #discrétisation exacte à entrée constante sur laz période d'échantillonnage Te du système continu
    a = np.exp(-Te/T)
    F = np.array([[1., T * (1 - a)],[0., a]])
    Bd = np.array([G * (Te - T * (1 - a)),G * (1 - a)])
    for k in range(N - 1):
        # Évolution de l'état discret
        x[:,k+1]= F@ x[:,k]+Bd*u[k]
        
        # Mesure fournie par le codeur 9 bits (quantification de la position)
        y[0,k+1]=np.round(x[0,k+1]/pas)*pas
        e[0,k+1]=np.abs(y[0,k+1]-x[0,k+1]) #erreur de mesure du codeur incrémental
        
    return x, y, e


u = entree(p.D, p.Acc, p.delta, p.Te)
x, y, e = simule(u, p.G, p.T, p.Te, p.pas, x1)

# --- Affichage des résultats ---
t_vect = np.arange(0, p.D, p.Te)

plt.figure(figsize=(10, 8))

plt.subplot(3, 1, 1)
plt.step(t_vect, u, color='orange')
plt.title("Tension d'alimentation u(t) (Créneau)")
plt.ylabel("U (V)")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t_vect, x[0, :], label="Theta réel", color='blue')
plt.step(t_vect, y[0, :], where='post', label="Mesure codeur (y)", color='red', linestyle='--', alpha=0.7)
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

plt.show()

plt.figure(figsize=(10, 4))
plt.plot(t_vect, e[0, :], color='purple')
plt.title("Erreur de mesure du codeur incrémental")
plt.ylabel("Erreur (rad)")
plt.xlabel("Temps (s)")
plt.grid(True)
plt.show()