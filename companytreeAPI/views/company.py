"""View module for handling company requests"""
import json
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from companytreeAPI.models import Company
from companytreeAPI.models import Employee
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for companies
    Arguments:
        serializers.HyperlinkedModelSerializer
    """
    
    class Meta:
        model = Company
        url = serializers.HyperlinkedIdentityField(
            view_name='company',
            lookup_field='id'
        )
        fields = ('id', 'name',)

class Companies(ViewSet):

    """Companies"""

    @csrf_exempt
    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Company instance
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            new_company = Company()
            new_company.name = request.data["name"]
            new_company.save()

            serializer = CompanySerializer(new_company, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single company
        Returns:
            Response -- JSON serialized company instance
        """
        try:
            company = Company.objects.get(pk=request.auth.user.employee.company_id)
            serializer = CompanySerializer(company, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @csrf_exempt
    def list(self, request):
        """Handle GET requests for all employees
        Returns:
            Response -- JSON serialized employee instance
        """
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category', None)
        user = self.request.query_params.get('self')


        # filter for the 'search companies' view
        if limit:
            companies = Company.objects.order_by('name')[0:int(limit)]
        elif search:
            companies = Company.objects.filter(name__contains=search)
        # filter for the 'myCompanies' view
        else:
            companies = Company.objects.all()

        serializer = CompanySerializer(
            companies,
            many=True,
            context={'request': request}
            )
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Handle PUT requests for a company
        Returns:
            Response -- Empty body with 204 status code
        """
        #First, find out if current user has admin access
        current_user = Employee.objects.get(pk=request.auth.user.employee.id)
        if current_user.is_admin == True:
            company_to_update = Company.objects.get(pk=request.auth.user.employee.company_id)
            company_to_update.name = request.data["name"]
            company_to_update.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single company
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            #Find out if current user has admin access
            current_user = Employee.objects.get(pk=request.auth.user.employee.id)
            if current_user.is_admin == True:
                company = Company.objects.get(pk=pk)
                company.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Company.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)