import csv
import pandas
import random
import uuid
import os
from plotly.offline import plot
import plotly.graph_objs as go
from os.path import join, dirname
import json
import re
import writeToS3 as s3
import deleteDir as d
import notification as n
import argparse

class Classification:

    def __init__(self,awsPath, localSavePath, localReadPath, remoteReadPath):

        self.localSavePath = localSavePath
        self.awsPath = awsPath

        # download remote socialmedia data into a temp folder
        # load it into csv
        filename = remoteReadPath.split('/')[-2] + '.csv'
        self.filename = filename # save it so split function can reuse this name
        s3.downloadToDisk(filename=filename,localpath=localReadPath, remotepath=remoteReadPath)
        
        Array = []
        try:
            with open(localReadPath + filename,'r',encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        Array.append(row)
                    except Exception as e:
                        pass
        except:
            with open(localReadPath + filename,'r',encoding='ISO-8859-1') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        Array.append(row)
                    except Exception as e:
                        pass

        df = pandas.DataFrame(Array[1:], columns=Array[0])
       
        # remoteReadPath always follows format of sessionID/folderID/datasetName/
        # example: local/GraphQL/twitter-Tweet/trump/ => ['local','GraphQL', 'twitter-Tweet','trump','']
        source = remoteReadPath.split('/')[2]
        
        if (source == 'twitter-Tweet') and ('text' in Array[0]):
            self.corpus = list(set(df[df['text']!='']['text'].dropna().astype('str').tolist()))
        elif (source == 'twitter-Stream') and ('_source.text' in Array[0]):
            self.corpus = list(set(df[df['_source.text']!='']['_source.text'].dropna().astype('str').tolist()))

        # find the unique content in crimson hexagon
        elif (source=='crimson-Hexagon') and ('contents' in Array[0]):
            self.corpus = list(set(df[df['contents'] != '']['contents'].dropna().astype('str').tolist()))

        # find the unique title in reddit posts
        elif (source=='reddit-Search' or source=='reddit-Post') and 'title' in Array[0]:
            self.corpus = list(set(df[df['title']!='']['title'].dropna().astype('str').tolist()))
        elif source =='reddit-Historical-Post' and '_source.title' in Array[0]:
            self.corpus = list(set(df[df['_source.title']!='']['_source.title'].dropna().astype('str').tolist()))

        # find the unique body in reddit comments
        elif (source == 'reddit-Comment' or source == 'reddit-Historical-Comment') and 'body' in Array[0]:
            self.corpus = list(set(df[df['body']!='']['body'].dropna().astype('str').tolist()))

        # TODO: switch reddit comment to elasticsearch endpoint
        # elif source == 'reddit-Historical-Comment' and '_source.body' in Array[0]:
        #     self.corpus = list(set(df[df['_source.body']!='']['_source.body'].dropna().astype('str').tolist()))
 
        # strip http in the corpus
        self.corpus = [ re.sub(r"http\S+","",text) for text in self.corpus]

    def split(self,ratio):
        training_set = list(random.sample(self.corpus, int(len(self.corpus)*ratio/100)))
        testing_set = [item for item in self.corpus if item not in training_set]

        # plot a pie chart of the split
        labels = ['training set data points','unlabeled data points']
        values = [len(training_set), len(testing_set)]
        trace = go.Pie(labels=labels, values = values, textinfo='value')
        div_split = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')
        fname_div_split = 'div_split.html'
        with open(self.localSavePath + fname_div_split,"w") as f:
            f.write(div_split)
        s3.upload(self.localSavePath, self.awsPath, fname_div_split)
        div_url = s3.generate_downloads(self.awsPath, fname_div_split)
        
        fname1 = 'TRAINING_' + self.filename
        try:
            with open(self.localSavePath + fname1,'w',newline="",encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for row in training_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        except:
            with open(self.localSavePath + fname1,'w',newline="",encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for row in training_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        s3.upload(self.localSavePath, self.awsPath, fname1)
        training_url = s3.generate_downloads(self.awsPath, fname1)



        fname2 = 'UNLABELED_' + self.filename
        try:
            with open(self.localSavePath + fname2,'w',newline="",encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                for row in testing_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        except:
            with open(self.localSavePath + fname2,'w',newline="",encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                for row in testing_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        s3.upload(self.localSavePath, self.awsPath, fname2)
        unlabeled_url = s3.generate_downloads(self.awsPath, fname2)


        return {'div': div_url, 'training':training_url, 'testing': unlabeled_url}


if __name__ == '__main__':

    output = dict()

    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--ratio',required=True)
    parser.add_argument('--s3FolderName',required=True)
    parser.add_argument('--email',required=True)
    args = parser.parse_args()
    
    # arranging the paths
    uid = str(uuid.uuid4())
    awsPath = args.s3FolderName + '/ML/classification/' + uid +'/'
    localSavePath = '/tmp/' + args.s3FolderName + '/ML/classification/' + uid + '/'
    localReadPath = '/tmp/' + args.s3FolderName + '/' + uid + '/'
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localReadPath):
        os.makedirs(localReadPath)

    fname = 'config.json'
    with open(localSavePath + fname,"w") as f:
        json.dump(vars(args),f)
    s3.upload(localSavePath, awsPath, fname)
    output['config'] = s3.generate_downloads(awsPath, fname)
    output['uuid'] = uid    

    classification = Classification(awsPath, localSavePath, localReadPath, args.remoteReadPath)
    output.update(classification.split(int(args.ratio)))
    
    d.deletedir('/tmp')
    n.notification(args.email,case=3,filename=awsPath) 

