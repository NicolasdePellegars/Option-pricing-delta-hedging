import numpy as np
import math
from scipy.stats import norm 

# input : S0, K(strike), T(Maturité), r(taux sans risque), sigma(vol), Call/Put)
S0 = float(input("Inital stock price (S0): "))
K = float(input("Strike price (K): "))
T = float(input("Maturity in years (T): "))
r = float(input("Risk-free interest rate (r): "))
sigma = float(input("Volatility (sigma): "))
option_type = input("Option type (Call/Put): ").lower()

def payoff(St, K, option_type):
    if option_type == 'call':
        return np.maximum(St - K, 0)
    elif option_type == 'put':
        return np.maximum(K - St, 0)
    else:
        return ValueError("Invalid option type. Please choose 'Call' or 'Put'.")


# Black-Scholes : dSt​ = μSt​dt + σSt​dWt​
# St = Prix instant t  		  μ : Rendement espéré 
# σ	= Volatilité			  dWt : Mouvement brownien


def compute_d1_d2(S0, K, T, r, sigma):
    #N(d1) = Delta du Call (avec N cdf de la loi normale)
    d1 = np.log(S0 / K) + (r + 0.5 * sigma**2) * T / (sigma * np.sqrt(T))

    #N(d2) est la proba risque neutre que l'option dépasse le strike
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

d1,d2 = compute_d1_d2(S0, K, T, r, sigma)

# Pricing par BS analystique 
def BS_analytical(S0,K,T,r,sigma,option_type):

    #d1,d2 = compute_d1_d2(S0, K, T, r, sigma)

    if option_type == "call":
        price = S0 * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

    elif option_type == "put":
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)

    return price

def Monte_Carlo (S0, K, T, r, sigma, option_type, N=10000000):

    Z = np.random.standard_normal(N)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z) #Formule donnée par BS

    # Calculer le payoff pour chaque chemin simulé
    payoffs = payoff(ST, K, option_type)

    # Actualiser les payoffs à la valeur présente
    discounted_payoffs = np.exp(-r * T) * payoffs

    # Calculer le prix de l'option comme la moyenne des payoffs actualisés
    price = np.mean(discounted_payoffs)

    return price

bs_price = BS_analytical(S0, K, T, r, sigma, option_type)
mc_price = Monte_Carlo(S0, K, T, r, sigma, option_type)

print("Black-Scholes Price: ", bs_price)
print("Monte Carlo Price: ", mc_price)


#Calcul des greeks à partir de la formule BS analytique 

#Delta 
delta = norm.cdf(d1) if option_type == "call" else -norm.cdf(-d1)
