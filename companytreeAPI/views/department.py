"""View module for handling company requests"""
import json
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from companytreeAPI.models import Department
from companytreeAPI.models import Employee
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for departments
    Arguments:
        serializers.HyperlinkedModelSerializer
    """
    
    class Meta:
        model = Department
        url = serializers.HyperlinkedIdentityField(
            view_name='department',
            lookup_field='id'
        )
        fields = ('id', 'name', 'colorHex',)

class Departments(ViewSet):

    """Departments"""

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Department instance
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            new_department = Department()
            new_department.name = request.data["name"]
            new_department.colorHex = request.data["colorHex"]
            new_department.save()

            serializer = DepartmentSerializer(new_department, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single department
        Returns:
            Response -- JSON serialized department instance
        """
        try:
            department = Department.objects.get(pk=pk)
            serializer = DepartmentSerializer(department, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests for all departments
        Returns:
            Response -- JSON serialized department instance
        """
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category', None)
        user = self.request.query_params.get('self')


        # filter for the 'search departments' view
        if limit:
            departments = Department.objects.order_by('name')[0:int(limit)]
        elif search:
            departments = Department.objects.filter(name__contains=search)
        # filter for the 'myCompanies' view
        else:
            departments = Department.objects.all()

        serializer = DepartmentSerializer(
            departments,
            many=True,
            context={'request': request}
            )
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Handle PUT requests for a department
        Returns:
            Response -- Empty body with 204 status code
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            department_to_update = Department.objects.get(pk=pk)
            department_to_update.name = request.data["name"]
            department_to_update.colorHex = request.data["colorHex"]
            department_to_update.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single department
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            #Find out if current user has admin access
            current_user = Employee.objects.get(pk=request.auth.user.employee.id)
            if current_user.is_admin == True:
                department = Department.objects.get(pk=pk)
                department.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Department.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)