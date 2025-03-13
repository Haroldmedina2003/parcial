from flask import Flask, jsonify
from neo4j import GraphDatabase
import psycopg2
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Configuración de Neo4j
neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"
neo4j_password = "password"

# Configuración de PostgreSQL
postgres_host = "postgres"
postgres_db = "etl_db"
postgres_user = "user"
postgres_password = "password"

# Conectar a Neo4j
def get_neo4j_data():
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        result = session.run("MATCH (p:Pelicula) RETURN p")
        data = [dict(record["p"]) for record in result]
    driver.close()
    return data

# Transformar datos
def transform_data(data):
    transformed_data = []
    for item in data:
        # 1. Formatear nombre
        nombre_formateado = item["nombre"].lower().replace(" ", "-")
        
        # 2. Categorizar calificación
        calificacion = float(item["calificacion"])
        if calificacion <= 5:
            categoria_calificacion = "Mala"
        elif 5.1 <= calificacion <= 7:
            categoria_calificacion = "Regular"
        else:
            categoria_calificacion = "Buena"
        
        # 3. Clasificar década
        año_lanzamiento = int(item["año_lanzamiento"])
        decada = f"{str(año_lanzamiento)[:3]}0s"
        
        # 4. Calcular puntuación ajustada
        puntuacion_ajustada = (calificacion * 2) - (2025 - año_lanzamiento) / 10
        
        transformed_data.append({
            "id": item["id"],
            "nombre_formateado": nombre_formateado,
            "categoria_calificacion": categoria_calificacion,
            "decada": decada,
            "puntuacion_ajustada": puntuacion_ajustada,
            "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d")
        })
    return transformed_data

# Cargar datos en PostgreSQL
def load_data(data):
    conn = psycopg2.connect(
        host=postgres_host,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password
    )
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS etl_data (
            id VARCHAR(255),
            nombre_formateado VARCHAR(255),
            categoria_calificacion VARCHAR(50),
            decada VARCHAR(20),
            puntuacion_ajustada FLOAT,
            fecha_procesamiento DATE
        )
    """)
    
    # Insertar datos
    for item in data:
        cursor.execute("""
            INSERT INTO etl_data (id, nombre_formateado, categoria_calificacion, decada, puntuacion_ajustada, fecha_procesamiento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            item["id"],
            item["nombre_formateado"],
            item["categoria_calificacion"],
            item["decada"],
            item["puntuacion_ajustada"],
            item["fecha_procesamiento"]
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

# Exportar a CSV
def export_to_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("/app/csv/recap.csv", index=False)

# Ruta de la API
@app.route("/api/extract", methods=["GET"])
def extract():
    data = get_neo4j_data()
    transformed_data = transform_data(data)
    load_data(transformed_data)
    export_to_csv(transformed_data)
    return jsonify(transformed_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
