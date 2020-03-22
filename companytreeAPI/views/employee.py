"""View module for handling employee requests"""
import json
import sqlite3
from .connection import Connection
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from companytreeAPI.models import Employee
from companytreeAPI.serializers.user import UserSerializer
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for employees
    Arguments:
        serializers.HyperlinkedModelSerializer
    """
    
    user = UserSerializer(many=False)
    
    class Meta:
        model = Employee
        url = serializers.HyperlinkedIdentityField(
            view_name='employee',
            lookup_field='id'
        )
        fields = ('id', 'user', 'department_id', 'supervisor_id', 'position', 'location', 'bio', 'image_url', 'tasks', 'phone', 'slack', 'company_id', 'is_admin',)
        # depth = 2

class Employees(ViewSet):

    """Company Employees"""

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Employees instance
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
            new_employee.company_id = request.auth.user.employee.company_id
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
        if request.method == 'GET':
            with sqlite3.connect(Connection.db_path) as conn:
                conn.row_factory = sqlite3.Row
                db_cursor = conn.cursor()

                db_cursor.execute(f"SELECT * FROM companytreeAPI_employee as etable JOIN companytreeAPI_department as dtable ON etable.department_id=dtable.id JOIN auth_user as atable ON atable.id=etable.user_id AND company_id={request.auth.user.employee.company_id};")
                
                all_employees = []
                dataset = db_cursor.fetchall()
                
                for row in dataset:
                    employee = Employee()
                    employee = {
                        "id": row['id'],
                        "position": row['position'],
                        "location": row['location'],
                        "bio": row['bio'],
                         "image_url": row['image_url'],
                        "phone": row['phone'],
                        "is_admin": row['is_admin'],
                        "department_id": row['department_id'],
                        "user_id": row['user_id'],
                        "slack": row['slack'],
                        "company_id": row['company_id'],
                        "tasks": row['tasks'],
                        "supervisor_id": row['supervisor_id'],
                        "name": row['name'],
                        "colorHex": row['colorHex'],
                        "username": row['username'],
                        "first_name": row['first_name'],
                        "last_name": row['last_name'],
                        "email": row['email'],
                    }
                    all_employees.append(employee)

        context = {
            'all_employees': all_employees
        }
        res = json.dumps(all_employees)
        return Response(res, status=status.HTTP_200_OK)
        
        
    # def list(self, request):
    #     """Handle GET requests for all employees
    #     Returns:
    #         Response -- JSON serialized employee instance
    #     """


    #     # filter for the 'home' view
    #     if limit:
    #         employees = Employee.objects.order_by('-created_at')[0:int(limit)]
    #     elif search:
    #         employees = Employee.objects.filter(name__contains=search)
    #     # filter for the 'myEmployees' view
    #     else:
    #         employees = Employee.objects.filter(company_id=request.auth.user.employee.company_id)

    #     serializer = EmployeeSerializer(
    #         employees,
    #         many=True,
    #         context={'request': request}
    #         )
    #     return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Handle PUT requests for an employee
        Returns:
            Response -- Empty body with 204 status code
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            employee_to_update = Employee.objects.get(pk=pk)
            employee_to_update.department_id = request.data["department_id"]
            employee_to_update.supervisor_id = request.data["supervisor_id"]
            employee_to_update.position = request.data["position"]
            employee_to_update.location = request.data["location"]
            employee_to_update.bio = request.data["bio"]
            employee_to_update.image_url = request.data["image_url"]
            employee_to_update.tasks = request.data["tasks"]
            employee_to_update.phone = request.data["phone"]
            employee_to_update.slack = request.data["slack"]
            employee_to_update.company_id = request.auth.user.employee.company.id
            employee_to_update.is_admin = request.data["is_admin"]
            employee_to_update.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single employee
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