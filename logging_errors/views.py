import json
from uuid import uuid4
import datetime as dt

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import Application, Error


class ApplicationListView(ListView):
    queryset = Application.objects.all()
    template_name = 'applications.html'

    @staticmethod
    def post(request):
        new_application = request.POST.get('addnewapp')
        if len(str(new_application)) > 0:
            token = uuid4()
            application = Application.objects.create(name=new_application, token=token)
            application.save()
            return redirect('app_list')
        else:
            return redirect('app_list')


class ApplicationDetailView(DetailView):
    model = Application
    template_name = 'application_detail.html'

    def get(self, request, *args, **kwargs):
        application = Application.objects.get(id=self.kwargs['id'])
        app_name = application.name
        app_token = application.token
        errors_set = Error.objects.filter(app_id=self.kwargs['id']).values_list('type', flat=True).distinct()
        type_error = request.GET.get('type')
        if type_error:
            error_list = Error.objects.filter(app_id=self.kwargs['id']).filter(type=type_error).order_by('-date')
            first_error_date = Error.objects.filter(type=type_error).order_by('date').first()
            last_error_date = Error.objects.filter(type=type_error).order_by('date').last()
            first_date = first_error_date.date.date()
            last_date = last_error_date.date.date()
            if first_date == last_date:
                time = list()
                count_errors = list()
                for hour in range(25):
                    time.append('%s' % hour)
                    count_hour_errors = 0
                    for error in error_list:
                        if error.date.hour == hour:
                            count_hour_errors += 1
                    count_errors.append(count_hour_errors)
                time.reverse()
                count_errors.reverse()
            else:
                delta_dates = last_date - first_date
                total_days = delta_dates.days + 1
                time = list()
                count_errors = list()
                for day_number in range(total_days):
                    current_date = (first_date + dt.timedelta(days=day_number))
                    time.append('%s' % current_date)
                    count_day_errors = 0
                    for error in error_list:
                        if error.date.date() == current_date:
                            count_day_errors += 1
                    count_errors.append(count_day_errors)
            time.reverse()
            count_errors.reverse()
        else:
            error_list, time, count_errors = None, None, None
        return render(request, 'application_detail.html', {'errors_set': errors_set,
                                                           'errors_list': error_list,
                                                           'error_type': type_error,
                                                           'app_name': app_name,
                                                           'app_token': app_token,
                                                           'date': json.dumps(time),
                                                           'count_errors': json.dumps(count_errors),
                                                           })
