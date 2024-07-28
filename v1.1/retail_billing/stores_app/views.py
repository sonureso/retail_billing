# stores_app -> view.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.templatetags.extra_filters import has_group
# from products.models import product, bill_data
from stores_app.models import store, store_emp
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import Group


# require group -> store manager
@login_required(login_url='/login/')    
def settings(request):
    # if not has_group(request, 'store_manager'):
    if request.user.is_superuser == False:
        return redirect('/home/')
    data = {}
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
    if request.method=='POST':
        what = request.POST['upd_what']
        if what == 'add_new_store':
            store_nm = request.POST['store_name']
            addr = request.POST['store_address']
            cv = request.POST['CV']
            activeFlag = request.POST['activeFlag']
            manager = request.POST['Store_Manager']
            owner = request.user
            new_store = store(name=store_nm,address=addr,cash_value=cv,activeFlag=activeFlag,creator=owner)
            new_store.save()
            # UPDATE store_manager group to User:
            group, created = Group.objects.get_or_create(name='store_manager')
            user_obj = User.objects.get(username=manager)
            user_obj.groups.add(group)
            user_obj.save()
            # Update store_emp as manager and assign store obj:
            mngr_obj = store_emp.objects.get(emp_obj=user_obj)
            mngr_obj.store_obj = new_store
            mngr_obj.role = 'store_manager'
            mngr_obj.save()

    # GET ALL STORES AND MANAGERS INFO:
    stores = list(store.objects.all().order_by('-id'))[:]
    managers = []
    for store_obj in stores:
        try:
            managers.append(store_emp.objects.all().filter(store_obj=store_obj).filter(role__icontains='store_manager').first())
        except:
            managers.append("not available")
    data['stores_data'] = zip(stores,managers)

    # GET ALL USERS AND STORE EMPs Data:
    all_users = list(User.objects.all())
    all_emp_objs = list(store_emp.objects.all())
    data['all_users'] = []
    for a_user_obj in all_users:
        d = {}
        d['user_obj'] = a_user_obj
        a_emp_obj = [a_emp_obj for a_emp_obj in all_emp_objs if a_emp_obj.emp_obj==a_user_obj]

        d['is_emp'] = True if len(a_emp_obj)>0 else False
        d['emp_obj'] = a_emp_obj[0] if len(a_emp_obj)>0 else None
        data['all_users'].append(d)
    return render(request,'settings.html',data)

# require group -> store manager
@login_required(login_url='/login/')
def upd_settings(request):
    data = {}
    group, created = Group.objects.get_or_create(name='store_manager')
    data['check_what'] = 'Nothing'
    emp_obj = store_emp.objects.all().filter(emp_obj=request.user).first()
    data['store_obj'] = emp_obj.store_obj if emp_obj is not None else "Store not available"
    if request.user.is_superuser == False:
        return redirect('/home/')
    elif request.method=='POST':
        what = request.POST['upd_what']
        # Extract store and manager details if: 
        if(what=='get_store_details' or what=='update_store_details'):
            store_id = request.POST['upd_id']
            obj = store.objects.get(id=store_id)
            manager_obj = store_emp.objects.all().filter(store_obj=obj).filter(role__icontains='store_manager').first()
            data['check_what'] = 'store'
            data['store'] = obj
            data['manager'] = manager_obj
        elif(what=='get_emp_details'):
            raw_user_id = request.POST['upd_id']
            raw_user_obj = User.objects.get(id=raw_user_id)
            try:
                emp_user_obj = store_emp.objects.all().filter(emp_obj=raw_user_obj).first()
            except:
                emp_user_obj = None
            data['check_what'] = 'emp'
            data['raw_user_obj'] = raw_user_obj
            data['emp_user_obj'] = emp_user_obj

        if(what=='get_store_details' or what=='get_emp_details'):
            return render(request,'upd_settings.html',data)
        elif(what=='update_store_details'):
            if(request.POST['submit_button'] == ' Delete '):
                if manager_obj != None:
                    manager_obj.role = 'store_staff'
                    manager_obj.save()
                    manager_obj_user = manager_obj.emp_obj
                    manager_obj_user.groups.remove(group)
                    manager_obj_user.save()
                obj.delete()
            elif(request.POST['submit_button'] == ' Update '):
                obj.name = request.POST['store_name']
                obj.cash_value = request.POST['CV']
                obj.address = request.POST['store_address']
                obj.activeFlag = request.POST['activeFlag']
                st_owner = User.objects.get(username=request.POST['Store_Owner'])
                obj.creator = st_owner
                obj.save()
                # remove prev manager and UPDATE Store_emp as new Manager:
                try:
                    prev_mngr = store_emp.objects.all().filter(store_obj=obj).filter(role__icontains='store_manager').first()
                    new_user_obj = User.objects.all().filter(username=request.POST['Store_Manager']).first()
                    # print("prev manager: ",prev_mngr)
                    # print("new Manager:", new_user_obj)
                    if prev_mngr != new_user_obj:
                        if prev_mngr is not None and new_user_obj is not None:
                            prev_mngr.role = 'store_staff'
                            prev_mngr.save()
                            prev_mngr_user = prev_mngr.emp_obj
                            prev_mngr_user.groups.remove(group)
                            prev_mngr_user.save()
                        if new_user_obj is not None:
                            new_user_obj.groups.add(group)
                            new_user_obj.save()
                            mngr_obj = store_emp.objects.get(emp_obj=new_user_obj)
                            mngr_obj.store_obj = obj
                            mngr_obj.role = 'store_manager'
                            mngr_obj.save()
                            print("Manager updated: ",prev_mngr," -> ",new_user_obj)
                except:
                    # print("prev manager or new manager not found, hence no updates here.")
                    # print("prev Manager: ",)
                    pass
            else:
                pass
        elif(what=='update_emp_details'):
            emp_user_id = request.POST['upd_id']
            emp_user_obj = store_emp.objects.get(id=emp_user_id)
            raw_user_obj = emp_user_obj.emp_obj
            if(request.POST['submit_button'] == ' Update '):
                emp_user_obj.addr = request.POST['user_address']
                emp_user_obj.activeFlag = request.POST['activeFlag']
                emp_user_obj.role = request.POST['role']
                if request.POST['role'] != 'store_manager':
                    raw_user_obj.groups.remove(group)
                else:
                    raw_user_obj.groups.add(group)
                try:
                    store_alloted = store.objects.all().filter(name=request.POST['store']).first()
                except:
                    store_alloted = None
                emp_user_obj.store_obj = store_alloted
                emp_user_obj.save()
                raw_user_obj.save()
            elif(request.POST['submit_button'] == ' Delete '):
                raw_user_obj.groups.clear()
                raw_user_obj.save()
                emp_user_obj.delete()
        elif(what=='create_new_employee'):
            raw_user_id = request.POST['upd_id']
            raw_user_obj = User.objects.get(id=raw_user_id)
            address = request.POST['user_address']
            activeFlag = request.POST['activeFlag']
            role = request.POST['role']
            if request.POST['role'] == 'store_manager':
                raw_user_obj.groups.add(group)
            else:
                pass
            try:
                store_alloted = store.objects.all().filter(name=request.POST['store']).first()
            except:
                store_alloted = None
            emp_user_obj = store_emp(emp_obj=raw_user_obj,addr=address,activeFlag=activeFlag,role=role,store_obj=store_alloted)
            emp_user_obj.save()
        else:
            print("updating2..")
            return HttpResponse("Hello Mr. OverSmart !!")
        return redirect('/settings/')
    else:
        return HttpResponse("Hello")

# require group -> store manager
@login_required(login_url='/login/')
def get_user(request):
    if 'term' in request.GET:
            user_names = []
            qs = list(store_emp.objects.filter(emp_obj__username__icontains=request.GET.get('term')))  # icontains, istartswith can also be used.
            for item in qs:
                user_names.append(item.emp_obj.username)
            return JsonResponse(user_names, safe=False)

# require group -> store manager
@login_required(login_url='/login/')
def get_user_for_manager(request):
    if 'term' in request.GET:
            user_names = []
            qs = list(store_emp.objects.filter(emp_obj__username__icontains=request.GET.get('term')).filter(role__icontains='staff'))  # icontains, istartswith can also be used.
            for item in qs:
                user_names.append(item.emp_obj.username)
            return JsonResponse(user_names, safe=False)

# require group -> store manager
@login_required(login_url='/login/')
def get_store(request):
    if 'term' in request.GET:
            store_names = []
            qs = list(store.objects.filter(name__icontains=request.GET.get('term')))  # icontains, istartswith can also be used.
            for item in qs:
                store_names.append(item.name)
            return JsonResponse(store_names, safe=False)

