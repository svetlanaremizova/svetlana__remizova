# -*- coding: utf-8 -*-
"""Копия блокнота "ВКР(3) Ремизова С.Н.ipynb"

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10PplkHbydSBORWsc-dA5sKN3bluJJOqE
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns


import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.pylab as plt
from matplotlib import pyplot as plt
from matplotlib import pyplot


import pandas_profiling
from pandas import read_csv
from pandas.plotting import scatter_matrix


from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import Normalizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PowerTransformer,MinMaxScaler
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor


from keras.engine.sequential import Sequential
from keras import layers
from keras import models

from scipy.sparse.linalg import svds
from imblearn.over_sampling import SMOTE, ADASYN


from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization, GlobalAveragePooling2D
import tensorflow.keras as keras
import tensorflow as tf
import tensorflow_datasets as tfds
from keras.wrappers.scikit_learn import KerasClassifier


from IPython.display import clear_output


import torch
from torch.autograd import Variable


# %matplotlib inline
# %config InlineBackend.figure_format = 'retina' # для более четкой отрисовки графиков

!pip install matplotlib

!pip install xlrd

import xlrd

df1 = pd.read_excel('/content/X_bp.xlsx')
df1.head(5)

df1.shape

df2 = pd.read_excel('/content/X_nup.xlsx')
df2.head()

df2.shape

df1.profile_report()

df2.profile_report()

df3_merged = pd.merge(df1, df2) 
 df3_merged.head()

df3_merged.shape

df3_merged.dtypes

df3_merged.isna().sum()

df3_merged.profile_report()

df3_merged.drop(['Плотность, кг/м3', 'Количество отвердителя, м.%',	'Содержание эпоксидных групп,%_2',	'Температура вспышки, С_2',	'Поверхностная плотность, г/м2', 'модуль упругости, ГПа','Потребление смолы, г/м2',	'Угол нашивки, град',	'Шаг нашивки', 'Плотность нашивки'], axis=1)

df4 = df3_merged

df4.head()

for col in df4: # посмотрим на распределение числовых переменных
    plt.figure()
    sns.histplot(df4[col])

sns.pairplot(df4)

df4.plot.box(title='Диаграмма "ящик с усами"')
plt.rcParams['figure.figsize']=10,15

sns.boxplot(df4['Модуль упругости при растяжении, ГПа'])

sns.boxplot(df3_merged['Прочность при растяжении, МПа'])

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(df4.corr(), annot=True, fmt='.3f', cmap = 'coolwarm', ax=ax);

fig, ax = plt.subplots(figsize=(18, 14))
sns.heatmap(df4.corr(), annot=True, fmt='.3f', cmap = 'viridis', ax=ax);

#получим среднее и медианное значения данных в колонках
mean_and_50 = df4.describe()
mean_and_50.loc[['mean', '50%']]
#в целом мы видим близкие друг к другу значения

df4.mean()

# Вычисляем коэффициенты ранговой корреляции Кендалла. Статистической зависимости не наблюдаем.?
df4.corr(method = 'kendall')

df4.median()

#Вычисляем коэффициенты корреляции Пирсона. Статистической зависимости не наблюдаем. ?
df4.corr(method ='pearson')

# "Ящики с усами"(боксплоты) 
scaler = MinMaxScaler()
scaler.fit(df4)
plt.figure(figsize = (10, 10))
plt.suptitle('Диаграммы "ящики с усами"', y = 0.9 ,
             fontsize = 20)
plt.boxplot(pd.DataFrame(scaler.transform(df4)), labels = df4.columns,patch_artist = True, meanline = True, vert = False, boxprops = dict(facecolor = 'g', color = 'y'),medianprops = dict(color = 'lime'), whiskerprops = dict(color="g"), capprops = dict(color = "black"), flierprops = dict(color = "y", markeredgecolor = "maroon"))
plt.show()

#Для удаления выбросов существует 2 основных метода - метод 3-х сигм и межквартильных расстояний. Сравним эти 2 метода.
metod_3s = 0
metod_iq = 0
count_iq = [] # Список, куда записывается количество выбросов по каждой колонке датафрейма методом.
count_3s = [] # Список, куда записывается количество выбросов по каждой колонке датафрейма.
for column in df4:
    d = df4.loc[:, [column]]
    # методом 3-х сигм
    zscore = (df4[column] - df4[column].mean()) / df4[column].std()
    d['3s'] = zscore.abs() > 3
    metod_3s += d['3s'].sum()
    count_3s.append(d['3s'].sum())
    print(column,'3s', ': ', d['3s'].sum())

    # методом межквартильных расстояний
    q1 = np.quantile(df4[column], 0.25)
    q3 = np.quantile(df4[column], 0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    d['iq'] = (df4[column] <= lower) | (df4[column] >= upper)
    metod_iq += d['iq'].sum()
    count_iq.append(d['iq'].sum())
    print(column, ': ', d['iq'].sum())
print('Метод 3-х сигм, выбросов:', metod_3s)
print('Метод межквартильных расстояний, выбросов:', metod_iq)

m = df4.copy()
for i in df4.columns:
    m[i] = abs((df4[i] - df4[i].mean()) / df4[i].std())
    print(f"{sum(m[i] > 3)} выбросов в признаке {i}")
print(f' Всего {sum(sum(m.values > 3))} выброса')

for i in df4.columns:
    q75, q25 = np.percentile(df4.loc[:,i], [75,25])
    intr_qr = q75 - q25
    max = q75 + (1.5 * intr_qr)
    min = q25 - (1.5 * intr_qr)
    df4.loc[df4[i] < min, i] = np.nan
    df4.loc[df4[i] > max, i] = np.nan
df4.dropna(inplace = True)

# "Ящики с усами"(боксплоты) 
scaler = MinMaxScaler()
scaler.fit(df4)
plt.figure(figsize = (10, 10))
plt.suptitle('Диаграммы "ящики с усами"', y = 0.9 ,
             fontsize = 20)
plt.boxplot(pd.DataFrame(scaler.transform(df4)), labels = df4.columns,patch_artist = True, meanline = True, vert = False, boxprops = dict(facecolor = 'g', color = 'y'),medianprops = dict(color = 'lime'), whiskerprops = dict(color="g"), capprops = dict(color = "black"), flierprops = dict(color = "y", markeredgecolor = "maroon"))
plt.show()

sns.boxplot(data = df4, orient="h")
plt.show()

df4.shape

df4.describe().T.round(2)

#Визуализация предсказанных значений целевых переменных
#Модели.Прочность и упругость при растяжении 
def predicted_plot(y_test, y_pred, model_name):
  plt.figure(figsize=(15,9))
  plt.title(f'Тестовые и прогнозные значения, Модуль 1: {model_name}')
  plt.plot(y_test.to_numpy()[:,0], label='Тест')
  plt.plot(y_pred[:,0], label='Прогноз')
  plt.legend(loc='best')
  plt.ylabel('н')
  plt.xlabel('Порядок')

  plt.figure(figsize=(15,9))
  plt.title(f'Тестовые и прогнозные значения, Модуль 1: {model_name}')
  plt.plot(y_test.to_numpy()[:,1], label='Тест')
  plt.plot(y_pred[:,1], label='Прогноз')
  plt.legend(loc='best')
  plt.ylabel('н')
  plt.xlabel('Порядок')
def predicted_ns(y_test, y_pred):
  plt.figure(figsize=(15,9))
  plt.title(f'Тест и прогноз, Соотношение М-Н: ')
  plt.plot(y_test.to_numpy(), label='Тест')
  plt.plot(y_pred, label='Прогноз')
  plt.legend(loc='best')
  plt.ylabel('н')
  plt.xlabel('Порядок')

from joblib import dump, load
minmax_y = MinMaxScaler()  
minmax_x = MinMaxScaler()
y_label = ['Модуль упругости при растяжении, ГПа', 'Прочность при растяжении, МПа']
minmax_y.fit(df4[y_label])
minmax_x.fit(df4.drop(y_label, axis = 1))

# Сохраним масштабаторы для x и y
from joblib import dump, load
dump(minmax_y, 'minmax_y.remiz')
dump(minmax_x, 'minmax_x.remiz')

# проверим
minmax_y_l = load('minmax_y.remiz')
x1 = minmax_y_l.inverse_transform(np.array([0.34,0.77]).reshape(1,-1))
x1[0][0], x1[0][1]

y_label = ['Модуль упругости при растяжении, ГПа', 'Прочность при растяжении, МПа']
y = df4[y_label] 
x = df4.drop(y_label, axis = 1)
y.shape,x.shape

model_list = [] # список в котором будем хранить лучшие модели
x_train, x_test, y_train,y_test = train_test_split(x, y , test_size=0.3, random_state=42)

# Итоговый датасет ошибок
loss_df4 = pd.DataFrame(columns=['target','model','MSE','MSE_0','MSE_1','R2','R2_1','R2_1'])

scl = RobustScaler() 
x_train_scl = scl.fit_transform(x_train)
x_test_scl = scl.transform(x_test)

model = ElasticNet(random_state=17) # Сетчатая регрессия
cv = KFold(n_splits=7) # схема для кросс-валидации

cv_score = cross_val_score(model, 
                           x_train, y_train, 
                           scoring='neg_mean_absolute_error', 
                           cv=cv, n_jobs=-1) # прогоняем модель на кросс-валидации
print('MAE на кросс-валидации: %.3f+-%.3f'% (abs(np.mean(cv_score)), np.std(cv_score)))

params = {'alpha': (0.1, 0.5, 1), 
          'l1_ratio': (0.1, 0.5, 0.9)}
model_grid = GridSearchCV(model, 
                          param_grid=params, 
                          scoring='neg_mean_absolute_error', 
                          n_jobs=-1, cv=cv)
model_grid.fit(x_train, y_train)

print('Лучшая модель на кросс-валидации с параметрами {} и MAE {}'.format(model_grid.best_params_, 
                                                                        abs(model_grid.best_score_)))

best_model = model_grid.best_estimator_

best_model.fit(x_train_scl, y_train)
print('MAE на тестовой выборке: %.3f' % mean_absolute_error(y_test, best_model.predict(x_test_scl)))

print('Размер тренировочного датасета: {}\nРазмер тестового датасета:{}'.format(x_train.shape, x_test.shape))

loss_df4

# модуль упругости при растяжении
del loss_df4
loss_df4 =pd.DataFrame([])
model = LinearRegression()
model.fit(x_train,  y_train)
y_pred = model.predict(x_test)


model_name = 'Linear Regression'
def add_loss(loss_df4, model_name,y_test, y_pred):
  MSE = mean_squared_error(y_test, y_pred)
  R2 = r2_score(y_test, y_pred)
  R2_0 = r2_score(y_test[y_label[0]],y_pred[:,0])
  R2_1 = r2_score(y_test[y_label[1]],y_pred[:,1])
  MSE_0 = mean_squared_error(y_test[y_label[0]],y_pred[:,0])
  MSE_1 = mean_squared_error(y_test[y_label[1]],y_pred[:,1])
  # без индекса общая
  #_0 'Модуль упругости при растяжении'
  #_1 'Прочность при растяжении, МПа'
  df4 = pd.DataFrame({'model':model_name,\
                     'target':['Модуль упругости и Прочность'],\
                     'MSE': MSE,\
                     'MSE_0': MSE_0,\
                     'MSE_1': MSE_1,\
                     'R2':R2,\
                     'R2_0': R2_0,\
                     'R2_1': R2_1})

  loss_df4 = pd.concat([loss_df4, df4],ignore_index=True)
  return loss_df4
model_list.append(model)
loss_df4 = add_loss(loss_df4, model_name, y_test, y_pred)
# loss_df4 'Linear Regression'

y_test.shape, y_pred.shape

loss_df4.head()

predicted_plot(y_test, y_pred, model_grid.best_estimator_)

predicted_plot(y_test, y_pred, model_name)

def fit_model(model,model_name,grid,loss_df4, y_test, y_pred): # SVR
  gsc = GridSearchCV(model, grid, n_jobs=-1, cv=10)
  gsc.fit(x_train,  y_train)
  model = gsc.best_estimator_
  model.fit(x_train,  y_train)
  y_pred = model.predict(x_test)
  
  model_list.append(model)
  loss_df = add_loss(loss_df4,model_name, y_test, y_pred)
  predicted_plot(y_test, y_pred,model_name)
  return loss_df4

grid = {
    'estimator__C':np.arange(1.0,5.5,0.5),
    'estimator__epsilon':np.arange(0.1,1.1,0.1)}

model = MultiOutputRegressor(SVR()) 
model_name = 'SVR' 
loss_df4 = fit_model(model,model_name, grid,loss_df4, y_test, y_pred)
model_list[-1]

"""Дерево решений"""

model = RandomForestRegressor(random_state=14) 
grid = {
    'n_estimators' : range(0, 101, 25),
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth' : range(1, 5, 1),
    
}
model_name = 'Random Forest Regressor'
loss_df4 = fit_model(model, model_name, grid,loss_df4, y_test, y_pred)
model_list[-1]

""" нейронная сеть 

 Рекомендательная нейросеть для соотношения матрица-наполнитель

"""

loss_df4

df4.columns

y = df4['Соотношение матрица-наполнитель']
x = df4.drop(['Соотношение матрица-наполнитель'], axis = 1)

x_train, x_test, y_train,y_test = train_test_split(x, y , test_size=0.3, random_state=42)
y.shape,x.shape

def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.ylim([0, 1])
    plt.xlabel('Эпоха')

    plt.ylabel('MAE [MPG]')
    plt.legend()
    plt.grid(True)
model = Sequential()
model.add(layers.Dropout(0.12))
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dropout(0.12))
model.add(layers.Dense(19, activation='relu'))
model.add(layers.Dropout(0.12))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dropout(0.12))
model.add(layers.Dense(32, activation='tanh'))
model.add(layers.Dense(1))

model
df4model = model.compile(optimizer='adam', loss='mae', metrics=['mae'])
history = model.fit(
    x_train,
    y_train,
    validation_split=0.2,
    verbose=1, epochs=150)

model.summary()

plot_loss(history)

"""Бинарная и множественная классификация"""

input_ = keras.layers.Input(shape=(x_train.shape[1],)) # входной слой
x = keras.layers.Dense(30, activation='relu')(input_) # полносвязный слой
x = keras.layers.Dense(20, activation='relu')(x) # полносвязный слой
output_ = keras.layers.Dense(1, activation='sigmoid')(x) # выходной слой

model = keras.models.Model(input_, output_) # определем вход и выход моедли

model.compile(loss = 'binary_crossentropy', # определяем метрики и алгоритм оптимизации
              optimizer = 'adam',
              metrics = 'accuracy'
             )

history = model.fit(x_train, y_train, 
                    epochs=100, 
                    batch_size=30, 
                    validation_split=0.3,
                    callbacks=keras.callbacks.EarlyStopping(patience=5)
                   ) # сохраняем историю тренировки

plot_loss(history)

print('MAE на тестовой выборке: %.3f' %mean_absolute_error(y_test, model.predict(x_test)))

"""Нейронная сеть для задач регрессии"""

input_ = keras.layers.Input(shape=(x_train.shape[1],)) # входной слой
x = keras.layers.Dense(400, activation='relu')(input_) # полносвязный слой
x = keras.layers.Dropout(0.3)(x)
x = keras.layers.Dense(200, activation='relu')(x) # полносвязный слой
x = keras.layers.Dropout(0.2)(x)
x = keras.layers.Dense(100, activation='relu')(x) # полносвязный слой
x = keras.layers.Dropout(0.2)(x)
x = keras.layers.Dense(50, activation='relu')(x) # полносвязный слой
x = keras.layers.Dropout(0.2)(x)
x = keras.layers.Dense(20, activation='relu')(x) # полносвязный слой
output_ = keras.layers.Dense(1)(x) # выходной слой

model = keras.models.Model(input_, output_) # определем въод и выход моедли

early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', 
                                           patience=6) # ранняя остановка
reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', 
                                              factor=0.25, 
                                              patience=3, 
                                              verbose=1) # редактирование скорости обучения

model.compile(loss = 'mse', # определяем метрики и алгоритм оптимизации
              optimizer = 'adam',
              metrics = ['mae']
             )

history = model.fit(x_train, 
                    y_train, 
                    epochs=100,
                    batch_size=70,
                    validation_split=0.3,
                    callbacks = [early_stop, reduce_lr],
                    shuffle=False
                   ) # сохраняем историю тренировки

pd.DataFrame(history.history).iloc[:, :4].plot()

print('MAE на тестовой выборке: %.3f' %mean_absolute_error(y_test, model.predict(x_test)))

"""Заключение

Стоит подвести итог и сказать, что машинное обучение в задачах моделей прогнозирования – довольно сложный процесс, требующий навыков программирования, и профессионального подхода к сфере самих композитных материалов.
 Необходимо понимать, на какие атрибуты нужно в первую очередь обратить внимание, чтобы суметь впоследствии грамотно и чётко спрогнозировать тот или иной признак. И, естественно, обладать всеми необходимыми знаниями, умениями и навыками для прогнозов и расчетов. 
 В ходе работы был задействован дата-сет с реальными данными, произведен сопутствующий анализ; построены разнообразные графики,осуществлено разбиение данных на обучающую и тестовую выборки, которая во многом облегчила процесс машинного обучения. 
 В рамках машинного обучения и поиска гиперпараметров были задействованы несколько алгоритмов: линейная регрессия, К ближайших соседей, деревья решений,случайный лес.
  Поиск гиперпараметров осуществлялся при помощи таких методов, как «GridSearch».Обучена нейронная сеть и разработано пользовательское приложение, предсказывающе вероятный прогноз по заданным параметрам. 

"""

loss_df4

for model in model_list:
  print(model)

from joblib import dump, load
dump(model_list[0], 'filename.remiz')

model_best = load('filename.remiz')

model_best

"""ПРИЛОЖЕНИЕ"""

from joblib import dump, load

from joblib import dump, load
def input_variable():

  x1 = float(input('Введите значение переменной Соотношение матрица-наполнитель: '))
  x2 = float(input('Введите значение переменной Плотность: '))
  x3 = float(input('Введите значение переменной Модуль упругости: '))
  x4 = float(input('Введите значение переменной Количество отвердителя: '))
  x5 = float(input('Введите значение переменной Содержание эпоксидных групп: '))
  x6 = float(input('Введите значение переменной Температура вспышки: '))
  x7 = float(input('Введите значение переменной Поверхностная плотность: '))
  x8 = float(input('Введите значение переменной Потребление смолы: '))
  x9 = float(input('Введите значение переменной Угол нашивки: '))
  x10 = float(input('Введите значение переменной Шаг нашивки: '))
  x11 = float(input('Введите значение переменной Плотность нашивки: '))
  return x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11

def input_proc(X):
  print('вызов модели')
  res = model_best.predict(X)
  return res 

def app_model():
  scaler_x = load('minmax_x.remiz')
  scaler_y = load('minmax_y.remiz') 
  model_l = load('filename.remiz') 
  print('Приложение прогнозирует значения модулей упругости и растяжения')
  for i in range(110):
    try:
      print('введите 1 для прогноза, 2 для выхода')
      check = input()
      
      if check == '1':
        print('Введите данные')
        X = input_variable()
        X = scaler_x.transform(np.array(X).reshape(1,-1))
        print(['Модуль упругости при растяжении, ГПа', 'Прочность при растяжении, МПа'])
        print(scaler_y.inverse_transform(input_proc(X)))


      elif check == '2':
        break
      else:
        print('Повторите выбор')
    except Exeption as e:
      print('Неверные данные. Повторите операцию')
      print(e)
app_model()

from google.colab import drive
drive.mount('/content/drive')

! pwd

#@title Текст заголовка по умолчанию
!jupyter nbconvert --to html notebook.ipynb