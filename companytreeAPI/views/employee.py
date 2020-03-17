"""View module for handling employee requests"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from companytreeAPI.models import Employee
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for products
    Arguments:
        serializers.HyperlinkedModelSerializer
    """
    class Meta:
        model = Employee
        url = serializers.HyperlinkedIdentityField(
            view_name='employee',
            lookup_field='id'
        )
        fields = ('id', 'department_id', 'supervisor_id', 'position', 'location', 'bio', 'image_url', 'tasks', 'phone', 'slack', 'company_id', 'is_admin')

class Employees(ViewSet):

    """Company Employees"""

    # def create(self, request):
    #     """Handle POST operations
    #     Returns:
    #         Response -- JSON serialized Products instance
    #     """
    #     newEmployee = Employee()
    #     newEmployee = request.data["name"]
    #     newEmployee.department_id = request.auth.user.customer.id
    #     newEmployee.price = request.data["price"]
    #     newEmployee.description = request.data["description"]
    #     newEmployee.quantity = request.data["quantity"]
    #     newEmployee.location = request.data["location"]
    #     newEmployee.image_path = request.data["image_path"]
    #     newEmployee.product_type_id = request.data["product_type_id"]
    #     newEmployee.save()

    #     serializer = ProductSerializer(newproduct, context={'request': request})

    #     return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single employee
        Returns:
            Response -- JSON serialized employee instance
        """
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests for all employees
        Returns:
            Response -- JSON serialized product instance
        """
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category', None)
        user = self.request.query_params.get('self')


        # filter for the 'home' view
        if limit:
            employees = Employee.objects.order_by('-created_at')[0:int(limit)]
        elif search:
            employees = Employee.objects.filter(name__contains=search)
        # filter for the 'myEmployees' view
        else:
            employees = Employee.objects.filter(company_id=request.auth.user.employee.company_id)
        # else:
        #     employees = Employee.objects.all()

        serializer = EmployeeSerializer(
                    employees,
                    many=True,
                    context={'request': request}
                )


        return Response(serializer.data)