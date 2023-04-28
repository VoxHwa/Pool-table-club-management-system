from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import math
# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    card_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name
    
    def deposit(self, amount):
        self.balance += amount
        self.save()

    def consume(self, amount):
        if self.balance < amount:
            raise ValueError('Insufficient balance')
        else:
            self.balance -= amount
            self.save()        
    def delete(self, *args, **kwargs):
        # Delete all related recharge and usage records
        Recharge.objects.filter(member=self).delete()
        Usage.objects.filter(member=self).delete()
        super().delete(*args, **kwargs)


class Recharge(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    recharge_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member.name} 于 {self.recharge_date} 充值了 {self.amount} 元'


class Usage(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    usage_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.member.name} 使用于 {self.usage_date}，使用时间 {self.start_time} 至 {self.end_time}, 费用为 {self.fee}'
    @classmethod
    def create(cls, member, start_time):
        usage = cls(member=member, start_time=start_time)
        usage.save()
        return usage

    def stop(self, member):
        #计算费用直接调table的费用，如果连接了关系

        self.save()

    @classmethod
    def get_recent(cls, count=10):
        return cls.objects.order_by('-usage_date')[:count]
    
class Transaction(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=8, decimal_places=2)



class PoolTable(models.Model):
    name = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    current_member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    paused_time = models.DateTimeField(null=True, blank=True)
    usage_time = models.DurationField(default=timezone.timedelta())
    total_paused_time = models.DurationField(default=timezone.timedelta())
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,validators=[MinValueValidator(0)])
    def start(self):
        self.is_available = False
        self.start_time = timezone.now()
        self.save()

    def pause(self):
        if self.start_time is not None and self.paused_time is None:
            self.paused_time = timezone.now()
            self.save()

    def resume(self):
        if self.start_time is not None and self.paused_time is not None:
            paused_delta = timezone.now() - self.paused_time
            self.total_paused_time += paused_delta
            self.paused_time = None
            self.save()



    def stop(self):
        if self.start_time is not None and self.end_time is None:
            self.is_available = True
            self.end_time = timezone.now()
            self.save()


    def reset(self):
        self.is_available = True
        self.current_member = None
        self.start_time = None
        self.end_time = None
        self.paused_time = None
        self.total_paused_time = timezone.timedelta()
        self.save()

    def get_elapsed_time(self):
        if self.paused_time is not None:
            return self.paused_time - self.start_time - self.total_paused_time
        if self.start_time is None:
            return timezone.timedelta()
        elif self.end_time is None:
            return timezone.now() - self.start_time - self.total_paused_time
        else:
            return self.end_time - self.start_time - self.total_paused_time
    
    def get_usage_time(self):
        if self.start_time is None or self.end_time is None:
            return timezone.timedelta()
        usage_time = self.end_time - self.start_time - self.total_paused_time
        return usage_time
    def get_cost(self):
        total_cost=0
        if self.start_time is None or self.end_time is None:
            usage_time = self.get_elapsed_time()
        else:
            usage_time = self.get_usage_time()
        yu=usage_time.total_seconds() // 1800
        remainder=usage_time.total_seconds() % 1800
        if yu%2==0:
            if remainder==0:
                total_cost=25*yu//2
            else:
                total_cost=25*yu//2 + 13
        else:
            if remainder==0:
                total_cost=25*yu + 13
            else:
                total_cost=25*(yu+1)//2
        self.total_cost=total_cost                
        self.save()
        return total_cost