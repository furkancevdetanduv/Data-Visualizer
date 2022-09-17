import os
from django.shortcuts import render , get_object_or_404, render_to_response
from django.http import HttpResponse ,HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Question,Choice
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image
import pandas as pd
from io import StringIO, BytesIO
from django.views.generic import View
from braces.views import (
    AjaxResponseMixin,
    JSONResponseMixin
)




from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def index(request):
	return HttpResponse("Test response")

def detail(request, question_id):
	question = get_object_or_404(Question, pk = question_id)
	return render(request, 'polls/detail.html', {'question' : question })

def results(request, question_id):
	question = get_object_or_404(Question, pk = question_id )
	return render(request , 'polls/results.html', {'question' : question})

def vote (request, question_id):
	return HttpResponse("You are voting on question %s." %question_id)
	question = get_object_or_404(Question, pk = question_id)
	try:
		selected_choice = question.choice_set.get(pk = request.POST['choice'])
		given_str = question.choice_set.get(pk = request.POST['str'])
	except(KeyError , Choice.DoesNotExist):
	   	return render(request,'polls/detail.html', {
	    	'question':question,
	    	'error_message': "You did not select a choice."
	    	})
	else:
	    selected_choice.votes += 1
	    selected_choice.save()
	    return HttpResponseRedirect(reverse ('polls:results', args = (given_str,)))    

def index (request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	template = loader.get_template('polls/index.html')
	context = {
		'latest_question_list':
		latest_question_list,
	}
	return HttpResponse(template.render(context,request))
	
def uploadcsv(request):
	data = {}
	if "GET" == request.method:
		return render(request, "polls/uploadcsv.html",data) 
	csv_file = request.FILES['csv_file']
	file_data = csv_file.read().decode("utf-8")
	TESTDATA = StringIO(file_data)
	df = pd.read_csv(TESTDATA, sep = ",|;",error_bad_lines=False)
	slist = []
	slist = df.columns
	nlist= list(map(lambda x: x[1:-1], slist))
	df.columns = nlist
	new = df.head()
	path = default_storage.save('polls/uploadedcsvs/uploaded.csv', csv_file)
	return render(request, 'polls/new.html',{'slist' : nlist,'new' : new.to_html() })

def drawchart(request):
	csv_file = default_storage.open(os.path.join("polls/uploadedcsvs/", 'uploaded.csv'))
	file_data = csv_file.read().decode("utf-8")
	TESTDATA = StringIO(file_data)
	df = pd.read_csv(TESTDATA, sep = "," , error_bad_lines=False)
	slist = []
	slist = df.columns
	nlist= list(map(lambda x: x[1:-1], slist))
	df.columns = nlist
	l=[]
	l = request.POST.getlist('inputs')
	res = []
	res = [i for i in l if "date" in i] 
	resx = [i for i in l if "Date" in i]
	if res != [] or resx !=[]:#changing over time
		xaxis = res
		yaxis = [i for i in l if "date" not in i] 
		j=len(yaxis)
		if df[xaxis[0]].count() <100:#few periods
			if j > 1:
				fig, ax = plt.subplots()
				for cols in xaxis :
					for col in yaxis:
						ax=df.plot(cols, col, ax=ax,figsize=(25,20),secondary_y = [yaxis[1]])
						                 
	                    
	                    
			else:
				fig, ax = plt.subplots()
				for cols in xaxis :
					for col in yaxis:
						df.plot.bar(cols, col, figsize=(20,20))
	                    
		else : # many periods
			if j > 1:
				fig, ax = plt.subplots()
				for cols in xaxis :
					for col in yaxis:
						plt.figure()
						ax=df.plot(cols, col, ax=ax,figsize=(25,20),secondary_y = [yaxis[1]])
						ax.set_ylabel("1233",fontsize = 10)
						                    
			else:
				fig, ax = plt.subplots()
				for cols in xaxis :
					for col in yaxis:
						df.plot(cols, col, figsize=(20,20))
	                    
	                    
	else:#others
		xaxis = res
		yaxis = l
		j=len(yaxis)
		if j == 2:
			fig, ax = plt.subplots()
			for cols in xaxis :
				for col in yaxis:
					ax=df.plot(cols, col, ax=ax,figsize=(25,20),secondary_y = [yaxis[1]])
					ax.set_ylabel(yaxis[0])
					ax.set_xlabel(yaxis[1])

		else:
			fig, ax = plt.subplots()
			for cols in xaxis :
				for col in yaxis:
					df.plot(cols, col, ax=ax,figsize=(20,20),secondary_y=True)

	buffer = BytesIO()
	canvas = pylab.get_current_fig_manager().canvas
	canvas.draw()
	pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
	pilImage.save(buffer, "PNG")
	pylab.close()
 
    # Send buffer in a http response the the browser with the mime type image/png set
	return HttpResponse(buffer.getvalue(), content_type="image/png")


def dropzone(request):
	return render(request, 'polls/dropzone.js')