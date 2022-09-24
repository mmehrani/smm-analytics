# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 12:18:15 2022

@author: mohsen
"""

from googletrans import Translator
import pandas as pd
import os
from tqdm import tqdm

translator = Translator(service_urls=['translate.google.com'])


df = pd.read_csv('example_dataset.csv', index_col=0)

for index, row in tqdm(df.iterrows(), total=df.shape[0], desc = brand):
    df.at[index,'text'] = translator.translate(row['text'] + ' XYZ',dest="en").text.replace(' XYZ','') # adding XYZ fulfills the min character limit.

save_path = os.path.join('example_dataset_en')
df.to_csv(save_path, encoding='utf-8')
