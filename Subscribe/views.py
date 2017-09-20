from django.shortcuts import render
from django.http import JsonResponse
from models import Subscriber
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
import re

@csrf_exempt
def index(request):

	if request.method == 'POST':

		email = request.POST['email']
		name = request.POST['name']
		mobile_number = request.POST["mobile_number"]
		
		try:
			Subscriber.objects.get(email_address = email)
			user_exists = True
		except:
			user_exists = False

		if user_exists:

			data = {'status':0}
			return JsonResponse(data)

		

		if len(mobile_number) == 10:
			try:

				number = int(mobile_number)

				if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):

					subscriber = Subscriber()
					subscriber.email_address = email
					subscriber.name = name
					subscriber.mobile_number = '+91' + mobile_number
					subscriber.save()
					data = {'status':1,'email':email, 'name':name, 'mobile_number':mobile_number}
					return JsonResponse(data)

				else:

					data = {'status':3}
					return JsonResponse(data)

			except ValueError:
				data = {'status':2}
				return JsonResponse(data)



		else:
			data = {'status':2}
			return JsonResponse(data)

	return render(request, 'Subscribe/index.html')

@staff_member_required
def get_list(request):
	from django.http import HttpResponse, HttpResponseRedirect
	import xlsxwriter
	from models import Subscriber
	# if request.POST:
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	a_list = []


	entries = Subscriber.objects.all()

	for p in entries:
		a_list.append({'obj': p})
	data = sorted(a_list, key=lambda k: k['obj'].id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('new-spreadsheet')
	date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
	worksheet.write(0, 0, "Generated:")
	from time import gmtime, strftime
	generated = strftime("%d-%m-%Y %H:%M:%S UTC", gmtime())
	worksheet.write(0, 1, generated)

	worksheet.write(1, 0, "ID")
	worksheet.write(1, 1, "Name")
	worksheet.write(1, 2, "Email ID")
	worksheet.write(1, 3, "Mobile No.")

	

	for i, row in enumerate(data):
		"""for each object in the date list, attribute1 & attribute2
		are written to the first & second column respectively,
		for the relevant row. The 3rd arg is a failure message if
		there is no data available"""

		worksheet.write(i+2, 0, deepgetattr(row['obj'], 'id', 'NA'))
		worksheet.write(i+2, 1, deepgetattr(row['obj'], 'name', 'NA'))
		worksheet.write(i+2, 2, deepgetattr(row['obj'], 'email_address', 'NA'))
		worksheet.write(i+2, 3, deepgetattr(row['obj'], 'mobile_number', 'NA'))
		

	workbook.close()
	filename = 'ExcelReport.xlsx'
	output.seek(0)
	response = HttpResponse(output.read(), content_type="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

def deepgetattr(obj, attr, default = None):
    
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj