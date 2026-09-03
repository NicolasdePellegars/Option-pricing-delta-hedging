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

def calculate_greeks(S, K, T, r, sigma, option_type):
    d1, d2 = compute_d1_d2(S, K, T, r, sigma)

    # Delta
    if option_type() == "call":
        delta = norm.cdf(d1)
    elif option_type() == "put":
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError("Option type must be 'Call' or 'Put'.")

    # Gamma
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    # Vega
    vega = S * norm.pdf(d1) * np.sqrt(T)

    # Theta
    if option_type() == "call":
        theta = (
            -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
            - r * K * np.exp(-r * T) * norm.cdf(d2)
        )
    else:
        theta = (
            -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
            + r * K * np.exp(-r * T) * norm.cdf(-d2)
        )

    # Rho
    if option_type() == "call":
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    return delta, gamma, vega, theta, rho


def trajectoire(S0, K, T, r, sigma, N):
    dt = T / N

    S = np.zeros(N) #tableau qui contient la valo simulée de l'optio 
    S[0] = S0

    for i in range(1, N):
        Z = np.random.standard_normal()
        S[i] = S[i - 1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)

    return S

def delta_hedging_call(S0, K, T, r, sigma, N):
    dt = T / N

    #Simulation d'une trajectoire du sous jacent 
    S = trajectoire(S0, K, T, r, sigma, N)

    #Prix initial de l'option
    option_price = BS_analytical(S0, K, T, r, sigma, "call")

    #Delta initial 
    d1,d2 = compute_d1_d2(S0, K, T, r, sigma)
    delta = norm.cdf(d1)
    
    cash = option_price - delta * S0  # Initial cash position

    for i in range(N):
        #Capitalisation du cash au taux sans risque 
        cash = cash * np.exp(r * dt)  # Update cash position with interest

        #Temps restant avant maturité 
        T_remaining = T - i * dt

        #Prix courant du sous jacent 
        St = S[i]

        #Nouveau delta 
        d1,d2 = compute_d1_d2(St, K, T_remaining, r, sigma)
        delta_new = norm.cdf(d1)

        #Quantité d'action a short / long 
        delta_change = delta_new - delta

        #Achat / Vente financé par le compte cash 
        cash = cash - delta_change * St

        #Maj Delta
        # delta = delta_new
        # 
        # 

    return S, delta_values



def delta_hedging_call(S0, K, T, r, sigma, n_steps):
    dt = T / n_steps

    # 1 Simulation d'une trajectoire du sous-jacent
    stock_path = simulate_stock_path(S0, T, r, sigma, n_steps)

    # 2 Prix initial de l'option
    option_price = BS_analytical(S0, K, T, r, sigma, "call")

    # 3. Delta initial
    d1, d2 = calculate_d1_d2(S0, K, T, r, sigma)
    delta = norm.cdf(d1)

    # Nous sommes short d'un call :
    # on reçoit le prix de l'option et on achète delta actions.
    cash = option_price - delta * S0

    # Pour stocker l'évolution du hedge
    delta_path = np.zeros(n_steps + 1)
    cash_path = np.zeros(n_steps + 1)

    delta_path[0] = delta
    cash_path[0] = cash

    # 4. Rebalancement dynamique
    for i in range(1, n_steps):

        # Le cash accumule les intérêts
        cash = cash * np.exp(r * dt)

        # Temps restant avant maturité
        remaining_time = T - i * dt

        # Prix courant du sous-jacent
        S_t = stock_path[i]

        # Nouveau delta
        d1, d2 = calculate_d1_d2(
            S_t,
            K,
            remaining_time,
            r,
            sigma
        )

        new_delta = norm.cdf(d1)

        # Quantité d'actions à acheter ou vendre
        delta_change = new_delta - delta

        # Achat / vente financé par le compte cash
        cash = cash - delta_change * S_t

        # Mise à jour du delta
        delta = new_delta

        delta_path[i] = delta
        cash_path[i] = cash

    # 5. Dernière capitalisation jusqu'à maturité
    cash = cash * np.exp(r * dt)

    S_T = stock_path[-1]

    # Valeur finale du portefeuille de couverture
    hedge_portfolio = delta * S_T + cash

    # Payoff du call vendu
    payoff = max(S_T - K, 0)

    # Erreur de couverture
    hedging_error = hedge_portfolio - payoff

    delta_path[-1] = delta
    cash_path[-1] = cash

    return stock_path, delta_path, cash_path, hedge_portfolio, payoff, hedging_error