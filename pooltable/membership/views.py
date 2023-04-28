# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Member, Recharge, Usage
from .forms import MemberForm
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import MemberForm, DeleteMemberForm
from membership.models import Member, Transaction
import json
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PoolTable
from django.utils import timezone


from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from membership.models import PoolTable, Member

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import PoolTable, Member
from django.http import HttpResponseRedirect
from django.db.models import Q
from .models import Member, Consumption

def member_detail(request, member_id):
    member = Member.objects.get(id=member_id)
    usage_transactions = Consumption.objects.filter(member=member, type=Consumption.CONSUME).order_by('-timestamp')
    recharge_transactions = Consumption.objects.filter(member=member, type=Consumption.RECHARGE).order_by('-timestamp')
    context = {
        'member': member,
        'usage_transactions': usage_transactions,
        'recharge_transactions': recharge_transactions,
    }
    return render(request, 'membership/member_detail.html', context)
def search_member(request):
    search_query = request.GET.get('search', '')
    members = Member.objects.filter(Q(name__icontains=search_query) | Q(phone__icontains=search_query))
    return render(request, 'membership/membership_list.html', {'members': members})
@csrf_exempt
def deposit(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        amount = Decimal(request.POST.get('amount'))
        if amount<=0:
            return JsonResponse({'success': False, 'message': 'Amount must be greater than zero'})
        member = get_object_or_404(Member, id=member_id)
        member.balance += amount
        member.save()
        consumption = Consumption.objects.create(
            member=member,
            amount=Decimal(amount),
            type=Consumption.RECHARGE,
        )
        return JsonResponse({'success': True})
@csrf_exempt
def consume(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        amount = Decimal(request.POST.get('amount'))
        member = get_object_or_404(Member, id=member_id)
        if amount<=0:
            return JsonResponse({'success': False, 'message': 'Amount must be greater than zero'})
        if member.balance < amount:
            return JsonResponse({'success': False, 'message': 'Insufficient balance'})
        else:
            member.balance -= amount
            member.save()
            consumption = Consumption.objects.create(
                member=member,
                amount=Decimal(amount),
                type=Consumption.CONSUME,
            )
            return JsonResponse({'success': True})
def get_table_status(request):
    pool_tables = PoolTable.objects.all()
    context = {'pool_tables': pool_tables}
    return render(request, 'membership/table_status_partial.html', context)

def pool_table_view(request):
    # 获取所有的桌子和会员
    pool_tables = PoolTable.objects.all()
    members = Member.objects.all()

    # 初始化表格和会员变量
    table = None
    member = None

    # 检查表格选择表单是否提交
    if request.method == 'POST' and 'submit' in request.POST and 'table_id' in request.POST:
        table_id = request.POST.get('table_id')
        table = PoolTable.objects.get(id=table_id)

    # 检查会员选择表单是否提交
    if request.method == 'POST' and 'submit' in request.POST and 'member_id' in request.POST:
        member_id = request.POST.get('member_id')
        member = Member.objects.get(id=member_id)

    # 过滤使用中的桌子和已选的会员
    if table:
        pool_tables = pool_tables.filter(id=table.id)
    if member:
    # 过滤当前会员正在使用的桌子，或者没有任何会员使用的桌子
        pool_tables = pool_tables.filter(Q(current_member=member) | Q(current_member__isnull=True))


    # 计算消费金额
    money_to_pay = None
    if table and member:
        money_to_pay = table.get_usage_time() * member.rate_per_hour

    # 传递桌子、会员和消费金额给模板
    context = {
        'pool_tables': pool_tables,
        'members': members,
        'table': table,
        'member': member,
        'money_to_pay': money_to_pay,
    }

    return render(request, 'membership/pool_tables.html', context)

def timer_view(request):
    if request.method == 'POST':
        table_id = request.POST['table_id']
        pool_table = PoolTable.objects.get(id=table_id)
        if 'start' in request.POST:
            pool_table.start()
        elif 'pause' in request.POST:
            pool_table.pause()
        elif 'resume' in request.POST:
            pool_table.resume()
        elif 'stop' in request.POST:
            pool_table.stop()

        elif 'reset' in request.POST:
            pool_table.reset()
        return HttpResponseRedirect(request.path_info)

    pool_tables = PoolTable.objects.all()
    return render(request, 'membership/timer.html', {'pool_tables': pool_tables})



@csrf_exempt
def pool_table_start(request):
    if request.method == 'POST':
        pool_table_id = request.POST.get('pool_table_id')
        try:
            pool_table = PoolTable.objects.get(id=pool_table_id)
        except PoolTable.DoesNotExist:
            return HttpResponseBadRequest('Invalid pool table ID')

        if not pool_table.is_available:
            return HttpResponseBadRequest('Pool table is already in use')

        pool_table.start_timer()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponseBadRequest('Invalid request method')


@csrf_exempt
def pool_table_pause(request):
    if request.method == 'POST':
        pool_table_id = request.POST.get('pool_table_id')
        try:
            pool_table = PoolTable.objects.get(id=pool_table_id)
        except PoolTable.DoesNotExist:
            return HttpResponseBadRequest('Invalid pool table ID')

        if not pool_table.is_timer_running:
            return HttpResponseBadRequest('Pool table timer is not running')

        pool_table.pause_timer()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponseBadRequest('Invalid request method')


@csrf_exempt
def pool_table_resume(request):
    if request.method == 'POST':
        pool_table_id = request.POST.get('pool_table_id')
        try:
            pool_table = PoolTable.objects.get(id=pool_table_id)
        except PoolTable.DoesNotExist:
            return HttpResponseBadRequest('Invalid pool table ID')

        if not pool_table.is_timer_paused:
            return HttpResponseBadRequest('Pool table timer is not paused')

        pool_table.resume_timer()
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponseBadRequest('Invalid request method')


@csrf_exempt
def pool_table_stop(request):
    if request.method == 'POST':
        pool_table_id = request.POST.get('pool_table_id')
        try:
            pool_table = PoolTable.objects.get(id=pool_table_id)
        except PoolTable.DoesNotExist:
            return HttpResponseBadRequest('Invalid pool table ID')

        if not pool_table.is_timer_running:
            return HttpResponseBadRequest('Pool table timer is not running')

        pool_table.stop_timer()
        return JsonResponse({'status': 'success', 'usage_time': pool_table.get_usage_time()})
    else:
        return HttpResponseBadRequest('Invalid request method')

def member_detail(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    #
    member = Member.objects.get(id=member_id)
    usage_transactions = Consumption.objects.filter(member=member, type=Consumption.CONSUME).order_by('-timestamp')
    recharge_transactions = Consumption.objects.filter(member=member, type=Consumption.RECHARGE).order_by('-timestamp')
    context = {
        'member': member,
        'usage_transactions': usage_transactions,
        'recharge_transactions': recharge_transactions,
    }
    return render(request, 'membership/detail.html', context)
    #
    transactions = Transaction.objects.filter(member=member)
    usage_transactions = []
    recharge_transactions = []
    for transaction in transactions:
        if transaction.amount < 0:
            usage_transactions.append(transaction)
        else:
            recharge_transactions.append(transaction)
    return render(request, 'membership/detail.html', {'member': member, 'usage_transactions': usage_transactions, 'recharge_transactions': recharge_transactions})

def member_list(request):
    members = Member.objects.all()
    return render(request, 'membership/index.html', {'members': members})

@login_required
def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)

    if request.method == 'POST':
        form = DeleteMemberForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(username=request.user.username, password=password)

            if user is not None:
                confirm_password = form.cleaned_data.get('confirm_password')

                if password == confirm_password:
                    member.delete()
                    return HttpResponseRedirect('/membership/')
                else:
                    form.add_error('confirm_password', '两次输入的密码不匹配')
    else:
        form = DeleteMemberForm()
        
    return render(request, 'membership/delete_member.html', {'member': member, 'form': form})

@login_required(login_url='/admin/login/')
def index(request):
    members = Member.objects.all()
    return render(request, 'membership/index.html', {'members': members})


def detail(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    recharges = Recharge.objects.filter(member=member).order_by('-recharge_date')
    usages = Usage.objects.filter(member=member).order_by('-usage_date')
    return render(request, 'membership/detail.html', {'member': member, 'recharges': recharges, 'usages': usages})


@csrf_exempt
def recharge(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    amount = float(request.POST.get('amount', 0))
    member.balance += amount
    member.save()
    Recharge.objects.create(member=member, amount=amount)
    return redirect('membership:detail', member_id)


@csrf_exempt
def start_usage(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    start_time = datetime.datetime.now()
    usage = Usage.objects.create(member=member, start_time=start_time)
    return redirect('membership:usage', usage.id)


def usage(request, usage_id):
    usage = get_object_or_404(Usage, pk=usage_id)
    if usage.end_time:
        return redirect('membership:detail', usage.member.id)
    else:
        return render(request, 'membership/usage.html', {'usage': usage})


def end_usage(request, usage_id):
    usage = get_object_or_404(Usage, pk=usage_id)
    if not usage.end_time:
        usage.end_time = datetime.datetime.now()
        delta = usage.end_time - usage.start_time
        hours = delta.total_seconds() / 3600
        usage.fee = hours * 20 # 假设每小时收费20元
        usage.member.balance -= usage.fee
        usage.member.save()
        usage.save()
    return redirect('membership:detail', usage.member.id)


'''def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.delete()
    return redirect('membership:index')
    '''
def edit_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('membership:index')
    else:
        form = MemberForm(instance=member)
    context = {
        'form': form,
        'member_id': member_id,
    }
    return render(request, 'membership/edit_member.html', context)

def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('membership:index')
    else:
        form = MemberForm()
    return render(request, 'membership/add_member.html', {'form': form})

