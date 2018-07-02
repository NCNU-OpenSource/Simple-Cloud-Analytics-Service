from django.db import models

# Create your models here.
class tensorflow_test_result(models.Model):
	ID = models.AutoField(primary_key=True)
	userID = models.TextField()
	iteration_times = models.IntegerField()
	variable1 = models.FloatField()
	variable2 = models.FloatField()
	variable3 = models.FloatField()
	loss = models.FloatField()

class NeuralNetwork_result(models.Model):
	ID = models.AutoField(primary_key=True)
	userID = models.TextField()
	iteration_times = models.IntegerField()
	test_data_num = models.IntegerField()
	result = models.TextField()
	RMSE = models.FloatField()
	R_squared = models.FloatField()
	data_file_name = models.TextField()

class Kmeans_result(models.Model):
	ID = models.AutoField(primary_key=True)
	userID = models.TextField()
	num_cluster = models.IntegerField()
	labels = models.TextField()
	data_file_name = models.TextField()

class worker_check_time(models.Model):
	hostIP = models.TextField()
	time_last_check = models.DateTimeField()
	isBusy = models.BooleanField()

class file(models.Model):
	ID = models.AutoField(primary_key=True)
	title = models.TextField()
	file = models.FileField(upload_to='file/')
	note = models.TextField(null=True)