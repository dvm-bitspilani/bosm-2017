from django.shortcuts import render, redirect
from registrations.models import *
from barg

def gen_barcode(gl_id):
	try:
		try:
			g_l = GroupLeader.objects.get(id=gl_id)
			encoded = g_l.barcode
		except ObjectDoesNotExist:
			return None
		encoded = ""+encoded
	except:
		gl_ida = "%04d" % int(gl_id)
		mixed = string.ascii_uppercase + string.ascii_lowercase
		encoded = ''.join([x+mixed[randint(0,51)] for x in gl_ida])
		g_l.barcode = encoded
		g_l.save()
	try:
		image='/home/dvm/bosm/public_html/bosm2017/barcodes/%s.gif' % str(gl_id)
	except:
		image = '~/barcodes/%s.gif' % str(gl_id)
	barg.code128_image(encoded).save(image)
	return encoded
