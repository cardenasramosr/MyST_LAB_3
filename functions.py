
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio 3. Finanzas Conductuales                                                       -- #
# -- script: functions.py : script de python con las funciones generales                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Configuraciones
import pandas as pd 
import numpy as np
import yfinance as yf
import datetime as dt

def f_columnas_tiempos(param_data):
    """
    f_columnas_tiempos transforma las columnas de opentime y closetime a formato datetime.
    
    """
    
    param_data["opentime"] = pd.to_datetime(param_data["opentime"])
    param_data["closetime"] = pd.to_datetime(param_data["closetime"])
    param_data["tiempo"] = list(map(lambda i : (param_data.iloc[i, 8] - param_data.iloc[i, 0]).seconds, 
                                    range(len(param_data))))
    
    return param_data

def f_pip_size(param_ins):
    """
    f_pip_size devuelve el multiplicador de pips para el instrumento ingresado.
    
    """
    
    pips = pd.read_csv("files/instruments_pips.csv")
    
    if param_ins not in ["NAT.GAS", "AMZN.O", "TSLA.O", "GOOGL.O", "KO.N", "BRKb.N", "WMT.N"]:
        param_ins = param_ins[0:3] + "/" + param_ins[3:]
        
        return 1 / pips[pips["Description"] == param_ins]["TickSize"].values[0]
        
    else:
        return 100
    
def f_columnas_pips(param_data):
    """
    f_columnas_pips devuelve la cantidad de pips ganados/perdidos por cada operación, su acumulado y el beneficio en unidades monetarias acumulado.
    
    """
    
    param_data["pips"] = 0
    
    for i in range(len(param_data)):
        
        if param_data.loc[i, "type"] == "buy":
            param_data.loc[i, "pips"] = (param_data.loc[i, "closeprice"] - 
                                         param_data.loc[i, "openprice"]) * f_pip_size(param_data.loc[i, "item"])
            
        else:
            param_data.loc[i, "pips"] = (-param_data.loc[i, "closeprice"] + 
                                         param_data.loc[i, "openprice"]) * f_pip_size(param_data.loc[i, "item"])
            
    param_data["pips_acm"] = param_data["pips"].cumsum()
    param_data["profit_acm"] = param_data["profit"].cumsum()
    
    return param_data

def f_estadisticas_ba(param_data):
    """
    f_estadisticas_ba retorna algunas estadísticas de las operaciones de trading.
    
    """

    dic_estadisticas_ba = {}
    # Tabla
    tabla = pd.DataFrame(index = ["Ops totales", "Ganadoras", "Ganadoras_c", "Ganadoras_v", 
                              "Perdedoras", "Perdedoras_c", "Perdedoras_v", "Mediana (Profit)",
                              "Mediana (Pips)", "r_efectividad", "r_proporcion", "r_efectividad_c", "r_efectividad_v"])
    tabla.index.name = "Medida"
    tabla["Valor"] = 0
    tabla["Descripcion"] = ["Operaciones totales", "Operaciones ganadoras", "Operaciones ganadoras de compra",
                        "Operaciones ganadoras de venta", "Operaciones perdedoras", "Operaciones perdedoras de compra",
                        "Operaciones perdedoras de venta", "Mediana de profit de operaciones", 
                        "Mediana de pips de operaciones", "Ganadoras totales / Operaciones totales",
                        "Ganadoras totales / Perdedoras totales", "Ganadoras compra / Operaciones totales", 
                        "Ganadoras venta / Operaciones totales"]
    
    tabla.loc["Ops totales", "Valor"] = len(param_data)
    tabla.loc["Ganadoras", "Valor"] = len(param_data[param_data["profit"] > 0])
    tabla.loc["Ganadoras_c", "Valor"] = len(param_data[(param_data["profit"] > 0) & (param_data["type"] == "buy")])
    tabla.loc["Ganadoras_v", "Valor"] = len(param_data[(param_data["profit"] > 0) & (param_data["type"] == "sell")])
    tabla.loc["Perdedoras", "Valor"] = len(param_data[param_data["profit"] <= 0])
    tabla.loc["Perdedoras_c", "Valor"] = len(param_data[(param_data["profit"] <= 0) & (param_data["type"] == "buy")])
    tabla.loc["Perdedoras_v", "Valor"] = len(param_data[(param_data["profit"] <= 0) & (param_data["type"] == "sell")])
    tabla.loc["Mediana (Profit)", "Valor"] = np.median(param_data["profit"])
    tabla.loc["Mediana (Pips)", "Valor"] = np.median(param_data["pips"])
    tabla.loc["r_efectividad", "Valor"] = tabla.loc["Ganadoras", "Valor"] / tabla.loc["Ops totales", "Valor"]
    tabla.loc["r_proporcion", "Valor"] = tabla.loc["Ganadoras", "Valor"] / tabla.loc["Perdedoras", "Valor"]
    tabla.loc["r_efectividad_c", "Valor"] =  tabla.loc["Ganadoras_c", "Valor"] /  tabla.loc["Ops totales", "Valor"]
    tabla.loc["r_efectividad_v", "Valor"] = tabla.loc["Ganadoras_v", "Valor"] /  tabla.loc["Ops totales", "Valor"]
    
    # Ranking
    rank = pd.DataFrame(index = set(param_data["item"]), columns = ["r_efectividad", "rank"])
    rank.index.name = "symbol"
    for i in list(set(param_data["item"])):
        rank.loc[i, "r_efectividad"] = len(param_data[(param_data["item"] == i) & 
                                                      (param_data["profit"] > 0)]) / len(param_data[param_data["item"] == i])
    
    rank.sort_values(["r_efectividad"], ascending = False, inplace = True)
    rank["rank"] = np.arange(1, len(rank) + 1)
    
    dic_estadisticas_ba["df_1_tabla"] = tabla
    dic_estadisticas_ba["df_2_ranking"] = rank
    
    return dic_estadisticas_ba

def f_evolucion_capital(param_data):
    """
    f_evolucion_capital retorna el desempeño de la cuenta de trading durante los días operados.
    
    """
    
    param_data.sort_values(["closetime"], ascending = True, inplace = True)
    param_data.reset_index(drop = True, inplace = True)
    
    beneficios = param_data.groupby([param_data["closetime"].dt.date])["profit"].sum()
    evolucion_capital = pd.DataFrame(index = beneficios.index)
    evolucion_capital.index.name = "timestamp"
    evolucion_capital["profit_d"] = beneficios.values
    evolucion_capital["profit_acm_d"] = 100000 + evolucion_capital["profit_d"].cumsum()
    
    return evolucion_capital
    
def f_estadisticas_mad(param_data):
    """
    f_estadisticas_mad retorna métricas de atribución al desempeño de la cuenta de trading durante los días operados.
    
    """
    
    # Ratio Sharpe
    mad = pd.DataFrame(columns = ["Métrica", "Valor", "Descripción"])
    
    retornos = np.log(param_data["profit_acm_d"] / param_data["profit_acm_d"].shift(1)).dropna()
    mad.loc[0, "Métrica"] = "sharpe_original"
    mad.loc[0, "Valor"] = (retornos.mean() * 252 - 0.05) / (retornos.std() * np.sqrt(252))
    mad.loc[0, "Descripción"] = "Sharpe Ratio Fórmula Original"
    
    benchmark = yf.download("^GSPC", progress = False, start = param_data.index[0], 
                            end = param_data.index[-1] + dt.timedelta(1))["Adj Close"]
    retornos_benchmark = np.log(benchmark / benchmark.shift(1)).dropna()
    spread_retornos = retornos - retornos_benchmark
    mad.loc[1, "Métrica"] = "sharpe_actualizado"
    mad.loc[1, "Valor"] = ((retornos.mean() - retornos_benchmark.mean()) * 252) / (spread_retornos.std() * np.sqrt(252))
    mad.loc[1, "Descripción"] = "Sharpe Ratio Fórmula Ajustada"
    
    # Drawdown
    dd_f = np.argmax(np.maximum.accumulate(param_data["profit_acm_d"]) - param_data["profit_acm_d"]) 
    dd_i = np.argmax(param_data["profit_acm_d"][:dd_f]) 
    
    mad.loc[2, "Métrica"] = "drawdown_capi"
    mad.loc[2, "Valor"] = param_data.index[dd_i]
    mad.loc[2, "Descripción"] = "Fecha inicial del DrawDown de Capital"
    
    mad.loc[3, "Métrica"] = "drawdown_capi"
    mad.loc[3, "Valor"] = param_data.index[dd_f]
    mad.loc[3, "Descripción"] = "Fecha final del DrawDown de Capital"
    
    mad.loc[4, "Métrica"] = "drawdown_capi"
    mad.loc[4, "Valor"] = param_data.loc[param_data.index[dd_f], "profit_acm_d"] - param_data.loc[param_data.index[dd_i], 
                                                                                                  "profit_acm_d"]
    mad.loc[4, "Descripción"] = "Máxima pérdida flotante registrada"
    
    # Drawup
    du_f = np.argmax(np.maximum.accumulate(param_data["profit_acm_d"]) + param_data["profit_acm_d"]) 
    du_i = np.argmin(param_data["profit_acm_d"][:du_f]) 
    
    mad.loc[5, "Métrica"] = "drawup_capi"
    mad.loc[5, "Valor"] = param_data.index[du_i]
    mad.loc[5, "Descripción"] = "Fecha inicial del DrawUp de Capital"
    
    mad.loc[6, "Métrica"] = "drawup_capi"
    mad.loc[6, "Valor"] = param_data.index[du_f]
    mad.loc[6, "Descripción"] = "Fecha final del DrawUp de Capital"
    
    mad.loc[7, "Métrica"] = "drawup_capi"
    mad.loc[7, "Valor"] = param_data.loc[param_data.index[du_f], "profit_acm_d"] - param_data.loc[param_data.index[du_i], 
                                                                                                  "profit_acm_d"]
    mad.loc[7, "Descripción"] = "Máxima ganancia flotante registrada"
    
    return mad
    
    