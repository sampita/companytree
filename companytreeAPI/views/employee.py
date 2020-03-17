"""View module for handling employee requests"""
import json
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from companytreeAPI.models import Employee
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
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
        fields = ('id', 'user_id', 'department_id', 'supervisor_id', 'position', 'location', 'bio', 'image_url', 'tasks', 'phone', 'slack', 'company_id', 'is_admin',)
        depth = 2

class Employees(ViewSet):

    """Company Employees"""

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Products instance
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            # Load the JSON string of the request body into a dict
            req_body = json.loads(request.body.decode())
            
            new_user = User.objects.create_user(
            username=req_body['username'],
            email=req_body['email'],
            password=req_body['password'],
            first_name=req_body['first_name'],
            last_name=req_body['last_name']
            )
            
            new_employee = Employee()
            new_employee.user = new_user
            new_employee.department_id = request.data["department_id"]
            new_employee.supervisor_id = request.data["supervisor_id"]
            new_employee.position = request.data["position"]
            new_employee.location = request.data["location"]
            new_employee.bio = request.data["bio"]
            new_employee.image_url = request.data["image_url"]
            new_employee.tasks = request.data["tasks"]
            new_employee.phone = request.data["phone"]
            new_employee.slack = request.data["slack"]
            new_employee.company_id = request.data["company_id"]
            new_employee.is_admin = request.data["is_admin"]
            new_employee.save()

            serializer = EmployeeSerializer(new_employee, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single employee
        Returns:
            Response -- JSON serialized employee instance
        """
        try:
            employee = Employee.objects.get(pk=pk, company_id=request.auth.user.employee.company_id)
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

        serializer = EmployeeSerializer(
            employees,
            many=True,
            context={'request': request}
            )
        return Response(serializer.data)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single park area
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            #Find out if current user has admin access
            current_user = Employee.objects.get(pk=request.auth.user.employee.id)
            if current_user.is_admin == True:
                employee = Employee.objects.get(pk=pk)
                employee.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Employee.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)