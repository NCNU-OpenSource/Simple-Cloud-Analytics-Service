from django.shortcuts import render

from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response

from django.contrib import auth

import socket,os,csv
from django.conf import settings
from . import models
from datetime import datetime

def tensorflow_test(request):
	result_list = models.tensorflow_test_result.objects.all()
	return render_to_response('tensortest.html',locals())

def login(request):
	if request.user.is_authenticated: 
		return HttpResponseRedirect('/tensor/index/')

	username = request.POST.get('username')
	password = request.POST.get('password')

	user = auth.authenticate(username=username, password=password)

	if user is not None and user.is_active:
		auth.login(request, user)
		return HttpResponseRedirect('/tensor/index/')
	else:
		return render_to_response('login.html')

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/tensor/index/')

def index(request):
	return render_to_response('index.html',locals())

def NeuralNetwork(request):
	result_list = models.NeuralNetwork_result.objects.all().order_by('-ID')[0].result.split(';')[:-1]
	num_day = len(result_list)
	x_list = []
	y_list = []
	for i in range(num_day):
		tmp = result_list[i].split(',')
		x_list.append(tmp[0])
		y_list.append(tmp[1])
	day_range = range(1,num_day+1)
	day_start = 356-num_day
	data_list = models.file.objects.all()
	return render_to_response('NeuralNetwork.html',locals())

def kmeans(request):
	obj = models.Kmeans_result.objects.all().order_by('-ID')[0]
	label_list = obj.labels.split(',')[:-1]
	file_path = settings.MEDIA_ROOT+'/file/'+obj.data_file_name
	num_cluster = 0
	for i in range(len(label_list)):
		tmp = int(label_list[i])
		if tmp+1 > num_cluster:
			num_cluster = tmp+1 
	cluster = [[] for i in range(num_cluster)]
	with open(file_path) as csvfile:
		file_csv = csv.reader(csvfile)
		i = 0
		for row in file_csv:
			tmp_row = []
			for col in row:
				tmp_row.append(float(col))
			cluster[int(label_list[i])].append(tmp_row)
			i += 1
	data_list = models.file.objects.all()
	return render_to_response('Kmeans.html',locals())

def call_help(request):
	if request.user.is_authenticated:
		uID = request.user.id
		username = "cluster_worker"
		password = "worker_password"
		workers = models.worker_check_time.objects.all()
		num_workers = len(workers)
		i = 0
		while i < num_workers:
			if not workers[i].isBusy:
				hostIP = workers[i].hostIP
				break
			i += 1
		if i == num_workers:
			return HttpResponse("No worker is available!")
		s = socket.socket()        
		port = 12343

		method = request.POST.get('method')
		if method == "NN" or method == "Kmeans":
			print(request.POST.get('file_exist'))
			if request.POST.get('file_exist') != "none":
				file_name = request.POST.get('file_exist')
				file_path = settings.MEDIA_ROOT+'/file/'+file_name
				data = models.file.objects.filter(title=file_name)
			else:
				file = request.FILES['file']
				file_path = settings.MEDIA_ROOT+'/file/'+file.name
				data = models.file()
				data.title = file.name
				data.file = file
				data.save()
		s.connect((hostIP, port))
		if s.recv(1024).decode() == "OK":
			s.send((username+","+password).encode())
			receive_string = s.recv(1024).decode()
			if receive_string == "What can I do for you?":
				print(receive_string)	
				if method == "tensorflow_test":
					iteration_times = request.POST.get('iteration_times')
					s.send((str(uID)+",tensorflow_test|"+iteration_times).encode())
				elif method == "NN":
					iteration_times = request.POST.get('iteration_times')
					testdata_num = request.POST.get('testdata_num')
					send_string = str(uID)+",NeuralNetwork|"
					send_string += file_path+"|"
					send_string += testdata_num+"|"+iteration_times+"|"
					s.send(send_string.encode())
				elif method == "Kmeans":
					num_cluster = request.POST.get('num_cluster')
					send_string = str(uID)+",Kmeans|"
					send_string += file_path+"|"
					send_string += num_cluster+"|"
					s.send(send_string.encode())
				receive_string = s.recv(1024).decode()
				print(receive_string)
		s.close()
		
	return HttpResponseRedirect('/tensor/index/')

def send_result_back(request):
	if request.POST.get('username') and request.POST.get('password'):
		username = request.POST.get('username')
		password = request.POST.get('password')
		hostIP = request.POST.get('hostIP')
		if username == "cluster_worker" and password == "worker_password":
			if request.POST.get('userID') and request.POST.get('parameter') and request.POST.get('result'):
				userID = request.POST.get('userID')
				method = request.POST.get('method')
				parameter = request.POST.get('parameter')
				result = request.POST.get('result')
				if method == "tensorflow_test":
					tmp_parameter = parameter.split('|')[1:-1]
					tmp_result = result.split('|')[1:-1]
					data = models.tensorflow_test_result()
					data.userID = userID
					data.iteration_times = tmp_parameter[0]
					data.variable1 = tmp_result[0]
					data.variable2 = tmp_result[1]
					data.variable3 = tmp_result[2]
					data.loss  = tmp_result[3]
					data.save()
				elif method == "NeuralNetwork":
					file_name = request.POST.get('file_name')
					tmp_parameter = parameter.split('|')[1:-1]
					tmp_result = result.split('|')[1:-1]
					data = models.NeuralNetwork_result()
					data.userID = userID
					data.result = tmp_result[0]
					data.test_data_num = int(tmp_parameter[0])
					data.iteration_times = int(tmp_parameter[1])
					data.data_file_name = file_name
					data.save()
				elif method == "Kmeans":
					print(result)
					file_name = request.POST.get('file_name')
					tmp_parameter = parameter.split('|')[1:-1]
					data = models.Kmeans_result()
					data.userID = userID
					data.num_cluster = tmp_parameter[0]
					data.labels = result
					data.data_file_name = file_name
					data.save()
				return HttpResponse("Thanks")
			return HttpResponse("????")
		else:
			return HttpResponse("Authentication Failed")

def worker_check_status(request):
	if request.POST.get('username') and request.POST.get('password'):
		username = request.POST.get('username')
		password = request.POST.get('password')
		hostIP = request.POST.get('hostIP')
		if username == "cluster_worker" and password == "worker_password":
			status = request.POST.get('status')
			print(status)
			worker = models.worker_check_time.objects.filter(hostIP=hostIP)
			if len(worker) == 0:
				new_worker = models.worker_check_time()
				new_worker.hostIP = hostIP
				new_worker.time_last_check = datetime.now()
				if status == "Ready!":
					new_worker.isBusy = False
					new_worker.save()
					return HttpResponse("Stand by!")
				elif status == "Working!":
					new_worker.isBusy = True
					new_worker.save()
					return HttpResponse("Keep up the good work!")
			else:
				worker[0].time_last_check = datetime.now()
				if status == "Ready!":
					worker[0].isBusy = False
					worker[0].save()
					return HttpResponse("Stand by!")
				elif status == "Working!":
					worker[0].isBusy = True
					worker[0].save()
					return HttpResponse("Keep up the good work!")
		else:
			return HttpResponse("Authentication Failed")
	else:
		return HttpResponse("????")
