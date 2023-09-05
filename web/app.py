import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, url_for
import pickle
from sklearn import svm
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import plotly.express as px


# Path del modelo preentrenado
MODEL_PATH = '/mount/src/tpinicial/web/models/kmeans_model.pkl'


# Paths de datasets
data = pd.read_csv('/mount/src/tpinicial/data.csv')
data3d = pd.read_csv('/mount/src/tpinicial/data3d.csv')
data_ref = pd.read_csv('/mount/src/tpinicial/data_ref.csv')


# Se recibe los datos del usuario y el modelo, devuelve la predicción
def model_prediction(x_in, model):
    x = np.asarray(x_in).reshape(1, -1)
    preds = model.predict(x)
    return preds


# Histograma por clusters de riesgo de suicidio
def hist_suic_clusters(data_ref):
    colors = {
        'Riesgo bajo': '#feca8d',
        'Riesgo medio': '#f1605d',
        'Riesgo alto': '#9e2f7f'
    }
    unique_clusters = np.unique(data_ref['Cluster'])
    for cluster in unique_clusters:
        cluster_data = data_ref[data_ref['Cluster'] == cluster]
        if cluster == 'Riesgo bajo':
            bin_limits = [0, 25]
        elif cluster == 'Riesgo medio':
            bin_limits = [25, 50]
        elif cluster == 'Riesgo alto':
            bin_limits = [50, 100]
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(cluster_data['SUIC RISK'], bins=20, range=bin_limits, color=colors[cluster], alpha=0.7)
        ax.set_title(f'Distribución de riesgo total de suicidio en Cluster {cluster}')
        ax.set_xlabel('Riesgo total de suicidio')
        ax.set_ylabel('Cantidad de casos')
        ax.grid(True)
        ax.set_xlim(bin_limits)
        # Mostrar la figura en Streamlit
        st.write(f'')
        st.pyplot(fig)
        

# Histograma de provincias para cada cluster
def hist_suic_clusters_regions(data_ref):
    unique_clusters = np.unique(data_ref['Cluster'])
    for cluster in unique_clusters:
        cluster_data = data_ref[data_ref['Cluster'] == cluster]
        province_counts = cluster_data['REGION'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        province_counts.plot(kind='bar', color='#5a167e', alpha=0.7, ax=ax)
        plt.title(f'Distribución de regiones y provincias en Cluster {cluster}')
        plt.xlabel('Region-Provincia')
        plt.ylabel('Cantidad de casos')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True)
        # Mostrar la figura en Streamlit
        st.write(f'')
        st.pyplot(fig)


# Scatter plot de clusters y tsne
def scatter_plot_clusters(data_ref, kmeans, cluster_names):
    colors = ['#f1605d', '#feca8d', '#9e2f7f']
    plt.figure(figsize=(12, 8))
    unique_clusters = np.unique(kmeans.labels_)
    for i, cluster in enumerate(unique_clusters):
        cluster_data = data_ref[data_ref['Cluster'] == cluster]
        cluster_name = cluster_names.get(cluster, f'Cluster {cluster}')
        # Asignar color a cada cluster
        color = colors[i % len(colors)]
        plt.scatter(cluster_data['tsne_x'], cluster_data['tsne_y'],
                    label=cluster_name, alpha=0.7, s=50, c=color)
    plt.xlabel('t-SNE x')
    plt.ylabel('t-SNE y')
    st.pyplot(plt)


def scatter_plot_clusters_3d(data_ref, cluster_names):
    custom_palette = {
        'Riesgo bajo': '#feca8d',
        'Riesgo medio': '#f1605d',
        'Riesgo alto': '#9e2f7f'
    }
    data_ref['Riesgo'] = data_ref['Cluster'].map(cluster_names)
    fig = px.scatter_3d(data_ref, x='tsne_x', y='tsne_y', z='tsne_z', color='Riesgo',
                         color_discrete_map=custom_palette, opacity=0.7)
    fig.update_layout(scene=dict(xaxis_title='t-SNE x', yaxis_title='t-SNE y', zaxis_title='t-SNE z'), 
                      paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor="rgb(0,0,0,0)", margin=dict(r=100))
    st.plotly_chart(fig)


def main():
    model = ''
    # Se carga el modelo
    if model == '':
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)


    cluster_names_for_pred = {
        0: 'Riesgo medio',
        1: 'Riesgo bajo',
        2: 'Riesgo alto',
    }
    

    # Título
    html_temp = """
    <h1 text-align:center;">SISTEMA DE CLASIFICACION DE RIESGO DE SUICIDIO </h1>
    </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)


    # Lecctura de datos
    N = st.text_input("Valor de riesgo (0 a 100)")
    P = st.text_input("Valor del promedio de riesgo (0 a 100)")

    # El botón clasificar se usa para iniciar el procesamiento
    if st.button("Clasificar"):
        if not N:
            st.error("El valor de riesgo es obligatorio")
        elif not P:
            st.error("El valor del promedio de riesgo es obligatorio")
        else:
            N = float(N)
            P = float(P)
        
            if N < 0 or N > 100:
                st.error("El valor de riesgo debe estar entre 0 y 100")
            elif P < 0 or P > 100:
                st.error("El valor del promedio de riesgo debe estar entre 0 y 100")
            else:

    # Verificar si N es válido
    #if N:
     #   N = float(N)
      #  if N < 0 or N > 100:
       #     st.error("El valor de riesgo debe estar entre 0 y 100")
    # Verificar si P es válido
    #if P:
     #   P = float(P)
      #  if P < 0 or P > 100:
       #     st.error("El valor del promedio de riesgo debe estar entre 0 y 100")


    # El botón clasificar se usa para iniciar el procesamiento
    # if st.button("Clasificar"):
                x_in = [np.float_(N),
                        np.float_(P),
                        ]
                predictS = model_prediction(x_in, model)  # Supongamos que predictS es 0, 1 o 2
                # Obtener el nombre del cluster correspondiente
                predicted_cluster = cluster_names_for_pred.get(predictS[0], 'Riesgo Desconocido')
                # Mostrar el resultado en Streamlit
                st.success(f'El grupo de riesgo al que pertenecen estos valores es: {predicted_cluster}')


                with st.expander("Termómetro de riesgo"):
                    # Define un diccionario de mapeo de valores de predicción a rutas de imágenes
                    imagen_por_prediccion = {
                        0: "/mount/src/tpinicial/web/assets/thermcluster1.png",
                        1: "/mount/src/tpinicial/web/assets/thermcluster0.png",
                        2: "/mount/src/tpinicial/web/assets/thermcluster2.png",
                    }

                    cluster = predictS[0]

                    if cluster in imagen_por_prediccion:
                        # Obtiene la ruta de la imagen correspondiente
                        ruta_imagen = imagen_por_prediccion[cluster]
                        # Muestra la imagen en Streamlit
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.write(' ')

                        with col2:
                            st.image(ruta_imagen, use_column_width="True")

                        with col3:
                            st.write(' ')
                        # st.image(ruta_imagen, use_column_width="True")
                    else:
                        st.write("No se encontró una imagen para la predicción.")

                how = """
                <div>
                <h1 text-align:center;">Visualizaciones del modelo entrenado</h1>
                </div>
                <div>
                <p text-align:center;">
                En este apartado se muestran las diferentes visualizaciones logradas luego de entrenar al modelo
                de machine learning y ver como ayudan a entender los resultados con diferentes tipos de gráficos. 
                </p>
                </div>
                """
                st.markdown(how, unsafe_allow_html=True)
            

                with st.expander("Distribución de clusters en 2D"):
                    title_hist_suic_clusters_regions = """
                    <div>
                    <h1 text-align:center;">Distribución de clusters en 2D</h1>
                    </div>
                    <div>
                    <p text-align:center;">
                    Así es como se ve gracias a la reducción de dimensionalidad t-SNE (80 de perplejidad) 
                    la distribución de los 3 clusters con el entrenamiento de K-Means en dos dimensiones.
                    Cada punto en el gráfico se colorea según el clúster al que pertenece, lo que permite 
                    identificar visualmente cómo se agrupan los registros en el espacio bidimensional.
                    El color amarillo nos indica los casos de bajo riesgo, el rosado de riesgo medio y el violeta de riesgo alto.
                    </p>
                    </div>
                    """
                    st.markdown(title_hist_suic_clusters_regions, unsafe_allow_html=True)
                    scatter_plot_clusters(data, model, cluster_names_for_pred)

            
                with st.expander("Distribución de clusters en 3D"):
                    title_hist_suic_clusters_regions = """
                    <div>
                    <h1 text-align:center;">Distribución de clusters en 3D</h1>
                    </div>
                    <div>
                    <p text-align:center;">
                    Así es como se ve gracias a la reducción de dimensionalidad t-SNE (80 de perplejidad) 
                    la distribución de los 3 clusters con el entrenamiento de K-Means en 3 dimensiones.
                    Se respetan los mismos colores que en el de dos dimensiones.
                    </p>
                    </div>
                    """
                    st.markdown(title_hist_suic_clusters_regions, unsafe_allow_html=True)
                    scatter_plot_clusters_3d(data3d, cluster_names_for_pred)


                with st.expander("Histograma cantidad de casos según riesgo total"):
                    title_hist_suic_clusters = """
                    <h1 text-align:center;">Histograma cantidad de casos según riesgo total</h1>
                    </div>
                    """
                    st.markdown(title_hist_suic_clusters, unsafe_allow_html=True)
                    hist_suic_clusters(data_ref)

                
                with st.expander("Histograma cantidad de casos según riesgo por regiones-provincias"):
                    title_hist_suic_clusters_regions = """
                    <h1 text-align:center;">Histograma cantidad de casos según riesgo por regiones-provincias</h1>
                    </div>
                    """
                    st.markdown(title_hist_suic_clusters_regions, unsafe_allow_html=True)
                    hist_suic_clusters_regions(data_ref)

        
if __name__ == '__main__':
    main()