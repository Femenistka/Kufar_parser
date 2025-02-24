import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

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

def Goods_by_price(
        table, 
        ax=None,  # Теперь значение по умолчанию корректное
        bins=8, 
        price_min=0, 
        price_max=100000, 
        KDE=False, 
        save=False, 
        folder_name="graphs", 
        file_name="goods_by_price.png"):
    
    sql_query = f"""
        SELECT
            id,
            title,
            CAST(REPLACE(price, ' р.', '') AS INTEGER) AS price_int,
            district,
            url
        FROM {table}
        WHERE price_int > {price_min} AND price_int < {price_max}
    """
    conn = sqlite3.connect("ads.db")
    df = pd.read_sql_query(sql_query, conn)
    conn.close()

    # Вычисление статистик
    Mo = df["price_int"].mode()
    Me = df["price_int"].median()
    Ex = df["price_int"].mean()

    # ✅ Создаём фигуру и ось, если `ax` не передан (для одиночного графика)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        standalone = True  # Флаг для сохранения отдельного графика
    else:
        standalone = False

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

    # ✅ Сохраняем график, если передано `save=True`
    if save and standalone:
        Save_as_png(fig, file_name, folder_name)

    # ✅ Показываем график только если он одиночный (не часть `dashboard`)
    if standalone:
        plt.show()

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

def Save_as_png(fig, filename="dashboard.png", folder="graphs"):
    
    if not os.path.exists(folder):  # Проверяем, существует ли папка
        os.makedirs(folder)  # Создаём папку
        print(f"📂 Папка {folder} создана.")

    file_path = os.path.join(folder, filename)
    fig.savefig(file_path, dpi=300, bbox_inches="tight")
    print(f"✅ График сохранён в: {file_path}")

def Show_dashboard(save=False, filename="dashboard.png"):
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    # Коррекция расстояний между графиками
    plt.subplots_adjust(hspace=0.5, wspace=0.1, top=0.9, bottom=0.15)

    Goods_by_district("guitars", axes[0][0], "Распределение гитар по районам")
    Goods_by_district("synthesizers", axes[1][0], "Распределение синтезаторов по районам")
    Goods_by_price("guitars", axes[0][1], 12, 200, 4000)
    Goods_by_price("synthesizers", axes[1][1], 12, 200, 4000)

    if save:
        Save_as_png(fig, filename)

    show_fullscreen(fig) 
    plt.show()  


if __name__ == "__main__":
    # Show_dashboard(save=True, filename="my_dashboard.png")
    Goods_by_price(
                "guitars", 
                bins = 12, 
                price_min=200, 
                price_max=4000, 
                save = True, 
                file_name= "guitars.png"
                )
    Goods_by_price(
                "synthesizers", 
                bins=12, 
                price_min=200, 
                price_max=4000, 
                save=True, 
                file_name="synthesizers.png"
                )

