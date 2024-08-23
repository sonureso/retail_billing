# products views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from products.models import product, bill_data, customer
from stores_app.models import store_emp
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
    items = list(product.objects.all().filter(store=get_store_obj(request.user)).order_by('-id'))[:]
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
    for item in items:
        data['PV'] = data['PV'] + (item.WS_price * item.available_qty)
    data['SV'] = data['PV']+data['store_obj'].cash_value
    return render(request,'home.html', data)

@login_required(login_url='/login/')
def bill(request):
    if 'term' in request.GET:
        product_names = []
        qs = list(product.objects.filter(store=get_store_obj(request.user)).filter(name__icontains=request.GET.get('term')))  #istartswith can also be used.
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
            cust_name = request.POST['cust']
            try:
                try:
                    cust_obj = customer.objects.filter(store_obj=get_store_obj(request.user)).get(name__iexact=cust_name)
                except:
                    data['issue'] = 'yes'
                    data['message'] = 'Please select valid customer !!!'
                    data['bill_id'] = bill_id 
                    return JsonResponse(data)
                prd_obj = product.objects.filter(store=get_store_obj(request.user)).get(name__iexact=prd_nm)
                # customer specific pricing:
                price = prd_obj.price if int(cust_obj.category) == 0 else prd_obj.WS_price
                # print("Customer category is:",int(cust_obj.category))
                # print("price applied is: ",price)
                item_dict = {}
                item_dict['id'] = prd_obj.id
                item_dict['name'] = prd_obj.name
                item_dict['price'] = price
                item_dict['unit'] = prd_obj.unit
                item_dict['qty'] = 1
                item_dict['amt'] = price * 1
                if(bill_id==0):
                    dict = {}
                    dict['status'] = 'INITIATED'
                    dict['items'] = {}
                    dict['items']['item'+str(prd_obj.id)] = item_dict
                    dict['bill_value'] = price * 1
                    bill_obj = bill_data(b=json.dumps(dict),store=get_store_obj(request.user),cust_obj=cust_obj)
                else:
                    bill_obj = bill_data.objects.filter(store=get_store_obj(request.user)).get(id=bill_id)
                    dict = json.loads(bill_obj.b)
                    if('item'+str(prd_obj.id) in list(dict['items'].keys())):
                        data['issue'] = 'yes'
                        data['message'] = "item already added."
                    else:
                        dict['items']['item'+str(prd_obj.id)] = item_dict
                        dict['bill_value'] = dict['bill_value'] + item_dict['amt']
                        bill_obj.b = json.dumps(dict)
                    bill_obj.cust_obj = cust_obj
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
            bill_obj = bill_data.objects.filter(store=get_store_obj(request.user)).get(id=bill_id)
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
            cust_name = request.POST['cust']
            cust_obj = customer.objects.filter(store_obj=get_store_obj(request.user)).get(name__iexact=cust_name)
            if(bill_id != 0):
                bill_obj = bill_data.objects.filter(store=get_store_obj(request.user)).get(id=bill_id)
                dict = json.loads(bill_obj.b)
                dict['status'] = "PAID"
                bill_obj.b = json.dumps(dict)
                bill_obj.cust_obj = cust_obj
                bill_obj.save()
                # Upate Customer visit count:
                cust_obj.visit_freq+=1
                cust_obj.save()
                # Changing products database:
                for key in dict['items'].keys():
                    prod_obj = product.objects.filter(store=get_store_obj(request.user)).get(id=dict['items'][key]['id'])
                    prod_obj.available_qty-=dict['items'][key]['qty']
                    prod_obj.save()
                # Update Store Cash Value:
                store_obj = get_store_obj(request.user)
                store_obj.cash_value += dict['bill_value']
                store_obj.save()

                data['bill_id'] = bill_id
                data['bill_dict'] = dict
                data['cust'] = str(cust_obj)
            else:
                data['issue'] = 'yes'
                data['message'] = 'Please add items first.'
            return JsonResponse(data)
        else:
            return HttpResponse("ok")
    else:
        data = {}
        emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
        data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
        return render(request,'bill.html',data)

@login_required(login_url='/login/')
def cust_home(request):
    # AJAX Call for getting customers name in suggest
    if 'term' in request.GET:
        cust_names = []
        qs = list(customer.objects.filter(store_obj=get_store_obj(request.user)).filter(name__icontains=request.GET.get('term')))  #istartswith can also be used.
        for item in qs:
            cust_names.append(item.name)
        return JsonResponse(cust_names, safe=False)
    else:
        data = {}
        store_obj = get_store_obj(request.user)
        data['store_obj'] = store_obj
        data['cust_obj_list'] = list(customer.objects.all().filter(store_obj=store_obj))
        # print("Customers are: ", data['cust_obj_list'])
        return render(request,'customers.html', data)

@login_required(login_url='/login/')
def upd_cust(request):
    data = {}
    data['what'] = "Nothing"
    data['store_obj'] = get_store_obj(request.user)
    if request.method=='POST':
        what = request.POST['upd_what']
        print("What is: ",what)
        if what == "form_create_new_cust":
            data['what'] = "form_create_new_cust"
            return render(request,'upd_cust.html', data)
        elif what == "form_update_cust":
            cust_id = request.POST['upd_id']
            data['what'] = "form_update_cust"
            data['cust_obj'] = customer.objects.filter(store_obj=get_store_obj(request.user)).get(id=cust_id)
            return render(request,'upd_cust.html', data)
        elif what == "create_new_cust":
            name = request.POST['cust_name']
            addr = request.POST['cust_addr']
            category  = request.POST['category']
            new_cust = customer(name=name,addr=addr,visit_freq=0,category=category,store_obj=data['store_obj'])
            new_cust.save()
            return redirect('/customers/')
        elif what == "upd_cust":
            if(request.POST['submit_button'] == ' Update '):
                cust_id = request.POST['cust_id']
                cust_obj = customer.objects.filter(store_obj=get_store_obj(request.user)).get(id=cust_id)
                cust_obj.name = request.POST['cust_name']
                cust_obj.addr = request.POST['cust_addr']
                cust_obj.category  = request.POST['category']
                cust_obj.save()
            elif(request.POST['submit_button'] == ' Delete '):
                cust_obj = customer.objects.filter(store_obj=get_store_obj(request.user)).get(id=request.POST['cust_id'])
                cust_obj.delete()
        else:
            return redirect('/customers/')
    else:
        print("Reqest is not a post req.")
    return redirect('/customers/')

@login_required(login_url='/login/')
def prev_bill(request):
    data = {}
    ## ****** Collect Recent Bills ****** ##
    data['recent_bills'] = {}
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
    bill_objs = list(bill_data.objects.all().filter(store=get_store_obj(request.user)).order_by('-date_updated'))[:50]
    for bill_obj in bill_objs:
        d = {}
        d['bill_id'] = bill_obj.id
        d['bill_dict'] = json.loads(bill_obj.b)
        d['date_created'] = bill_obj.date_created.strftime('%d-%b-%Y | %H:%M')
        d['date_updated'] = bill_obj.date_updated.strftime('%d-%b-%Y | %H:%M')
        d['cust'] = bill_obj.cust_obj
        data['recent_bills'][bill_obj.id] = d
    ## ****** Check for any special requested ****** ##
    if request.method=='POST':
        data = {}
        data['issue'] = 'no'
        what = request.POST['what']
        if(what=='get_bill'):
            try:
                bill_id = int(request.POST['bill_id'])			
                bill_obj = bill_data.objects.filter(store=get_store_obj(request.user)).get(id=bill_id)
                data['bill_id'] = bill_id
                data['bill_dict'] = json.loads(bill_obj.b)
                data['date_created'] = bill_obj.date_created.strftime('%d-%b-%Y | %H:%M:%S')
                data['date_updated'] = bill_obj.date_updated.strftime('%d-%b-%Y | %H:%M:%S')
                data['cust'] = str(bill_obj.cust_obj)
            except:
                data['issue'] = 'yes'
                data['message'] = 'Bill not found!!'
        else:
            print("ERROR: Don't even try !!")
        # print("returning data", data)
        return JsonResponse(data)
    else:
        return render(request,'prev_bill.html',data)

# require group -> store manager
@login_required(login_url='/login/')
def add_product(request):
    data = {}
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    store_obj = get_store_obj(request.user)
    data['store_obj'] = store_obj
    data['products'] = list(product.objects.all().filter(store=get_store_obj(request.user)).order_by('name'))[:50]
    if not has_group(request, 'store_manager'):
        return redirect('/home/')
    elif request.method=='POST':
        prd_nm = request.POST['prd_name']
        sp = request.POST['sp']
        wsp = request.POST['wsp']  # wsp means "Wholesale Price"
        unit = request.POST['unit']
        qty = request.POST['qty']
        tags = request.POST['tags']
        new_prd = product(store=store_obj,name=prd_nm,price=sp,WS_price=wsp,unit=unit,tags=tags,available_qty=qty)
        new_prd.save()
        return redirect('/add/')
    else:
        return render(request,'add_product.html',data)

# # require group -> store manager
# @login_required(login_url='/login/')    
# def settings(request):
#     if not has_group(request, 'store_manager'):
#         return redirect('/home/')
#     data = {}
#     data['products'] = list(product.objects.all().order_by('-id'))[:]
#     return render(request,'settings.html',data)

# require group -> store manager
@login_required(login_url='/login/')
def upd(request):
    data = {}
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
    if not has_group(request, 'store_manager'):
        return redirect('/home/')
    elif request.method=='POST':
        what = request.POST['upd_what']
        prd_id = request.POST['upd_id']
        obj = product.objects.filter(store=get_store_obj(request.user)).get(id=prd_id)
        data['product'] = obj
        if(what=='open'):
            return render(request,'upd.html',data)
        elif(what=='update'):
            if(request.POST['submit_button'] == ' Delete '):
                obj.delete()
            elif(request.POST['submit_button'] == ' Update '):
                obj.name = request.POST['prd_name']
                obj.price = request.POST['sp']
                obj.WS_price = request.POST['wsp']
                obj.unit = request.POST['unit']
                obj.available_qty = request.POST['qty']
                obj.tags = request.POST['tags']
                obj.save()
            else:
                pass
            return redirect('/add/')
            
        else:
            print("updating2..")
            return HttpResponse("Hello Mr. OverSmart !!")
    else:
        return HttpResponse("Hello")


# ******************************************************************* #
# ********* Additional Helper Functions ***************************** #
# ******************************************************************* #        
        
def get_store_obj(user_obj):
    emp_obj = store_emp.objects.all().filter(emp_obj=user_obj).first()
    return emp_obj.store_obj if emp_obj is not None else "Store not available"  
        