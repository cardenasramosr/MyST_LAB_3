
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
