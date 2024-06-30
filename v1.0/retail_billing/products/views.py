# products views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from products.models import product, bill_data
import json
from django.contrib.auth.decorators import login_required
from .templatetags.extra_filters import has_group

def index(request):
    data = {}
    if request.user.is_authenticated:
        return redirect('/home/')
    else:
        return HttpResponse("<body style='background-color:black;color:white;'><center><br><br><br><br> Login: <a href='login/' style='color:rgb(255, 190, 106);'>Click Here</a></center></body>")

@login_required(login_url='/login/')
def home(request):
    data = {}
    data['PV'] = 0  # PV: Product Valuation
    items = list(product.objects.all().order_by('-id'))[:]
    for item in items:
        data['PV'] = data['PV'] + (item.price * item.available_qty)
    return render(request,'home.html', data)

@login_required(login_url='/login/')
def bill(request):
    if 'term' in request.GET:
        product_names = []
        qs = list(product.objects.filter(name__icontains=request.GET.get('term')))  #istartswith can also be used.
        for item in qs:
            product_names.append(item.name)
        return JsonResponse(product_names, safe=False)
    
    if request.method=='POST':
        data = {}
        data['issue'] = 'no'
        what = request.POST['what']
        if(what=='add_to_bill'):
            prd_nm = request.POST['prd_name']
            bill_id = int(request.POST['bill_id'])
            try:
                prd_obj = product.objects.get(name__iexact=prd_nm)
                item_dict = {}
                item_dict['id'] = prd_obj.id
                item_dict['name'] = prd_obj.name
                item_dict['price'] = prd_obj.price
                item_dict['unit'] = prd_obj.unit
                item_dict['qty'] = 1
                item_dict['amt'] = prd_obj.price * 1
                if(bill_id==0):
                    dict = {}
                    dict['status'] = 'INITIATED'
                    dict['items'] = {}
                    dict['items']['item'+str(prd_obj.id)] = item_dict
                    dict['bill_value'] = prd_obj.price * 1
                    bill_obj = bill_data(b=json.dumps(dict))
                else:
                    bill_obj = bill_data.objects.get(id=bill_id)
                    dict = json.loads(bill_obj.b)
                    if('item'+str(prd_obj.id) in list(dict['items'].keys())):
                        data['issue'] = 'yes'
                        data['message'] = "item already added."
                    else:
                        dict['items']['item'+str(prd_obj.id)] = item_dict
                        dict['bill_value'] = dict['bill_value'] + item_dict['amt']
                        bill_obj.b = json.dumps(dict)
                bill_obj.save()
                data['bill_id'] = bill_obj.id
                data['bill_dict'] = json.loads(bill_obj.b)
            except:
                data['issue'] = 'yes'
                data['message'] = 'item not found'
                data['bill_id'] = bill_id   
            return JsonResponse(data)
        elif(what=='qty_change'):
            bill_id = int(request.POST['bill_id'])
            item_details = request.POST['item_details'].split(',')
            item_id = item_details[1]
            change = item_details[0]
            bill_obj = bill_data.objects.get(id=bill_id)
            dict = json.loads(bill_obj.b)
            if(change=='up'):
                dict['items']['item'+item_id]['qty']+=1
                dict['items']['item'+item_id]['amt']+=dict['items']['item'+item_id]['price']
                dict['bill_value']+=dict['items']['item'+item_id]['price']
            elif(change=='down'):
                if(dict['items']['item'+item_id]['qty'] == 1):
                    dict['bill_value']-=dict['items']['item'+item_id]['price']
                    del dict['items']['item'+item_id]
                else:
                    dict['items']['item'+item_id]['qty']-=1
                    dict['items']['item'+item_id]['amt']-=dict['items']['item'+item_id]['price']
                    dict['bill_value']-=dict['items']['item'+item_id]['price']
            else:
                print("ERROR.")
            bill_obj.b = json.dumps(dict)
            bill_obj.save()
            data['bill_id'] = bill_obj.id
            data['bill_dict'] = dict
            return JsonResponse(data)
        elif(what=='bill_paid'):
            bill_id = int(request.POST['bill_id'])
            if(bill_id != 0):
                bill_obj = bill_data.objects.get(id=bill_id)
                dict = json.loads(bill_obj.b)
                dict['status'] = "PAID"
                bill_obj.b = json.dumps(dict)
                bill_obj.save()
                #Changing products database:
                for key in dict['items'].keys():
                    prod_obj = product.objects.get(id=dict['items'][key]['id'])
                    prod_obj.available_qty-=dict['items'][key]['qty']
                    prod_obj.save()
                data['bill_id'] = bill_id
                data['bill_dict'] = dict
            else:
                data['issue'] = 'yes'
                data['message'] = 'Please add items first.'
            return JsonResponse(data)
        else:
            return HttpResponse("ok")
    else:
        data = {}
        return render(request,'bill.html',data)

@login_required(login_url='/login/')
def prev_bill(request):
    data = {}
    ## ****** Collect Recent Bills ****** ##
    data['recent_bills'] = {}
    bill_objs = list(bill_data.objects.all().order_by('-date_updated'))[:50]
    for bill_obj in bill_objs:
        d = {}
        d['bill_id'] = bill_obj.id
        d['bill_dict'] = json.loads(bill_obj.b)
        d['date_created'] = bill_obj.date_created.strftime('%d-%b-%Y | %H:%M')
        d['date_updated'] = bill_obj.date_updated.strftime('%d-%b-%Y | %H:%M')
        data['recent_bills'][bill_obj.id] = d
    ## ****** Check for any special requested ****** ##
    if request.method=='POST':
        data['issue'] = 'no'
        what = request.POST['what']
        if(what=='get_bill'):
            try:
                bill_id = int(request.POST['bill_id'])			
                bill_obj = bill_data.objects.get(id=bill_id)
                data['bill_id'] = bill_id
                data['bill_dict'] = json.loads(bill_obj.b)
                data['date_created'] = bill_obj.date_created.strftime('%d-%b-%Y | %H:%M:%S')
                data['date_updated'] = bill_obj.date_updated.strftime('%d-%b-%Y | %H:%M:%S')
            except:
                data['issue'] = 'yes'
                data['message'] = 'Bill not found!!'
        else:
            print("ERROR: Don't even try !!")
        return JsonResponse(data)
    else:
        return render(request,'prev_bill.html',data)

# require group -> store manager
@login_required(login_url='/login/')
def add_product(request):
    data = {}
    data['products'] = list(product.objects.all().order_by('-id'))[:5]
    if not has_group(request, 'store_manager'):
        return redirect('/home/')
    elif request.method=='POST':
        prd_nm = request.POST['prd_name']
        sp = request.POST['sp']
        unit = request.POST['unit']
        qty = request.POST['qty']
        tags = request.POST['tags']
        new_prd = product(name=prd_nm,price=sp,unit=unit,tags=tags,available_qty=qty)
        new_prd.save()
        return redirect('/add/')
    else:
        return render(request,'add_product.html',data)

# require group -> store manager
@login_required(login_url='/login/')    
def settings(request):
    if not has_group(request, 'store_manager'):
        return redirect('/home/')
    data = {}
    data['products'] = list(product.objects.all().order_by('-id'))[:]
    return render(request,'settings.html',data)

# require group -> store manager
@login_required(login_url='/login/')
def upd(request):
    data = {}
    if not has_group(request, 'store_manager'):
        return redirect('/home/')
    elif request.method=='POST':
        what = request.POST['upd_what']
        prd_id = request.POST['upd_id']
        obj = product.objects.get(id=prd_id)
        data['product'] = obj
        if(what=='open'):
            return render(request,'upd.html',data)
        elif(what=='update'):
            if(request.POST['submit_button'] == ' Delete '):
                obj.delete()
            elif(request.POST['submit_button'] == ' Update '):
                obj.name = request.POST['prd_name']
                obj.price = request.POST['sp']
                obj.unit = request.POST['unit']
                obj.available_qty = request.POST['qty']
                obj.tags = request.POST['tags']
                obj.save()
            else:
                pass
            return redirect('/settings/')
            
        else:
            print("updating2..")
            return HttpResponse("Hello Mr. OverSmart !!")
    else:
        return HttpResponse("Hello")


# ******************************************************************* #
# ********* Additional Helper Functions ***************************** #
# ******************************************************************* #        
        
        
        