import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def Save_as_csv(db_name):
    conn = sqlite3.connect(f"{db_name}.db")
    query = """
    SELECT
       id,
        title,
        CAST(REPLACE(REPLACE(price, ' р.', ''), ' ', '') AS INTEGER) AS price_int,
        description,
        url
    FROM ads;
    """
    df = pd.read_sql_query(query, conn)
    df.to_csv(f"{db_name}.csv", index=False, encoding="utf-8")
    conn.close()

def Goods_by_price(table, ax=None, bins=8, price_min=0, price_max=100000, KDE=False):
    sql_query = f"""
        SELECT
            id,
            title,
            CAST(REPLACE(price, ' р.', '') AS INTEGER) AS price_int,
            district,
            url
        FROM 
            {table}
        WHERE
            price_int > {price_min} AND price_int < {price_max}
        """
    conn = sqlite3.connect("ads.db")
    df = pd.read_sql_query(sql_query, conn)
    conn.close()

    # Вычисление статистик
    Mo = df["price_int"].mode()
    Me = df["price_int"].median()
    Ex = df["price_int"].mean()

    # Построение гистограммы с KDE
    sns.histplot(data=df, x="price_int", bins=bins, kde=KDE, ax=ax)

    ax.axvline(Ex, color="blue", linestyle="-", label=f"Мат. ожидание = {round(Ex, 2)};", ymax=1)
    
    if not Mo.empty:
        for i in range(len(Mo)):
            mode_value = Mo.iloc[i]
            if pd.notna(mode_value):  
                ax.axvline(mode_value, color="red", linestyle="--", label=f"Мода#{i+1} = {mode_value};")
    
    ax.set_xlabel("Цена, руб")
    ax.set_ylabel("Плотность")
    ax.set_title(f"Плотность товаров \nпо ценовым диапазонам, таблица '{table}'")
    ax.legend()

def Goods_by_district(table, ax, title):
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

    bars = ax.bar(df["district_name"], df["count"])
    ax.set_title(title)
    ax.set_ylabel("Количество")

    # Улучшение подписей
    ax.set_xticklabels(df["district_name"], rotation=30, ha="right", fontsize=9)

def show_fullscreen(fig):
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    plt.show()

if __name__ == "__main__":
    # Увеличиваем размеры графиков для читаемости
    fig, axes = plt.subplots(2, 2, figsize=(16, 10 ))
    
    # Коррекция расстояний между графиками
    plt.subplots_adjust(hspace=0.5, wspace=0.1, top = 0.9, bottom=0.15)

    Goods_by_district("guitars", axes[0][0], "Распределение гитар по районам")
    Goods_by_district("synthesizers", axes[1][0], "Распределение синтезаторов по районам")
    Goods_by_price("guitars", axes[0][1], 12, 200, 4000)
    Goods_by_price("synthesizers", axes[1][1], 12, 200, 4000)
    # Изменение
    show_fullscreen(fig)
    plt.show()
