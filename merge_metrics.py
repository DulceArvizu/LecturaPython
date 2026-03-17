import sys
import pandas as pd


def merge_session_data(unity_path, emotions_path, eyetracking_path, output_path):
    try:
        df_unity = pd.read_csv(unity_path)
        df_emo = pd.read_csv(emotions_path)
        df_eye = pd.read_csv(eyetracking_path)

        # Unir por timestamp
        df_final = pd.merge(df_unity, df_emo, on="timestamp", how="outer")
        df_final = pd.merge(df_final, df_eye, on="timestamp", how="outer")

        # Unificar nombre de contador
        if "contador_x" in df_final.columns:
            df_final = df_final.rename(columns={"contador_x": "contador_segundos"})

        # Eliminar contadores duplicados
        columnas_basura = [
            col for col in df_final.columns
            if col.startswith("contador_") and col != "contador_segundos"
        ]
        df_final = df_final.drop(columns=columnas_basura, errors="ignore")

        # Eliminar columna contador si existe
        if "contador" in df_final.columns:
            df_final = df_final.drop(columns=["contador"])

        # Orden temporal
        df_final = df_final.sort_values("timestamp")

        # Rellenar vacíos
        df_final = df_final.fillna("Sin registro")

        # Guardar
        df_final.to_csv(output_path, index=False, encoding="utf-8")
        print(f"[MergeMetrics] ¡Éxito! CSV maestro generado en: {output_path}")

    except Exception as e:
        print(f"[MergeMetrics] Error crítico al unir los CSV: {e}")


# ==============================
# EJECUCIÓN DESDE TERMINAL
# ==============================
if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Uso correcto:")
        print("python merge_metrics.py <unity.csv> <emociones.csv> <eyetracking.csv> <salida.csv>")
        sys.exit(1)

    merge_session_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])