import socket,time
import threading
import tensorflow as tf
import numpy as np
import math,csv
import os
import requests
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def tensor_test(parameter):
	iteration_times = int(parameter[0])
	training_x = np.floor(10 * np.random.random([10]),dtype=np.float32)
	print (training_x)

	training_y = np.floor(10 * np.random.random([10]),dtype=np.float32)
	print (training_y)

	training_z = 3*training_x*training_y + 6.5*training_y +8.0
	print (training_z)

	x = tf.placeholder(tf.float32)
	y = tf.placeholder(tf.float32)
	z = tf.placeholder(tf.float32)

	a = tf.Variable(0.0)
	b = tf.Variable(0.0)
	c = tf.Variable(0.0)

	predict_z = a*x*y + b*y +c

	loss = tf.reduce_sum(tf.pow(predict_z-z,2))
	#loss = tf.reduce_sum(tf.square(predict_y-y))

	optimizer = tf.train.GradientDescentOptimizer(0.00008)
	train = optimizer.minimize(loss)

	sess = tf.Session()
	sess.run(tf.global_variables_initializer())
	print("iteration_times: "+str(iteration_times))
	for i in range(iteration_times):
		sess.run(train, {x:training_x, y:training_y, z:training_z})
		#print (sess.run([a,b,c,loss],{x:training_x, y:training_y, z:training_z}))
	result = sess.run([a,b,c,loss],{x:training_x, y:training_y, z:training_z})
	result_string = "|"
	for i in range(len(result)):
		result_string += str(result[i])+"|"
	return result_string

def get_data_for_NN(file_name):
	training_variables = []
	observed_values = []
	with open(file_name) as csvfile:
		data = csv.reader(csvfile)
		for row in data:
			training_variables.append(float(row[0]))
			observed_values.append(float(row[1]))
	return [training_variables,observed_values]

def get_data_list_for_kmeans(file_name):
	attr_list = [] 
	with open(file_name) as csvfile:
		data_list = csv.reader(csvfile)
		for row in data_list:
			attr_list.append(row)
	return attr_list

def add_layer(inputs, in_size, out_size, activation_function=None):
	Weights = tf.Variable(tf.random_normal([in_size, out_size]))
	biases = tf.Variable(tf.zeros([1, out_size]) + 0.1)
	Wx_plus_b = tf.matmul(inputs, Weights) + biases   

	if activation_function is None:
		outputs = Wx_plus_b
	else:
		outputs = activation_function(Wx_plus_b)
	return outputs

def neural_network(x_data,y_data,parameter):
	test_data_num = int(parameter[0])
	iteration_times = int(parameter[1])
	x = tf.placeholder(tf.float32, [None, 1])
	y = tf.placeholder(tf.float32, [None, 1])
	training_data_x = []
	test_data_x_feed = []
	for var in x_data:
		training_data_x.append([var])
	test_data_x_feed = training_data_x[:test_data_num]
	training_data_x = training_data_x[test_data_num:] 

	training_data_y = []
	test_observed_value = []
	for var in y_data:
		training_data_y.append([var])
	for i in range(len(training_data_y)-test_data_num,len(training_data_y)):
		test_observed_value.append(training_data_y[i][0])
	training_data_y = training_data_y[test_data_num:]

	# add hidden layer
	l1 = add_layer(x, 1, 10, activation_function=tf.nn.relu)
	# add output layer
	prediction = add_layer(l1, 10, 1, activation_function=None)
	loss = tf.reduce_mean(tf.reduce_sum(tf.square(y - prediction),reduction_indices=[1]))
	train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)
	init = tf.global_variables_initializer()
	sess = tf.Session()
	sess.run(init)
	for i in range(iteration_times):
		sess.run(train_step, feed_dict={x: training_data_x, y: training_data_y})
	result_string = "|"
	prediction_value = sess.run(prediction, feed_dict={x: test_data_x_feed})
	test_estimated_value = []
	for i in range(len(prediction_value)):
		test_estimated_value.append(prediction_value[i][0])
		result_string += str(test_observed_value[i])+","+str(prediction_value[i][0])+";"
	return result_string

def k_means_cluster(data_list,cluster_num):
	df = pd.DataFrame(data_list)
	kmeans = KMeans(n_clusters=int(cluster_num))
	kmeans.fit(df)
	cluster_labels = kmeans.labels_
	result_string = ""
	for label in cluster_labels:
		result_string += str(label)+","
	return result_string


def excute_method(userID,server_IP,method_name,content):
	global isBusy
	isBusy = True
	if method_name == "tensorflow_test":
		parameter = content
		result_string = tensor_test(parameter)
		print("Finish, and result: "+result_string)
		parameter_string = "|"
		for i in range(len(parameter)):
			parameter_string += str(parameter[i])+"|"
		r = requests.post("http://"+server_IP+"/tensor/send_result_back/", data={'username': username,'password': password,'userID': userID,'method': method_name,'parameter': parameter_string,'result': result_string})
	elif method_name == "NeuralNetwork":
		file_name = content[0].split('/')[-1]
		print(content[0])
		data = get_data_for_NN("http://"+server_IP+"/"+content[0])
		parameter = content[1:]
		result_string = neural_network(data[0],data[1],parameter)
		parameter_string = "|"
		for i in range(len(parameter)):
			parameter_string += str(parameter[i])+"|"
		r = requests.post("http://"+server_IP+"/tensor/send_result_back/", data={'username': username,'password': password,'userID': userID,'method': method_name,'parameter': parameter_string,'result': result_string,'file_name': file_name})
	elif method_name == "Kmeans":
		file_name = content[0].split('/')[-1]
		data_list = get_data_list_for_kmeans("http://"+server_IP+"/"+content[0])
		cluster_num = content[1]
		result_string = k_means_cluster(data_list, cluster_num)
		parameter_string = "|"+str(cluster_num)+"|"
		r = requests.post("http://"+server_IP+"/tensor/send_result_back/", data={'username': username,'password': password,'userID': userID,'method': method_name,'parameter': parameter_string,'result': result_string,'file_name': file_name})

	#print(r.status_code, r.reason)
	#print(r.text)
	isBusy = False


def regularly_send_status():
	global username
	global password
	global hostIP
	global server_IP
	global time_send_status
	global isBusy
	if isBusy:
		r = requests.post("http://"+server_IP+"/tensor/worker_check_status/", data={'username': username,'password': password,'hostIP': hostIP,'status': "Working!"})
		#print(r.status_code, r.reason)
		print(r.text)
		threading.Timer(time_send_status,regularly_send_status).start()

	else:
		r = requests.post("http://"+server_IP+"/tensor/worker_check_status/", data={'username': username,'password': password,'hostIP': hostIP,'status': "Ready!"})
		#print(r.status_code, r.reason)
		print(r.text)
		threading.Timer(time_send_status,regularly_send_status).start()

##
username = "cluster_worker"
password = "worker_password"
server_IP = ""
time_send_status = 3.0
##

hostIP = ""
port = 12343
isBusy = False
regularly_send_status()
s = socket.socket()
s.bind((hostIP, port))
s.listen(5)
while True:
	c, addr = s.accept()
	start_time = time.time()
	print ('There are some node wants to connect：', addr)
	c.send("OK".encode())
	receive_data = c.recv(1024).decode().split(',')
	if receive_data[0] == username and receive_data[1] == password:
		c.send("What can I do for you?".encode())
		request = c.recv(1024).decode()
		tmp = request.split(',')
		uID = tmp[0]
		tmp = tmp[1].split('|')
		method_name = tmp[0]
		content = tmp[1:]
		print(method_name)
		c.send("My pleasure".encode())	
		excute_method(uID,addr[0],method_name,content)
	else:
		c.send("Authentication Failed".encode())
	c.close()
	end_time = time.time()
	print(end_time-start_time)

