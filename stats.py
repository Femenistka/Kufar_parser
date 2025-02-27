import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import random
import Buy_Sell 
import numpy as np

def Save_as_png(fig, filename="dashboard.png", folder="graphs"):
    
    if not os.path.exists(folder):  # Проверяем, существует ли папка
        os.makedirs(folder)  # Создаём папку
        print(f"📂 Папка {folder} создана.")

    file_path = os.path.join(folder, filename)
    fig.savefig(file_path, dpi=300, bbox_inches="tight")
    print(f"✅ График сохранён в: {file_path}")

def Show_DIST_of_SYNT(
        buy_array = None,               
        sell_array = None, 
        ax = None,
        folder_name ="graphs", 
        file_name = "Distribution_of_synthesizers",
        save = False,
        bins = 12
):
    table = "synthesizers"
    price_min = 200
    price_max = 800
    KDE = False
    Distribution_of_goods(
        table = table,
        buy = buy_array,
        sell = sell_array,
        bins = bins,
        ax = ax,
        price_min = price_min,
        price_max = price_max,
        KDE = KDE,
        save_file = save,
        folder_name = folder_name,
        file_name = file_name
    )

def Show_DIST_of_PIANO(
        buy_array = None,               
        sell_array = None, 
        ax = None,
        folder_name ="graphs", 
        file_name = "Distribution_of_piano",
        save = False,
        bins = 12
):
    table = "synthesizers_and_piano"
    price_min = 800
    price_max = 2500
    KDE = False
    Distribution_of_goods(
        table = table,
        buy = buy_array,
        sell = sell_array,
        bins = bins,
        ax = ax,
        price_min = price_min,
        price_max = price_max,
        KDE = KDE,
        save_file = save,
        folder_name = folder_name,
        file_name = file_name
    )
    return 0

def Distribution_of_goods(
        table, 
        buy = None,
        sell = None,
        bins = 12,
        ax = None,
        price_min = 0,
        price_max = 100000,
        KDE = False,
        save_file = False,
        folder_name = "graphs",
        file_name = "Distribution_of_synthesizers"
        ):
    sql_query = f"""
    SELECT
    id,
    title,
    CAST(REPLACE(REPLACE(price, ' р.', ''), ' ', '') AS INTEGER) AS price_int, 
    district,
    url
    FROM {table}
    WHERE price_int > {price_min} 
    AND price_int < {price_max}
    """
    conn = sqlite3.connect("ads.db")
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    # Вычисление описательных статистик 
    Mo = df["price_int"].mode()
    Me = df["price_int"].median()
    Ex = df["price_int"].mean()
    # Проверяем является ли данный график единственным
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        standalone = True  
    else:
        standalone = False
    # Построение графика 
    sns.histplot(data=df, x="price_int", bins=bins, kde=KDE, ax=ax)
    # Построение среднего уровня покупки/продажи
    if buy != None :
        buy_mean = np.mean(buy)
        plt.axvline(buy_mean, color = "green", label = f"Средняя цена покупки = {round(buy_mean)}")
    if sell != None :
        sell_mean = np.mean(sell)
        plt.axvline(sell_mean, color = "red", label = f"Средняя цена продажи = {round(sell_mean)}")
    if buy != None and sell != None :
        plt.axvspan(buy_mean, sell_mean, color = "lightgreen", alpha = 0.5, label = "Прибыль/убыток")
    # Добавляем подписи 
    ax.set_xlabel("Цена, руб")
    ax.set_ylabel("Плотность")
    ax.set_title(f"Плотность товаров \nпо ценовым диапазонам, таблица '{table}'")
    ax.legend()
    #Сохраняем график, если передано `save=True`
    if save_file and standalone:  
        Save_as_png(fig, file_name, folder_name)

    #Показываем график только если он одиночный (не часть `dashboard`)
    if standalone: 
        plt.get_current_fig_manager().full_screen_toggle()
        plt.show() 
    return Mo, Me, Ex 

def Goods_by_district(
        table, 
        title=None, 
        save=False, 
        folder_name="graphs", 
        file_name="district_distribution.png"
        ):
    sql_query = f"""
    SELECT
        COUNT(title) AS count,
        TRIM(SUBSTR(district, INSTR(district, 'Минск,') + LENGTH('Минск,'))) AS district_name
    FROM 
        {table}
    WHERE
        district LIKE '%Минск,%' COLLATE NOCASE
    GROUP BY 
        district_name
    ORDER BY 
        district_name ASC;
    """
    conn = sqlite3.connect("ads.db")
    df = pd.read_sql_query(sql_query, conn)
    conn.close()

    # ✅ Создание новой фигуры и оси
    fig, ax = plt.subplots(figsize=(10, 6))

    # ✅ Построение столбчатой диаграммы
    bars = ax.bar(df["district_name"], df["count"])

    # ✅ Добавление заголовка
    if title:
        ax.set_title(title)

    # ✅ Добавление подписей осей
    ax.set_ylabel("Количество")

    # ✅ Улучшение подписей оси X
    ax.set_xticklabels(df["district_name"], rotation=30, ha="right", fontsize=9)

    # ✅ Отображение графика
    plt.get_current_fig_manager().full_screen_toggle()
        # ✅ Сохранение графика с использованием Save_as_png
    if save:
        Save_as_png(plt.gcf(), filename=file_name, folder=folder_name)

    plt.show()
    

if __name__ == "__main__":
    buy = Buy_Sell.Buy_price
    sell = Buy_Sell.Sell_price
    Goods_by_district(table = "synthesizers_and_piano", title = "Распределение фортепиано по районам",save= True, file_name= "piano_by_region" )
    Goods_by_district(table = "synthesizers", title = "Распределение синтезаторов по районам",save= True, file_name= "synth_by_region" )
    # Show_DIST_of_PIANO(save = True)
